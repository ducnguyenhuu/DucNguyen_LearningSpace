"""
CRUD Operations Tests - Verify all CRUD functions work correctly.

This tests the fixed bugs and ensures CRUD operations are safe.
"""

import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.shelf_monitor.database.models import Base, Category, Product
from src.shelf_monitor.database import crud


@pytest.fixture(scope="function")
def db_session():
    """Create in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestCategoryCRUD:
    """Test Category CRUD operations."""
    
    def test_create_category(self, db_session):
        """Test creating a category."""
        category = crud.create_category(db_session, name="Beverages", description="All drinks")
        
        assert category.id is not None
        assert category.name == "Beverages"
        assert category.description == "All drinks"
        assert category.created_at is not None
    
    def test_create_duplicate_category(self, db_session):
        """Test that duplicate category names are rejected."""
        crud.create_category(db_session, name="Beverages", description="All drinks")
        
        with pytest.raises(ValueError, match="already exists"):
            crud.create_category(db_session, name="Beverages", description="Duplicate")
    
    def test_get_category(self, db_session):
        """Test getting category by ID."""
        created = crud.create_category(db_session, name="Snacks", description="Chips and candy")
        
        fetched = crud.get_category(db_session, created.id)
        
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Snacks"
    
    def test_get_category_by_name(self, db_session):
        """Test getting category by name."""
        crud.create_category(db_session, name="Dairy", description="Milk products")
        
        category = crud.get_category_by_name(db_session, "Dairy")
        
        assert category is not None
        assert category.name == "Dairy"
    
    def test_update_category(self, db_session):
        """Test updating category."""
        category = crud.create_category(db_session, name="Beverages", description="Drinks")
        
        updated = crud.update_category(
            db_session, 
            category.id, 
            name="Drinks",
            description="All beverages"
        )
        
        assert updated.name == "Drinks"
        assert updated.description == "All beverages"
    
    def test_delete_category(self, db_session):
        """Test deleting empty category."""
        category = crud.create_category(db_session, name="ToDelete", description="Test")
        
        success = crud.delete_category(db_session, category.id)
        
        assert success is True
        assert crud.get_category(db_session, category.id) is None
    
    def test_delete_category_with_products(self, db_session):
        """Test that category with products cannot be deleted."""
        category = crud.create_category(db_session, name="Beverages", description="Drinks")
        crud.create_product(
            db_session,
            sku="COKE-001",
            name="Coke",
            category_id=category.id,
            expected_price=1.99,
            barcode=None,
            image_url=None
        )
        
        with pytest.raises(ValueError, match="Cannot delete category"):
            crud.delete_category(db_session, category.id)


class TestProductCRUD:
    """Test Product CRUD operations - focusing on fixed bugs."""
    
    def test_create_product(self, db_session):
        """Test creating a product (Bug #1, #2 fix verification)."""
        category = crud.create_category(db_session, name="Beverages", description="Drinks")
        
        # This tests Bug #1 fix (category_id variable) and Bug #2 fix (refresh argument)
        product = crud.create_product(
            db_session,
            sku="COKE-500ML",
            name="Coca-Cola 500ml",
            category_id=category.id,
            expected_price=1.99,
            barcode="049000050103",
            image_url="https://example.com/coke.jpg"
        )
        
        assert product.id is not None  # Bug #2 fix: refresh() now works
        assert product.sku == "COKE-500ML"
        assert product.category_id == category.id
        assert float(product.expected_price) == 1.99
    
    def test_create_product_invalid_category(self, db_session):
        """Test that invalid category_id is rejected (Bug #1 fix verification)."""
        # Bug #1 was checking wrong variable - this ensures fix works
        with pytest.raises(ValueError, match="Category with id 999 does not exist"):
            crud.create_product(
                db_session,
                sku="INVALID",
                name="Invalid Product",
                category_id=999,  # Non-existent category
                expected_price=1.99,
                barcode=None,
                image_url=None
            )
    
    def test_get_product(self, db_session):
        """Test getting product by ID (Bug #3 fix verification)."""
        category = crud.create_category(db_session, name="Beverages", description="Drinks")
        created = crud.create_product(
            db_session,
            sku="PEPSI-001",
            name="Pepsi",
            category_id=category.id,
            expected_price=1.79,
            barcode=None,
            image_url=None
        )
        
        # Bug #3 fix: This should NOT raise error when product exists
        fetched = crud.get_product(db_session, created.id)
        
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == "Pepsi"
    
    def test_get_product_not_found(self, db_session):
        """Test getting non-existent product raises error (Bug #3 fix)."""
        # Bug #3 was reversed logic - should raise when NOT found
        with pytest.raises(ValueError, match="does not exist"):
            crud.get_product(db_session, 999)
    
    def test_update_product(self, db_session):
        """Test updating product (Bug #4, #5 fix verification)."""
        category = crud.create_category(db_session, name="Beverages", description="Drinks")
        product = crud.create_product(
            db_session,
            sku="SPRITE-001",
            name="Sprite",
            category_id=category.id,
            expected_price=1.49,
            barcode=None,
            image_url=None
        )
        
        # Bug #4 fix: kwargs.items() now has parentheses
        # Bug #5 fix: commit() and refresh() now called properly
        updated = crud.update_product(
            db_session,
            product.id,
            name="Sprite Lemon-Lime",
            expected_price=1.79
        )
        
        assert updated is not None
        assert updated.name == "Sprite Lemon-Lime"
        assert float(updated.expected_price) == 1.79
        assert updated.updated_at is not None
    
    def test_update_product_category(self, db_session):
        """Test updating product category_id."""
        category1 = crud.create_category(db_session, name="Beverages", description="Drinks")
        category2 = crud.create_category(db_session, name="Snacks", description="Food")
        
        product = crud.create_product(
            db_session,
            sku="CHIP-001",
            name="Chips",
            category_id=category1.id,
            expected_price=2.49,
            barcode=None,
            image_url=None
        )
        
        updated = crud.update_product(db_session, product.id, category_id=category2.id)
        
        assert updated.category_id == category2.id
    
    def test_get_product_by_sku(self, db_session):
        """Test getting product by SKU."""
        category = crud.create_category(db_session, name="Beverages", description="Drinks")
        crud.create_product(
            db_session,
            sku="FANTA-001",
            name="Fanta",
            category_id=category.id,
            expected_price=1.69,
            barcode=None,
            image_url=None
        )
        
        product = crud.get_product_by_sku(db_session, "FANTA-001")
        
        assert product is not None
        assert product.name == "Fanta"
    
    def test_get_products_with_search(self, db_session):
        """Test searching products."""
        category = crud.create_category(db_session, name="Beverages", description="Drinks")
        crud.create_product(db_session, sku="COKE-001", name="Coca-Cola", category_id=category.id, expected_price=1.99, barcode=None, image_url=None)
        crud.create_product(db_session, sku="PEPSI-001", name="Pepsi", category_id=category.id, expected_price=1.89, barcode=None, image_url=None)
        crud.create_product(db_session, sku="SPRITE-001", name="Sprite", category_id=category.id, expected_price=1.79, barcode=None, image_url=None)
        
        # Search by name
        results = crud.get_products(db_session, search="Pepsi")
        assert len(results) == 1
        assert results[0].name == "Pepsi"
        
        # Search by SKU
        results = crud.get_products(db_session, search="COKE")
        assert len(results) == 1
        assert results[0].sku == "COKE-001"
    
    def test_delete_product(self, db_session):
        """Test deleting product."""
        category = crud.create_category(db_session, name="Beverages", description="Drinks")
        product = crud.create_product(
            db_session,
            sku="DELETE-001",
            name="To Delete",
            category_id=category.id,
            expected_price=1.00,
            barcode=None,
            image_url=None
        )
        
        success = crud.delete_product(db_session, product.id)
        
        assert success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
