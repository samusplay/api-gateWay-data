import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__=="__main__":
    #traemos variables
    port=int(os.getenv("PORT_GATEWAY",8000))
    print(f"Iniciando Api GateWay en el puerto{port}...")
    uvicorn.run("app.main:app",host="0.0.0.0",port=port,reload=True)