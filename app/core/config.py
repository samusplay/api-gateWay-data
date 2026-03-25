import os

from dotenv import load_dotenv

#cargamos variables
load_dotenv()

class Settings:
    #trae urls
    MS_INGESTION_URL: str = os.getenv("MS_INGESTION_URL", "http://localhost:8001")

#exportamos globla
settings=Settings()