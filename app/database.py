from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from flask import current_app
from psycopg import ClientCursor
from psycopg import AsyncClientCursor

def get_sync_engine(app=None):
    """
    Creates a synchronous SQLAlchemy engine using psycopg3.
    
    Args:
        app: Flask application instance (optional)
        
    Returns:
        SQLAlchemy Engine instance configured for psycopg3
    """
    if app is None:
        app = current_app
        
    # Get database URI from app config
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    # Create engine with client-side parameter binding for better performance
    engine = create_engine(
        db_uri,
        connect_args={"cursor_factory": ClientCursor},
    )
    
    return engine

def get_async_engine(app=None):
    """
    Creates an asynchronous SQLAlchemy engine using psycopg3.
    
    Args:
        app: Flask application instance (optional)
        
    Returns:
        Async SQLAlchemy Engine instance configured for psycopg3
    """
    if app is None:
        app = current_app
        
    # Get database URI from app config
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    # Create async engine with client-side parameter binding
    engine = create_async_engine(
        db_uri,
        connect_args={"cursor_factory": AsyncClientCursor},
    )
    
    return engine