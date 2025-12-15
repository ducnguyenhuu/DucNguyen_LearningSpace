"""
Comprehensive tests for database models and Pydantic schemas.

This test suite validates:
1. SQLAlchemy model definitions and constraints
2. Pydantic schema validation rules
3. Model-Schema compatibility (ORM mode)
4. Relationships and cascading behavior
5. Field constraints and edge cases

Run with: pytest tests/test_models_and_schemas.py -v
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

# Import models
from src.shelf_monitor.database.models import Base, Category, Product, AnalysisJob, Detection, PriceHistory

# Import schemas
from src.shelf_monitor.database.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductReponse,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def db_engine():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for each test."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


# ============================================================================
# Test SQLAlchemy Models
# ============================================================================

class TestCategoryModel:
    """Test Category model constraints and behavior."""
    
    def test_create_valid_category(self, db_session: Session):
        """Test creating a valid category."""
        category = Category(
            name="Beverages",
            description="Soft drinks, juices, water"
        )
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.name == "Beverages"
        assert category.created_at is not None
        assert len(category.products) == 0
    
    def test_category_unique_name_constraint(self, db_session: Session):
        """Test that duplicate category names are rejected."""
        category1 = Category(name="Beverages")
        category2 = Category(name="Beverages")
        
        db_session.add(category1)
        db_session.commit()
        
        db_session.add(category2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_category_repr(self):
        """Test __repr__ method."""
        category = Category(id=1, name="Snacks")
        assert repr(category) == "<Category(id=1, name='Snacks')>"


class TestProductModel:
    """Test Product model constraints and relationships."""
    
    def test_create_valid_product(self, db_session: Session):
        """Test creating a valid product with category."""
        category = Category(name="Beverages")
        db_session.add(category)
        db_session.commit()
        
        product = Product(
            sku="COKE-500ML",
            name="Coca-Cola 500ml",
            category_id=category.id,
            expected_price=Decimal("1.99"),
            barcode="5449000000996"
        )
        db_session.add(product)
        db_session.commit()
        
        assert product.id is not None
        assert product.sku == "COKE-500ML"
        assert product.category.name == "Beverages"
        assert float(product.expected_price) == 1.99
    
    def test_product_unique_sku_constraint(self, db_session: Session):
        """Test that duplicate SKUs are rejected."""
        category = Category(name="Beverages")
        db_session.add(category)
        db_session.commit()
        
        product1 = Product(sku="COKE-500ML", name="Coke", category_id=category.id, expected_price=1.99)
        product2 = Product(sku="COKE-500ML", name="Cola", category_id=category.id, expected_price=2.99)
        
        db_session.add(product1)
        db_session.commit()
        
        db_session.add(product2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_product_price_constraint(self, db_session: Session):
        """Test that negative prices are rejected."""
        category = Category(name="Beverages")
        db_session.add(category)
        db_session.commit()
        
        product = Product(
            sku="INVALID", 
            name="Invalid Product", 
            category_id=category.id, 
            expected_price=-1.99  # Invalid negative price
        )
        db_session.add(product)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_product_category_relationship(self, db_session: Session):
        """Test bidirectional relationship between Product and Category."""
        category = Category(name="Snacks")
        db_session.add(category)
        db_session.commit()
        
        product1 = Product(sku="CHIP-001", name="Chips", category_id=category.id, expected_price=2.50)
        product2 = Product(sku="CANDY-001", name="Candy", category_id=category.id, expected_price=1.50)
        
        db_session.add_all([product1, product2])
        db_session.commit()
        
        # Test forward relationship
        assert product1.category.name == "Snacks"
        
        # Test backward relationship
        assert len(category.products) == 2
        assert product1 in category.products
        assert product2 in category.products
    
    def test_cascade_delete_category(self, db_session: Session):
        """Test that deleting category cascades to products."""
        category = Category(name="Dairy")
        db_session.add(category)
        db_session.commit()
        
        product = Product(sku="MILK-001", name="Milk", category_id=category.id, expected_price=3.99)
        db_session.add(product)
        db_session.commit()
        
        product_id = product.id
        
        # Delete category
        db_session.delete(category)
        db_session.commit()
        
        # Product should also be deleted
        deleted_product = db_session.query(Product).filter_by(id=product_id).first()
        assert deleted_product is None


class TestAnalysisJobModel:
    """Test AnalysisJob model constraints."""
    
    def test_create_valid_analysis_job(self, db_session: Session):
        """Test creating a valid analysis job."""
        job = AnalysisJob(
            image_path="data/uploads/shelf_001.jpg",
            challenge_type="OUT_OF_STOCK",
            status="PENDING"
        )
        db_session.add(job)
        db_session.commit()
        
        assert job.id is not None
        assert job.status == "PENDING"
        assert job.created_at is not None
        assert job.completed_at is None
    
    def test_analysis_job_invalid_challenge_type(self, db_session: Session):
        """Test that invalid challenge types are rejected."""
        job = AnalysisJob(
            image_path="data/uploads/shelf_001.jpg",
            challenge_type="INVALID_TYPE",  # Invalid
            status="PENDING"
        )
        db_session.add(job)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_analysis_job_invalid_status(self, db_session: Session):
        """Test that invalid status values are rejected."""
        job = AnalysisJob(
            image_path="data/uploads/shelf_001.jpg",
            challenge_type="OUT_OF_STOCK",
            status="INVALID_STATUS"  # Invalid
        )
        db_session.add(job)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestDetectionModel:
    """Test Detection model constraints."""
    
    def test_create_valid_detection(self, db_session: Session):
        """Test creating a valid detection."""
        # Setup dependencies
        category = Category(name="Beverages")
        db_session.add(category)
        db_session.commit()
        
        product = Product(sku="COKE-001", name="Coke", category_id=category.id, expected_price=1.99)
        db_session.add(product)
        db_session.commit()
        
        job = AnalysisJob(image_path="test.jpg", challenge_type="PRODUCT_RECOGNITION", status="PROCESSING")
        db_session.add(job)
        db_session.commit()
        
        # Create detection
        detection = Detection(
            analysis_job_id=job.id,
            product_id=product.id,
            bbox_x=100,
            bbox_y=200,
            bbox_width=80,
            bbox_height=150,
            confidence=0.92,
            label="COKE-001"
        )
        db_session.add(detection)
        db_session.commit()
        
        assert detection.id is not None
        assert detection.confidence == 0.92
        assert detection.product.sku == "COKE-001"
    
    def test_detection_negative_bbox_constraint(self, db_session: Session):
        """Test that negative bounding box values are rejected."""
        category = Category(name="Beverages")
        db_session.add(category)
        db_session.commit()
        
        product = Product(sku="COKE-001", name="Coke", category_id=category.id, expected_price=1.99)
        db_session.add(product)
        db_session.commit()
        
        job = AnalysisJob(image_path="test.jpg", challenge_type="PRODUCT_RECOGNITION", status="PROCESSING")
        db_session.add(job)
        db_session.commit()
        
        detection = Detection(
            analysis_job_id=job.id,
            product_id=product.id,
            bbox_x=-10,  # Invalid negative
            bbox_y=200,
            bbox_width=80,
            bbox_height=150,
            confidence=0.92
        )
        db_session.add(detection)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_detection_confidence_range_constraint(self, db_session: Session):
        """Test that confidence must be between 0 and 1."""
        category = Category(name="Beverages")
        db_session.add(category)
        db_session.commit()
        
        product = Product(sku="COKE-001", name="Coke", category_id=category.id, expected_price=1.99)
        db_session.add(product)
        db_session.commit()
        
        job = AnalysisJob(image_path="test.jpg", challenge_type="PRODUCT_RECOGNITION", status="PROCESSING")
        db_session.add(job)
        db_session.commit()
        
        detection = Detection(
            analysis_job_id=job.id,
            product_id=product.id,
            bbox_x=100,
            bbox_y=200,
            bbox_width=80,
            bbox_height=150,
            confidence=1.5  # Invalid > 1
        )
        db_session.add(detection)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestPriceHistoryModel:
    """Test PriceHistory model and computed fields."""
    
    def test_create_valid_price_history(self, db_session: Session):
        """Test creating a valid price history record."""
        # Setup dependencies
        category = Category(name="Beverages")
        db_session.add(category)
        db_session.commit()
        
        product = Product(sku="COKE-001", name="Coke", category_id=category.id, expected_price=Decimal("1.99"))
        db_session.add(product)
        db_session.commit()
        
        job = AnalysisJob(image_path="test.jpg", challenge_type="PRICE_VERIFICATION", status="PROCESSING")
        db_session.add(job)
        db_session.commit()
        
        # Create price history
        price_history = PriceHistory(
            analysis_job_id=job.id,
            product_id=product.id,
            detected_price=Decimal("2.49"),
            expected_price=Decimal("1.99"),
            ocr_confidence=0.88,
            bbox_x=200,
            bbox_y=120,
            bbox_width=60,
            bbox_height=40
        )
        db_session.add(price_history)
        db_session.commit()
        
        # Refresh to get computed value
        db_session.refresh(price_history)
        
        assert price_history.id is not None
        assert float(price_history.detected_price) == 2.49
        assert float(price_history.expected_price) == 1.99
        # Computed field: price_difference should be 0.50
        assert float(price_history.price_difference) == 0.50


# ============================================================================
# Test Pydantic Schemas
# ============================================================================

class TestCategorySchemas:
    """Test Category Pydantic schemas validation."""
    
    def test_category_create_valid(self):
        """Test valid category creation schema."""
        data = {
            "name": "Beverages",
            "description": "Soft drinks and juices"
        }
        schema = CategoryCreate(**data)
        
        assert schema.name == "Beverages"
        assert schema.description == "Soft drinks and juices"
    
    def test_category_create_name_too_short(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CategoryCreate(name="", description="Test")
        
        assert "name" in str(exc_info.value)
    
    def test_category_create_name_too_long(self):
        """Test that name exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            CategoryCreate(name="A" * 101, description="Test")
    
    def test_category_update_partial(self):
        """Test that CategoryUpdate allows partial updates."""
        schema = CategoryUpdate(description="Updated description only")
        
        assert schema.name is None
        assert schema.description == "Updated description only"
    
    def test_category_response_from_orm(self, db_session: Session):
        """Test CategoryResponse can serialize from ORM model."""
        category = Category(name="Snacks", description="Chips and candy")
        db_session.add(category)
        db_session.commit()
        
        # Convert ORM model to Pydantic schema
        schema = CategoryResponse.model_validate(category)
        
        assert schema.id == category.id
        assert schema.name == "Snacks"
        assert schema.description == "Chips and candy"
        assert schema.created_at == category.created_at


