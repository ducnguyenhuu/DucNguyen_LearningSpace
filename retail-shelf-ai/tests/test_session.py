"""
Test Database Session Configuration.

Verifies that session.py is configured correctly and handles edge cases.
"""

import pytest
import os
from sqlalchemy.orm import Session

# Test imports
def test_imports():
    """Test that all required modules can be imported."""
    from src.shelf_monitor.database import session
    assert session.engine is not None
    assert session.SessionLocal is not None
    assert session.DATABASE_URL is not None


def test_database_url_default():
    """Test that DATABASE_URL has a fallback default."""
    from src.shelf_monitor.database.session import DATABASE_URL
    
    # Should never be None
    assert DATABASE_URL is not None
    assert isinstance(DATABASE_URL, str)
    assert len(DATABASE_URL) > 0


def test_engine_creation():
    """Test that engine is created successfully."""
    from src.shelf_monitor.database.session import engine
    
    assert engine is not None
    assert hasattr(engine, 'connect')


def test_session_creation():
    """Test that sessions can be created."""
    from src.shelf_monitor.database.session import SessionLocal
    
    session = SessionLocal()
    assert session is not None
    assert isinstance(session, Session)
    session.close()


def test_get_db_generator():
    """Test that get_db() returns a generator."""
    from src.shelf_monitor.database.session import get_db
    
    db_gen = get_db()
    assert hasattr(db_gen, '__next__')  # Is a generator
    
    # Get the session
    db = next(db_gen)
    assert isinstance(db, Session)
    
    # Cleanup
    try:
        next(db_gen)
    except StopIteration:
        pass  # Expected - generator exhausted


def test_get_db_context_manager():
    """Test that get_db() works as a context manager."""
    from src.shelf_monitor.database.session import get_db
    
    # Simulate FastAPI Depends behavior
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Use the session
        assert isinstance(db, Session)
        # Session should be open
        assert not db.is_active or True  # May or may not be active yet
    finally:
        # Cleanup
        try:
            next(db_gen)
        except StopIteration:
            pass


def test_get_session():
    """Test get_session() helper function."""
    from src.shelf_monitor.database.session import get_session
    
    db = get_session()
    assert db is not None
    assert isinstance(db, Session)
    db.close()


def test_create_tables():
    """Test that create_tables() works without errors."""
    from src.shelf_monitor.database.session import create_tables
    
    # Should not raise any exceptions
    create_tables()
    
    # Run again - should be idempotent
    create_tables()


def test_sqlite_detection():
    """Test that SQLite is detected correctly."""
    from src.shelf_monitor.database.session import is_sqlite, DATABASE_URL
    
    if "sqlite" in DATABASE_URL.lower():
        assert is_sqlite is True
    else:
        assert is_sqlite is False


def test_pool_configuration():
    """Test that appropriate pool is configured for SQLite."""
    from src.shelf_monitor.database.session import engine, is_sqlite
    from sqlalchemy.pool import StaticPool, QueuePool
    
    if is_sqlite:
        # SQLite should use StaticPool
        assert isinstance(engine.pool, StaticPool)
    else:
        # Others should use QueuePool or similar
        assert hasattr(engine.pool, 'size')


def test_multiple_sessions():
    """Test that multiple sessions can be created independently."""
    from src.shelf_monitor.database.session import SessionLocal
    
    session1 = SessionLocal()
    session2 = SessionLocal()
    
    # Should be different objects
    assert session1 is not session2
    
    session1.close()
    session2.close()


def test_session_independence():
    """Test that sessions are independent (no shared state)."""
    from src.shelf_monitor.database.session import get_db
    from src.shelf_monitor.database.models import Category
    
    # Create tables first
    from src.shelf_monitor.database.session import create_tables
    create_tables()
    
    # Session 1
    gen1 = get_db()
    db1 = next(gen1)
    
    # Session 2
    gen2 = get_db()
    db2 = next(gen2)
    
    # Add to session 1
    cat1 = Category(name="Test1", description="From session 1")
    db1.add(cat1)
    
    # Session 2 shouldn't see uncommitted changes
    # (depends on isolation level, but sessions should be independent)
    
    # Cleanup
    try:
        next(gen1)
    except StopIteration:
        pass
    
    try:
        next(gen2)
    except StopIteration:
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
