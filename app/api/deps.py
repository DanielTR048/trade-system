# app/api/deps.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from typing import Generator

# Cria a engine de conexão com o banco de dados
engine = create_engine(settings.DATABASE_URL)

# Cria uma fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Gerador de dependência que fornece uma sessão de banco de dados
    para um request da API e a fecha ao final.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()