from typing import List, Dict, Any
from elasticsearch import Elasticsearch, helpers
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer
from..config import settings
from..schemas import MOCKAROO_SCHEMA
import requests

class SearchService:
    def __init__(self):
        self.es_client = settings.elasticsearch_client
        self.model = SentenceTransformer('all-mpnet-base-v2')
        self.model_embedding_dims = self.model.get_sentence_embedding_dimension()

    async def load_data_from_mockaroo(self):
        """
        Fetches data from Mockaroo, generates embeddings, and indexes it into Elasticsearch.
        """
        try:
            # Fetch data from Mockaroo using the imported schema
            mockaroo_url = "https://api.mockaroo.com/api/generate.json"
            params = {
                "count": 1000,  # Adjust the number of records as needed
                "key": settings.MOCKAROO_API_KEY
            }
            response = requests.post(mockaroo_url, params=params, json=MOCKAROO_SCHEMA["fields"])
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()

            # Delete indices if they exist
            if self.es_client.indices.exists(index="magazines"):
                # Check if the index has documents
                if self.es_client.count(index="magazines")['count'] > 0:
                    # Delete all documents in the index
                    self.es_client.delete_by_query(index="magazines", body={"query": {"match_all": {}}})
                self.es_client.indices.delete(index="magazines")
            if self.es_client.indices.exists(index="magazine_contents"):
                # Check if the index has documents
                if self.es_client.count(index="magazine_contents")['count'] > 0:
                    # Delete all documents in the index
                    self.es_client.delete_by_query(index="magazine_contents", body={"query": {"match_all": {}}})
                self.es_client.indices.delete(index="magazine_contents")

            # Create Elasticsearch indices
            self.es_client.indices.create(index="magazines", body={
                "mappings": {
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {"type": "text", "analyzer": "standard"},
                        "author": {"type": "text", "analyzer": "standard"},
                        "publication_date": {"type": "date"},
                        "category": {"type": "keyword"}
                    }
                }
            })
            self.es_client.indices.create(index="magazine_contents", body={
                "mappings": {
                    "properties": {
                        "id": {"type": "integer"},
                        "magazine_id": {"type": "integer"},
                        "content": {"type": "text"},
                        "vector_representation": {
                            "type": "dense_vector",
                            "dims": self.model_embedding_dims
                        }
                    }
                }
            })

            # Bulk insert data into Elasticsearch
            magazine_actions = []
            magazine_content_actions = []
            for item in data:
                # Generate vector embedding for the content
                embedding = self.model.encode(item['content']).tolist()

                # Action for indexing magazine information
                magazine_actions.append({
                    "_index": "magazines",
                    "_id": item['id'],
                    "_source": {
                        "id": item['id'],
                        "title": item['title'],
                        "author": item['author'],
                        "publication_date": item['publication_date'],
                        "category": item['category']
                    }
                })

                # Action for indexing magazine content with embedding
                magazine_content_actions.append({
                    "_index": "magazine_contents",
                    "_id": item['content_id'],
                    "_source": {
                        "id": item['content_id'],
                        "magazine_id": item['id'],
                        "content": item['content'],
                        "vector_representation": embedding
                    }
                })

            # Bulk insert actions
            helpers.bulk(self.es_client, magazine_actions, chunk_size=10, max_chunk_bytes=10485760)
            helpers.bulk(self.es_client, magazine_content_actions, chunk_size=10, max_chunk_bytes=10485760)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading data from Mockaroo: {e}")

    async def search_data(self, query: str, search_type: str = "hybrid"):
        """
        Performs a search based on the specified search_type.

        Args:
            query: The search query.
            search_type: The type of search to perform ('fulltext', 'vector', or 'hybrid').

        Returns:
            A list of matching magazines with their fields and content.
        """
        query_embedding = self.model.encode(query).tolist()
        query_fulltext = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "author", "category"]
                }
            }
        }
        query_vector_search = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vector_representation') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            }
        }
        retriever_hybrid_search = {
            "rrf": {
                "retrievers": [
                    {
                        "standard" : query_fulltext
                    },
                    {
                        "standard" : query_vector_search
                    }
                ]
            }
        }
        
        try:
            if search_type == "fulltext":
                # Full-text search
                results = self.es_client.search(
                    index="magazines",
                    body=query_fulltext
                )
            elif search_type == "vector":
                # Vector search
                results = self.es_client.search(
                    index="magazine_contents",
                    body=query_vector_search
                )
            elif search_type == "hybrid":
                # Hybrid search using RRF
                results = self.es_client.search(
                    index="magazines,magazine_contents",
                    retriever=retriever_hybrid_search
                )
            else:
                raise HTTPException(status_code=400, detail="Invalid search_type")

            # Extract magazine IDs from search results
            magazine_ids = []
            for result in results['hits']['hits']:
                if search_type == "vector":
                    magazine_ids.append(result['_source']['magazine_id'])
                elif search_type == "fulltext":  # Corrected condition
                    magazine_ids.append(result['_id'])
                else:  # Hybrid search
                    # For hybrid search, you might need to handle both cases
                    # depending on which retriever produced the result
                    if '_source' in result and 'magazine_id' in result['_source']:
                        magazine_ids.append(result['_source']['magazine_id'])
                    else:
                        magazine_ids.append(result['_id'])
            # Combine magazine and content data
            magazines = []
            if magazine_ids:
                magazine_data = self.es_client.mget(index="magazines", ids=magazine_ids)  # Fetch magazines in bulk

                # Search for content in bulk
                content_results = self.es_client.search(
                    index="magazine_contents",
                    body={
                        "query": {
                            "terms": {
                                "magazine_id": magazine_ids
                            }
                        }
                    }
                )['hits']['hits']
                
                # Create a dictionary mapping magazine_id to content
                content_map = {}
                if content_results:  
                    content_map = {result['_source']['magazine_id']: result['_source']['content'] for result in content_results}
                
                for doc in magazine_data['docs']:
                    magazine = doc['_source']
                    magazine_id = magazine['id']
                    if magazine_id in content_map:
                        magazine['content'] = content_map[magazine_id]
                        magazines.append(magazine)

            return magazines

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error searching data: {e}")