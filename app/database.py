from sqlmodel import create_engine, SQLModel, Session
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_engine():
    database_url = settings.DATABASE_URL

    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    elif database_url.startswith("postgresql"):
        connect_args = {}
    else:
        connect_args = {}
    
    engine = create_engine(database_url, echo=True, connect_args=connect_args)
    return engine

engine = get_engine()

#Cria no banco todas as tabelas definidas com o SQLModel
def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

def get_db():
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        pass