from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_db
from tests.test_database import override_get_db

# Substitui a dependência do banco de dados real pela de teste
app.dependency_overrides[get_db] = override_get_db

# Cria um cliente de teste que fará as requisições à nossa API
client = TestClient(app)

def test_health_check():
    """
    Testa se o endpoint de health check está funcionando e se a conexão
    com o banco de dados de teste é bem-sucedida.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "service_status": "ok",
        "database_status": "ok"
    }