import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv, find_dotenv

# Find and print the path of the.env file being loaded
env_path = find_dotenv(raise_error_if_not_found=True)
print(f"Loading environment variables from: {env_path}")

# Load environment variables
load_dotenv(dotenv_path='.env.local',override=True)

class Settings:
    ELASTICSEARCH_CLOUD_ID = os.getenv("ELASTICSEARCH_CLOUD_ID")
    ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
    MOCKAROO_API_KEY = os.getenv("MOCKAROO_API_KEY")

    @property
    def elasticsearch_client(self):
        try:
            return Elasticsearch(
                cloud_id=self.ELASTICSEARCH_CLOUD_ID,
                api_key=self.ELASTICSEARCH_API_KEY
            )
        except Exception as e:
            print(f"==={self.ELASTICSEARCH_CLOUD_ID}")
            raise e
settings = Settings()