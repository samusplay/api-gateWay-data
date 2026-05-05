import os

from dotenv import load_dotenv

#cargamos variables
load_dotenv()

class Settings:
    #trae urls
    MS_INGESTION_URL: str = os.getenv("MS_INGESTION_URL", "http://localhost:8001")

    #Url de Microservicio
    MS_TRANSFORM_URL:str = os.getenv("MS_TRANSFORM_URL", "http://localhost:8002")
    
    MS_ANALYTICS_URL: str = os.getenv("MS_ANALYTICS_URL", "http://localhost:8005")
    
    MS_CONFIGURATION_URL: str = os.getenv("MS_CONFIGURATION_URL", "http://localhost:8004")

    MS_ML_URL: str = os.getenv("MS_ML_URL", "http://localhost:8006")
    
    # Trae URL del Frontend (CORS)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

#exportamos globlal
settings=Settings()