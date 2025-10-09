"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from contextlib import contextmanager

from app.core.config import get_database_config


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self):
        self.db_config = get_database_config()
        self._engine = None
        self._session_factory = None
        self._base = declarative_base()
    
    @property
    def engine(self):
        """Get or create database engine."""
        if self._engine is None:
            connect_args = {}
            
            # SQLite specific configuration
            if self.db_config.is_sqlite():
                connect_args = {
                    "check_same_thread": False,
                    "poolclass": StaticPool
                }
            
            self._engine = create_engine(
                self.db_config.database_url,
                connect_args=connect_args,
                echo=False  # Set to True for SQL debugging
            )
        
        return self._engine
    
    @property
    def session_factory(self):
        """Get or create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        
        return self._session_factory
    
    @property
    def base(self):
        """Get declarative base for models."""
        return self._base
    
    def create_tables(self):
        """Create all database tables."""
        self._base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables."""
        self._base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        session = self.session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @contextmanager
    def get_transaction(self):
        """Get database session with transaction management."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_db() -> Generator[Session, None, None]:
    """Dependency function for FastAPI endpoints."""
    yield from db_manager.get_session()

def get_base():
    """Get the declarative base for models."""
    return db_manager.base

def create_tables():
    """Create all database tables."""
    db_manager.create_tables()

def get_engine():
    """Get database engine."""
    return db_manager.engine
