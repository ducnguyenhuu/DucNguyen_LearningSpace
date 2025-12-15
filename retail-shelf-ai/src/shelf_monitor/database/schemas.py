"""
Pydantic Schemas for API Request/Response Validation.

This module defines Pydantic models for validating API requests and responses.
Each schema corresponds to a database table and provides:
- Input validation for API requests (Create/Update schemas)
- Output serialization for API responses (Response schemas)
- Type safety with comprehensive field validation

Pydantic Features Used:
- Field(): Validation constraints (ge, le, min_length, max_length, regex)
- ConfigDict: ORM mode for SQLAlchemy compatibility
- computed_field: For derived fields
- field_validator: Custom validation logic

Usage:
    # Create a new product
    product_data = ProductCreate(
        sku="COKE-500ML",
        name="Coca-Cola 500ml",
        category_id=1,
        expected_price=1.99
    )
    
    # Validate API response
    product_response = ProductResponse.model_validate(db_product)
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, computed_field, field_validator
from typing import List, Optional, Any
from decimal import Decimal


# ============================================================================
# Category Schemas
# ============================================================================
class CategoryBase(BaseModel):
    name: str = Field(
                    ..., 
                    min_length=1, 
                    max_length=100,
                    description="Category name (e.g., 'Beverages', 'Snacks')",
                    example=["Beverages", "Snacks", "Dairy"]
    )

    description: Optional[str] = Field(
                    None, 
                    description="Optional description of the category",
                    example=["Soft drinks, juices, water"]
    )

# User input for creation (strict: require necessary fields)
class CategoryCreate(CategoryBase):
    """Schema for creating a new category.
    
    Example:
        {
            "name": "Beverages",
            "description": "Soft drinks, juices, water"
        }
    """
    pass

# User input for update (all fields optional)
class CategoryUpdate(BaseModel):
    """Schema for updating an existing category (all fields optional).
    
    Example:
        {
            "description": "Updated description"
        }
    """
    name: Optional[str] = Field(
                None, 
                min_length=1, 
                max_length=100,
                description="Update name of the category",
                example=["Beverages", "Snacks", "Dairy"])
    
    description: Optional[str] = Field(
                None, 
                min_length=1, 
                max_length=500,
                description="Update description of the category",
                example=["Soft drinks, juices, water"])
    
# Response schema (from DB model)
class CategoryResponse(CategoryBase):
    """Schema for category data returned in API responses.
    
    Example:
        {
            "id": 1,
            "name": "Beverages",
            "description": "Soft drinks, juices, water",
            "created_at": "2024-01-15T10:30:00Z"
        }
    """

    id: int = Field(..., description="Unique identifier for the category", example=1)
    created_at: datetime = Field(..., description="Timestamp when the category was created", example="2024-01-15T10:30:00Z")
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Product Schemas
# ============================================================================
class ProductBase(BaseModel):
    sku: str = Field(
                ..., 
                min_length=1, 
                max_length=50,
                description="Stock Keeping Unit (unique product code)",
                example=["COKE-500ML", "PEPSI-330ML"],
    )

    name: str = Field(
                ..., 
                min_length=1, 
                max_length=200,
                description="Name of the product",
                example=["Coca-Cola 500ml", "Pepsi 330ml Can"]
    )

    category_id: int = Field(
                ..., 
                ge=0,
                description="Category reference (foreign key to categories.id)",
                example=[1,2,4]
    )

    expected_price: Decimal = Field(
                ..., 
                ge=0,
                decimal_places=2,
                description="Expected retail price (non-negative, two decimal places)",
                example=[1.99, 0.99, 2.50]
    )

    barcode: Optional[str] = Field(
                None,
                min_length=1,
                max_length=50,
                description="Product barcode (EAN/UPC)",
                example=["5449000000996", "012345678905"]
    )

    image_url: Optional[str] = Field(
                None,
                max_length=500,
                description="Optional URL to the product image",
                example=["https://example.com/products/coke-500ml.jpg"]
    )

    # User input for creation (strict: require necessary fields)
    @field_validator("expected_price")
    @classmethod
    def validate_expected_price(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("Expected price must be non-negative.")
        return value.quantize(Decimal("0.01"))
    
class ProductCreate(ProductBase):
    """Schema for creating a new product.
    
    Example:
        {
            "sku": "COKE-500ML",
            "name": "Coca-Cola 500ml",
            "category_id": 1,
            "expected_price": 1.99,
            "barcode": "5449000000996",
            "image_url": "https://example.com/products/coke-500ml.jpg"
        }
    """
    pass

class ProductUpdate(BaseModel):
    """Schema for updating an existing product (all fields optional).
    
    Example:
        {
            "expected_price": 2.09,
            "image_url": "https://example.com/products/coke-500ml-new.jpg"
        }
    """
    sku: Optional[str] = Field(
                None, 
                min_length=1, 
                max_length=50,
                description="Update SKU of the product",
                example=["COKE-500ML", "PEPSI-330ML"],
    )

    name: Optional[str] = Field(
                None, 
                min_length=1, 
                max_length=200,
                description="Update name of the product",
                example=["Coca-Cola 500ml", "Pepsi 330ml Can"]
    )

    category_id: Optional[int] = Field(
                None, 
                ge=0,
                description="Update category reference (foreign key to categories.id)",
                example=[1,2,4]
    )

    expected_price: Optional[Decimal] = Field(
                None, 
                ge=0,
                decimal_places=2,
                description="Update expected retail price (non-negative, two decimal places)",
                example=[1.99, 0.99, 2.50]
    )

    barcode: Optional[str] = Field(
                None,
                min_length=1,
                max_length=50,
                description="Update product barcode (EAN/UPC)",
                example=["5449000000996", "012345678905"]
    )

    image_url: Optional[str] = Field(
                None,
                max_length=500,
                description="Update URL to the product image",
                example=["https://example.com/products/coke-500ml.jpg"]
    )

    @field_validator("expected_price")
    @classmethod
    def validate_expected_price(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is not None and value < 0:
            raise ValueError("Expected price must be non-negative.")
        
        return value.quantize(Decimal("0.01")) if value is not None else None


class ProductReponse(ProductBase):
    """Schema for product data returned in API responses.
    
    Example:
        {
            "id": 1,
            "sku": "COKE-500ML",
            "name": "Coca-Cola 500ml",
            "category_id": 1,
            "expected_price": 1.99,
            "barcode": "5449000000996",
            "image_url": "https://example.com/products/coke-500ml.jpg",
            "created_at": "2024-01-15T10:35:00Z",
            "updated_at": "2024-01-15T10:35:00Z"
        }
    """

    id: int = Field(..., description="Unique identifier for the product", example=[1, 2, 3])
    created_at: datetime = Field(..., description="Timestamp when the product was created", example=["2024-01-15T10:35:00Z"])
    updated_at: datetime = Field(..., description="Timestamp when the product was last updated", example=["2024-01-15T10:35:00Z"])
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# (Other Schemas would follow similar patterns)
# ============================================================================

class AnalysisJobBase(BaseModel):

    image_path: str = Field(..., description="Path to the image to be analyzed", example=["/images/shelf1.jpg"])
    challenge_type: str = Field(..., description="Type of analysis challenge", example=["OUT_OF_STOCK", "PRODUCT_RECOGNITION", "STOCK_ESTIMATION", "PRICE_VERIFICATION"])

    @field_validator("challenge_type")
    @classmethod
    def validate_challenge_type(cls, value: str) -> str:
        valid_types = ["OUT_OF_STOCK", "PRODUCT_RECOGNITION", "STOCK_ESTIMATION", "PRICE_VERIFICATION"]
        if value not in valid_types:
            raise ValueError(f"Invalid challenge type. Must be one of: {', '.join(valid_types)}")
        
        return value


class AnalysisJobCreate(AnalysisJobBase):
    

    """Schema for creating a new analysis job.
    
    Example:
        {
            "image_path": "/images/shelf1.jpg",
            "challenge_type": "OUT_OF_STOCK"
        }
    """
    pass


class AnalysisJobUpdate(BaseModel):

    status: Optional[str] = Field(
                None, 
                min_length=1, 
                max_length=20,
                description="Status of the analysis job",
                example=["PENDING", "PROCESSING", "COMPLETED", "FAILED"]
    )

    result_summary: Optional[dict[str, Any]] = Field(None, description="Summary of the analysis results")
    error_message: Optional[str] = Field(None, description="Error message if the job failed")
    completed_at: Optional[datetime] = Field(
                None,
                description="Timestamp when the analysis job completed",
                example=["2024-01-15T11:30:00Z"]
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, value:str) -> str:
        valid_status = ["PENDING", "PROCESSING", "COMPLETED", "FAILED"]
        if value not in valid_status:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_status)}")
        
        return value

class AnalysisJobResponse(AnalysisJobBase):
    """Schema for analysis job API responses.
    
    Example:
        {
            "id": 1,
            "image_path": "data/uploads/shelf_20240115_103045.jpg",
            "challenge_type": "OUT_OF_STOCK",
            "status": "COMPLETED",
            "result_summary": {
                "total_products": 45,
                "gaps_detected": 3,
                "gap_regions": [
                    {"x": 120, "y": 50, "width": 150, "height": 200}
                ]
            },
            "error_message": null,
            "created_at": "2024-01-15T10:30:45",
            "completed_at": "2024-01-15T10:31:12"
        }
    """

    id: int = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    result_summary: Optional[dict[str, Any]] = Field(None, description="JSON summary of results")
    error_message: Optional[str] = Field(None, description="Error details if status = FAILED")
    created_at: datetime = Field(..., description="Job submission timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Detection Schemas
# ============================================================================


class DetectionBase(BaseModel):
    """Base schema for Detection with shared fields."""

    analysis_job_id: int = Field(
        ..., gt=0, description="Analysis job reference (foreign key to analysis_jobs.id)"
    )
    product_id: Optional[int] = Field(
        None, gt=0, description="Product reference (NULL for unrecognized)"
    )
    bbox_x: int = Field(..., ge=0, description="Bounding box top-left X coordinate (pixels)")
    bbox_y: int = Field(..., ge=0, description="Bounding box top-left Y coordinate (pixels)")
    bbox_width: int = Field(..., gt=0, description="Bounding box width (pixels)")
    bbox_height: int = Field(..., gt=0, description="Bounding box height (pixels)")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Model confidence score (0.0-1.0)"
    )
    label: Optional[str] = Field(
        None, max_length=100, description="Detection label from model"
    )

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is in valid range [0, 1]."""
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {v}")
        return v


