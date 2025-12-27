"""
Product Detector Module
Module: src/shelf_monitor/core/detector.py
Purpose: Object detection and gap detection for Challenge 1 (Out-of-Stock Detection)

This module provides:
1. Detection dataclass - represents a single product detection
2. GapRegion dataclass - represents an empty shelf space (gap)
3. ProductDetector class - detects products and gaps in shelf images

Related Tasks:
- T025: Create Detection dataclass
- T026: Create GapRegion dataclass
- T027: Implement ProductDetector.__init__()
- T031: Implement ProductDetector.detect_products()
- T032: Implement ProductDetector.detect_gaps()
"""

from dataclasses import dataclass
from typing import List, Optional


# ============================================
# Data Classes
# ============================================

@dataclass
class Detection:
    """
    Represents a single product detection from object detection model.
    
    Attributes:
        bbox: Bounding box as (x, y, width, height) in pixels
            - x: Left coordinate (horizontal position from left edge)
            - y: Top coordinate (vertical position from top edge)
            - width: Box width in pixels
            - height: Box height in pixels
        confidence: Model confidence score (0.0-1.0)
            - Higher values indicate greater certainty
            - Typically filter detections with confidence < 0.5
        label: Detection label (SKU code like "COKE-500ML" or generic "object")
        product_id: Product ID if recognized and matched to database, None otherwise
    
    Validation:
        - confidence must be in range [0.0, 1.0]
        - bbox width and height must be positive (> 0)
        - bbox x and y should be non-negative (>= 0)
    
    Example:
        >>> detection = Detection(
        ...     bbox=(120, 50, 80, 150),
        ...     confidence=0.92,
        ...     label="COKE-500ML",
        ...     product_id=1
        ... )
        >>> print(f"Product detected at x={detection.bbox[0]}, width={detection.bbox[2]}px")
        Product detected at x=120, width=80px
    
    Notes:
        - YOLO models return boxes in (x1, y1, x2, y2) format - convert to (x, y, w, h)
        - Azure Custom Vision returns boxes in (left, top, width, height) format - already compatible
        - Confidence threshold of 0.5 is common default, tune based on false positive/negative rate
    """
    bbox: tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    label: str
    product_id: Optional[int] = None
    
    def __post_init__(self):
        """
        Validate detection data after initialization.
        
        Raises:
            ValueError: If confidence is not in [0.0, 1.0] or bbox dimensions are invalid
        """
        # Validate confidence score
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}. "
                f"Check model output format and ensure proper normalization."
            )
        
        # Validate bbox dimensions
        x, y, width, height = self.bbox
        if width <= 0 or height <= 0:
            raise ValueError(
                f"Bounding box dimensions must be positive. "
                f"Got width={width}, height={height}. "
                f"Full bbox: {self.bbox}"
            )
        
        if x < 0 or y < 0:
            raise ValueError(
                f"Bounding box coordinates must be non-negative. "
                f"Got x={x}, y={y}. "
                f"Full bbox: {self.bbox}"
            )


@dataclass
class GapRegion:
    """
    Represents an empty shelf space detected by gap detection algorithm.
    
    A gap region indicates a potential out-of-stock situation where products
    should be present but are missing. The gap detection algorithm analyzes
    horizontal spacing between detected products to identify these empty areas.
    
    Attributes:
        bbox: Gap bounding box as (x, y, width, height) in pixels
            - x: Left coordinate of gap (where empty space starts)
            - y: Top coordinate of gap (typically aligned with shelf row)
            - width: Gap width in pixels (horizontal empty space)
            - height: Gap height in pixels (typically matches product height)
        gap_width: Gap width in pixels (same as bbox[2], kept for convenience)
            - Used for severity classification
            - Typical thresholds: <100px (normal), 100-150px (medium), >150px (high)
        is_significant: Boolean flag indicating if gap exceeds threshold
            - True if gap_width > MIN_GAP_WIDTH (default 100px)
            - Significant gaps are flagged for restocking alerts
    
    Validation:
        - gap_width must be positive (> 0)
        - bbox width and height must be positive (> 0)
        - bbox x and y should be non-negative (>= 0)
        - gap_width should match bbox[2] for consistency
    
    Example:
        >>> gap = GapRegion(
        ...     bbox=(450, 60, 120, 180),
        ...     gap_width=120,
        ...     is_significant=True  # 120px > 100px threshold
        ... )
        >>> if gap.is_significant:
        ...     print(f"Alert: {gap.gap_width}px gap detected - restock needed!")
        Alert: 120px gap detected - restock needed!
    
    Usage in Gap Detection Algorithm:
        1. Sort product detections by x-coordinate (left to right)
        2. Calculate horizontal spacing between adjacent products
        3. If spacing > MIN_GAP_WIDTH, create GapRegion
        4. Set is_significant=True for gaps exceeding threshold
        5. Return list of GapRegion objects for database persistence
    
    Notes:
        - Gap width threshold (100px) is configurable via settings
        - Small gaps (<100px) might be intentional product spacing
        - Large gaps (>150px) typically indicate entire product row is missing
        - Gap height usually matches the height of surrounding products
    """
    bbox: tuple[int, int, int, int]  # (x, y, width, height)
    gap_width: int
    is_significant: bool
    
    def __post_init__(self):
        """
        Validate gap region data after initialization.
        
        Raises:
            ValueError: If gap_width is not positive or bbox dimensions are invalid
        """
        # Validate gap width
        if self.gap_width <= 0:
            raise ValueError(
                f"Gap width must be positive, got {self.gap_width}. "
                f"Gap width represents horizontal empty space and cannot be zero or negative."
            )
        
        # Validate bbox dimensions
        x, y, width, height = self.bbox
        if width <= 0 or height <= 0:
            raise ValueError(
                f"Bounding box dimensions must be positive. "
                f"Got width={width}, height={height}. "
                f"Full bbox: {self.bbox}"
            )
        
        if x < 0 or y < 0:
            raise ValueError(
                f"Bounding box coordinates must be non-negative. "
                f"Got x={x}, y={y}. "
                f"Full bbox: {self.bbox}"
            )
        
        # Validate consistency between gap_width and bbox width
        if self.gap_width != width:
            raise ValueError(
                f"Gap width ({self.gap_width}) must match bbox width ({width}). "
                f"These should be the same value representing horizontal empty space."
            )
