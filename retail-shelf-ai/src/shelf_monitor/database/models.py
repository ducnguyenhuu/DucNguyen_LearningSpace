"""
Database Models: SQLAlchemy ORM models for retail shelf monitoring.

This module defines 5 database tables:
1. Category: Product categories (beverages, snacks, etc.)
2. Product: Product catalog with SKU, pricing, barcode
3. AnalysisJob: Image analysis tracking (out-of-stock, recognition, etc.)
4. Detection: Individual product detections with bounding boxes
5. PriceHistory: Price verification records over time

All models follow:
- 3NF normalization (no redundant data)
- Full type hints for IDE support
- CHECK constraints for validation
- Proper indexes for query performance
- Relationships using SQLAlchemy ORM

Related:
- Data Model: .specify/plans/data-model.md
- Schemas: src/shelf_monitor/database/schemas.py (Pydantic validation)
- CRUD: src/shelf_monitor/database/crud.py (database operations)
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import relationship, declarative_base, Mapped
from sqlalchemy.schema import Computed
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Numeric,
    Float,
    ForeignKey,
    CheckConstraint,
    JSON,
    Index,
)
from sympy import Product

Base = declarative_base()

class Category(Base):
    '''
    Sample data
        Category(
            id=1,
            name="Beverages",
            description="Soft drinks, juices, water",
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
    '''

    __tablename__ = "categories"

    # columns - this is the product catalog is going to be created in SQL table
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = Column(Text, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)

    # relationships in object model
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name!r})>"

class Product(Base):
    ''' Sample data
    Product(
        id=1,
        sku="COKE-500ML",
        name="Coca-Cola 500ml",
        category_id=1,
        expected_price=1.99,
        barcode="5449000000996",
        image_url="https://example.com/products/coke-500ml.jpg",
        created_at=datetime(2024, 1, 15, 10, 35, 0),
        updated_at=datetime(2024, 1, 15, 10, 35, 0)
    )
    '''

    __tablename__ = "products"

    # columns - this is the product catalog is going to be created in SQL table
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = Column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = Column(String(200), nullable=False)
    category_id: Mapped[int] = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    expected_price: Mapped[float] = Column(Numeric(10, 2), CheckConstraint("expected_price >= 0"), nullable=False)
    barcode: Mapped[Optional[str]] = Column(String(50), unique=True, nullable=True)
    image_url: Mapped[Optional[str]] = Column(Text, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)



    # relationships in object model
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    detections: Mapped[List["Detection"]] = relationship("Detection", back_populates="product")
    price_histories: Mapped[List["PriceHistory"]] = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku={self.sku!r}, name={self.name!r})>"

class AnalysisJob(Base):
    '''
    Sample Data

        AnalysisJob(
        id=1,
        image_path="data/uploads/shelf_20240115_103045.jpg",
        challenge_type="OUT_OF_STOCK",
        status="COMPLETED",
        result_summary={
            "total_products": 45,
            "gaps_detected": 3,
            "gap_regions": [
                {"x": 120, "y": 50, "width": 150, "height": 200},
                {"x": 450, "y": 60, "width": 120, "height": 180}
            ]
        },
        error_message=None,
        created_at=datetime(2024, 1, 15, 10, 30, 45),
        completed_at=datetime(2024, 1, 15, 10, 31, 12)
        )

    '''
    __tablename__ = "analysis_jobs"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    image_path: Mapped[str] = Column(Text, nullable=False)
    challenge_type: Mapped[str] = Column(String(50),CheckConstraint("challenge_type in ('OUT_OF_STOCK', 'PRODUCT_RECOGNITION', 'STOCK_ESTIMATION', 'PRICE_VERIFICATION')"), 
                                                                    nullable=False)
    status: Mapped[str] = Column(String(20),CheckConstraint("status in ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')"), 
                                                            nullable=False, 
                                                            default="PENDING")
    result_summary: Mapped[Optional[dict]] = Column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = Column(Text, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)

    # relationships in object model
    detections: Mapped[List["Detection"]] = relationship("Detection", back_populates="analysis_job", cascade="all, delete-orphan")
    price_histories: Mapped[List["PriceHistory"]] = relationship("PriceHistory", back_populates="analysis_job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (
            f"<AnalysisJob(id={self.id}, challenge_type={self.challenge_type!r}, "
            f"status={self.status!r})>"
        )

class Detection(Base):
    '''
    Sample Data
        Detection(
            id=1,
            analysis_job_id=1,
            product_id=1,
            bbox_x=120,
            bbox_y=50,
            bbox_width=80,
            bbox_height=150,
            confidence=0.92,
            label="COKE-500ML",
            created_at=datetime(2024, 1, 15, 10, 31, 5)
        )
    '''
    __tablename__ = "detections"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    analysis_job_id: Mapped[int] = Column(Integer, ForeignKey("analysis_jobs.id"), nullable=False, index=True)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    bbox_x: Mapped[int] = Column(Integer, CheckConstraint("bbox_x >= 0"), nullable=False)
    bbox_y: Mapped[int] = Column(Integer, CheckConstraint("bbox_y >= 0"), nullable=False)
    bbox_width: Mapped[int] = Column(Integer, CheckConstraint("bbox_width > 0"), nullable=False)
    bbox_height: Mapped[int] = Column(Integer, CheckConstraint("bbox_height > 0"), nullable=False)
    confidence: Mapped[float] = Column(Float, CheckConstraint("confidence >= 0 AND confidence <= 1"), nullable=False)
    label: Mapped[Optional[str]] = Column(String(100), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)

    # relationships in object model
    analysis_job: Mapped["AnalysisJob"] = relationship("AnalysisJob", back_populates="detections")
    product: Mapped["Product"] = relationship("Product", back_populates="detections")



class PriceHistory(Base):
    '''
    Sample Data
        PriceHistory(
            id=1,
            analysis_job_id=5,
            product_id=1,
            detected_price=2.49,
            expected_price=1.99,
            price_difference=0.50,  # Auto-computed
            ocr_confidence=0.88,
            bbox_x=200,
            bbox_y=120,
            bbox_width=60,
            bbox_height=40,
            created_at=datetime(2024, 1, 15, 14, 20, 30)
        )
    '''
    __tablename__ = "price_history"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    analysis_job_id: Mapped[int] = Column(Integer, ForeignKey("analysis_jobs.id"), nullable=False, index=True)
    product_id: Mapped[int] = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    detected_price: Mapped[float] = Column(Numeric(10, 2), CheckConstraint("detected_price >= 0"), nullable=False)
    expected_price: Mapped[float] = Column(Numeric(10, 2), CheckConstraint("expected_price >= 0"), nullable=False)
    price_difference: Mapped[float] = Column(Numeric(10,2),Computed("detected_price - expected_price"), nullable=False, index=True)
    ocr_confidence: Mapped[float] = Column(Float, CheckConstraint("ocr_confidence >= 0 AND ocr_confidence <= 1"), nullable=False)
    bbox_x: Mapped[int] = Column(Integer, CheckConstraint("bbox_x >= 0"), nullable=False)
    bbox_y: Mapped[int] = Column(Integer, CheckConstraint("bbox_y >= 0"), nullable=False)
    bbox_width: Mapped[int] = Column(Integer, CheckConstraint("bbox_width > 0"), nullable=False)
    bbox_height: Mapped[int] = Column(Integer, CheckConstraint("bbox_height > 0"), nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)

    # relationships in object model
    analysis_job: Mapped["AnalysisJob"] = relationship("AnalysisJob", back_populates="price_histories")
    product: Mapped["Product"] = relationship("Product", back_populates="price_histories")
        
    def __repr__(self) -> str:
        return (
            f"<PriceHistory(id={self.id}, job_id={self.analysis_job_id}, "
            f"product_id={self.product_id}, detected=${self.detected_price}, "
            f"expected=${self.expected_price}, diff=${self.price_difference})>"
        )