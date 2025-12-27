"""
API Dependencies - Dependency Injection for FastAPI

This module provides dependency injection functions for FastAPI endpoints.
Dependencies are reusable components injected into route handlers automatically.

Key Dependencies:
- get_db: Database session management (create, use, close pattern)
- get_settings: Configuration settings (future)
- get_current_user: Authentication (future)

Dependency Injection Benefits:
- Automatic resource cleanup (database sessions closed after request)
- Testability (easy to mock dependencies in tests)
- Code reuse (same dependency used across multiple endpoints)
- Type safety (FastAPI validates dependency types)

Usage Example:
    from fastapi import APIRouter, Depends
    from sqlalchemy.orm import Session
    from .dependencies import get_db
    
    router = APIRouter()
    
    @router.get("/products")
    async def list_products(db: Session = Depends(get_db)):
        # db session automatically created and injected
        products = db.query(Product).all()
        return products
        # db session automatically closed after response

Related:
- Database session: src/shelf_monitor/database/session.py
- CRUD operations: src/shelf_monitor/database/crud.py
- Models: src/shelf_monitor/database/models.py
"""

from typing import Generator
from sqlalchemy.orm import Session
from src.shelf_monitor.database.session import get_db

__all__ = ["get_db"]

'''
# Without __all__
from src.shelf_monitor.api.dependencies import *
# Imports: get_db, anything else defined in the file

# With __all__ = ["get_db"]
from src.shelf_monitor.api.dependencies import *
# Imports: ONLY get_db
'''

# Future dependencies can be added here:
# 
# def get_settings() -> Settings:
#     """Get application settings."""
#     from src.shelf_monitor.config.settings import settings
#     return settings
#
# async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
#     """Get authenticated user from JWT token."""
#     # Decode JWT, validate, return user
#     pass

    

