from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis
from contextlib import contextmanager
from config import Config
from database.models import Base
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
            Config.DATABASE_URL,
            poolclass=StaticPool,
            pool_pre_ping=True,
            echo=False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
        
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
        
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
            
    def get_redis(self):
        """Get Redis client"""
        return self.redis_client
        
    def close_connections(self):
        """Close all connections"""
        self.engine.dispose()
        self.redis_client.close()

# Global database manager instance
db_manager = DatabaseManager()