class TestProductSchemas:
    """Test Product Pydantic schemas validation."""
    
    def test_product_create_valid(self):
        """Test valid product creation schema."""
        data = {
            "sku": "COKE-500ML",
            "name": "Coca-Cola 500ml",
            "category_id": 1,
            "expected_price": 1.99,
            "barcode": "5449000000996"
        }
        schema = ProductCreate(**data)
        
        assert schema.sku == "COKE-500ML"
        assert float(schema.expected_price) == 1.99
    
    def test_product_create_negative_price(self):
        """Test that negative price is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                sku="TEST-001",
                name="Test Product",
                category_id=1,
                expected_price=-1.99  # Invalid
            )
        
        assert "expected_price" in str(exc_info.value).lower()
    
    def test_product_create_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(sku="TEST-001")  # Missing name, category_id, price
        
        errors = str(exc_info.value)
        assert "name" in errors
        assert "category_id" in errors
        assert "expected_price" in errors
    
    def test_product_update_partial(self):
        """Test that ProductUpdate allows partial updates."""
        schema = ProductUpdate(expected_price=2.49)
        
        assert schema.sku is None
        assert schema.name is None
        assert float(schema.expected_price) == 2.49
    
    def test_product_response_from_orm(self, db_session: Session):
        """Test ProductReponse can serialize from ORM model."""
        category = Category(name="Beverages")
        db_session.add(category)
        db_session.commit()
        
        product = Product(
            sku="PEPSI-330ML",
            name="Pepsi 330ml",
            category_id=category.id,
            expected_price=Decimal("1.49"),
            barcode="012345678905"
        )
        db_session.add(product)
        db_session.commit()
        
        # Convert ORM model to Pydantic schema
        schema = ProductReponse.model_validate(product)
        
        assert schema.id == product.id
        assert schema.sku == "PEPSI-330ML"
        assert schema.name == "Pepsi 330ml"


# ============================================================================
# Integration Tests
# ============================================================================

class TestModelSchemaIntegration:
    """Test that models and schemas work together correctly."""
    
    def test_full_workflow_category_and_products(self, db_session: Session):
        """Test complete workflow: create via schema, save to DB, read back."""
        # 1. Create via Pydantic schema
        category_data = CategoryCreate(name="Dairy", description="Milk and cheese")
        
        # 2. Save to database
        category = Category(**category_data.model_dump())
        db_session.add(category)
        db_session.commit()
        
        # 3. Create products
        product_data = ProductCreate(
            sku="MILK-001",
            name="Whole Milk 1L",
            category_id=category.id,
            expected_price=3.99
        )
        
        product = Product(**product_data.model_dump())
        db_session.add(product)
        db_session.commit()
        
        # 4. Read back and validate with response schema
        db_category = db_session.query(Category).filter_by(name="Dairy").first()
        category_response = CategoryResponse.model_validate(db_category)
        
        assert category_response.name == "Dairy"
        assert len(db_category.products) == 1
        
        db_product = db_category.products[0]
        product_response = ProductReponse.model_validate(db_product)
        
        assert product_response.sku == "MILK-001"
        assert product_response.category_id == category.id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
