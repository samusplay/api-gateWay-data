import os
import sys
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock

# Añadir el directorio raíz de este microservicio al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from app.main import app

# Creamos el mock para httpx.AsyncClient
mock_http_client = AsyncMock()

@pytest.fixture(autouse=True)
def setup_gateway_client():
    # Asignar el cliente mockeado al estado de la aplicación
    app.state.http_client = mock_http_client
    yield
    mock_http_client.reset_mock()

def test_gateway_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "status: Vivo y respirando" in response.json()[0]

def test_proxy_ingestion_success():
    client = TestClient(app)
    
    # Simular una respuesta exitosa
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "dataset_id": "123"}
    mock_http_client.request.return_value = mock_response
    
    response = client.post("/api/v1/ingesta/datasets", json={"file": "content"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["dataset_id"] == "123"
    mock_http_client.request.assert_called_once()

def test_proxy_ingestion_timeout():
    client = TestClient(app)
    
    # Simular un timeout en la conexión
    mock_http_client.request.side_effect = httpx.TimeoutException("Timeout")
    
    response = client.get("/api/v1/ingesta/datasets/123/raw")
    assert response.status_code == 504
    assert "Timeout" in response.json()["detail"]["error"]

def test_proxy_ingestion_connect_error():
    client = TestClient(app)
    
    # Simular que el microservicio destino está apagado
    mock_http_client.request.side_effect = httpx.ConnectError("Connection refused")
    
    response = client.get("/api/v1/ingesta/datasets/123/raw")
    assert response.status_code == 503
    assert "apagado o inaccesible" in response.json()["detail"]["error"]
