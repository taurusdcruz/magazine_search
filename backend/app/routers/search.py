from typing import List
from fastapi import APIRouter, Depends, HTTPException
from..services.search_service import SearchService
from..models import Magazine, MagazineContent, MagazineWithContent

router = APIRouter()

@router.post("/load", response_model=dict, status_code=200, description="Loads magazine and magazine content data into Elasticsearch, generating vector embeddings for the content.")
async def load_data(search_service: SearchService = Depends(SearchService)):
    """
    Loads data from Mockaroo and indexes it into Elasticsearch.
    """
    try:
        await search_service.load_data_from_mockaroo()
        return {"message": "Data loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {e}")

@router.get("/search", response_model=List[MagazineWithContent], status_code=200, description="Performs a search based on the specified search_type.")
async def search_data(
    query: str, search_type: str = "hybrid", search_service: SearchService = Depends(SearchService)
):
    """
    Performs a search based on the specified search_type.
    """
    try:
        results = await search_service.search_data(query, search_type)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching data: {e}")