class DetectionCreate(DetectionBase):
    """Schema for creating a new detection.
    
    Example:
        {
            "analysis_job_id": 1,
            "product_id": 1,
            "bbox_x": 120,
            "bbox_y": 50,
            "bbox_width": 80,
            "bbox_height": 150,
            "confidence": 0.92,
            "label": "COKE-500ML"
        }
    """

    pass


class DetectionResponse(DetectionBase):
    """Schema for detection API responses.
    
    Example:
        {
            "id": 1,
            "analysis_job_id": 1,
            "product_id": 1,
            "bbox_x": 120,
            "bbox_y": 50,
            "bbox_width": 80,
            "bbox_height": 150,
            "confidence": 0.92,
            "label": "COKE-500ML",
            "created_at": "2024-01-15T10:31:05"
        }
    """

    id: int = Field(..., description="Unique detection identifier")
    created_at: datetime = Field(..., description="Detection timestamp")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PriceHistory Schemas
# ============================================================================


class PriceHistoryBase(BaseModel):
    """Base schema for PriceHistory with shared fields."""

    analysis_job_id: int = Field(
        ..., gt=0, description="Analysis job reference (foreign key to analysis_jobs.id)"
    )
    product_id: int = Field(
        ..., gt=0, description="Product reference (foreign key to products.id)"
    )
    detected_price: Decimal = Field(
        ..., ge=0, decimal_places=2, description="Price extracted via OCR"
    )
    expected_price: Decimal = Field(
        ..., ge=0, decimal_places=2, description="Expected price from product catalog"
    )
    ocr_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="OCR confidence score (0.0-1.0)"
    )
    bbox_x: int = Field(..., ge=0, description="Price tag bounding box X")
    bbox_y: int = Field(..., ge=0, description="Price tag bounding box Y")
    bbox_width: int = Field(..., gt=0, description="Price tag bounding box width")
    bbox_height: int = Field(..., gt=0, description="Price tag bounding box height")

    @field_validator("detected_price", "expected_price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        """Ensure price has at most 2 decimal places."""
        if v < 0:
            raise ValueError("Price must be non-negative")
        return v.quantize(Decimal("0.01"))

    @field_validator("ocr_confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure OCR confidence is in valid range [0, 1]."""
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"OCR confidence must be between 0.0 and 1.0, got {v}")
        return v


