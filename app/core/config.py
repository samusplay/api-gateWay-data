import os

from dotenv import load_dotenv

#cargamos variables
load_dotenv()

class Settings:
    #trae urls
    MS_INGESTION_URL: str = os.getenv("MS_INGESTION_URL", "http://localhost:8001")

    #Url de Microservicio
    MS_TRANSFORM_URL:str = os.getenv("MS_TRANSFORM_URL", "http://localhost:8002")
    
    # Trae URL del Frontend (CORS)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

#exportamos globlal
settings=Settings()