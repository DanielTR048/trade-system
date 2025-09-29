from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

# Usa um banco de dados SQLite em memória para os testes
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria todas as tabelas no banco de dados de teste
Base.metadata.create_all(bind=engine)

def override_get_db():
    """
    Esta função substitui a dependência `get_db` original
    para usar o banco de dados de teste durante os testes.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()