class PriceHistoryCreate(PriceHistoryBase):
    """Schema for creating a new price history record.
    
    Example:
        {
            "analysis_job_id": 5,
            "product_id": 1,
            "detected_price": 2.49,
            "expected_price": 1.99,
            "ocr_confidence": 0.88,
            "bbox_x": 200,
            "bbox_y": 120,
            "bbox_width": 60,
            "bbox_height": 40
        }
    """

    pass


class PriceHistoryResponse(PriceHistoryBase):
    """Schema for price history API responses.
    
    Note: price_difference is auto-computed by database (GENERATED column).
    
    Example:
        {
            "id": 1,
            "analysis_job_id": 5,
            "product_id": 1,
            "detected_price": 2.49,
            "expected_price": 1.99,
            "price_difference": 0.50,
            "ocr_confidence": 0.88,
            "bbox_x": 200,
            "bbox_y": 120,
            "bbox_width": 60,
            "bbox_height": 40,
            "created_at": "2024-01-15T14:20:30"
        }
    """

    id: int = Field(..., description="Unique price record identifier")
    price_difference: Decimal = Field(
        ...,
        decimal_places=2,
        description="Computed difference (detected_price - expected_price)",
    )
    created_at: datetime = Field(..., description="Price detection timestamp")

    model_config = ConfigDict(from_attributes=True)


