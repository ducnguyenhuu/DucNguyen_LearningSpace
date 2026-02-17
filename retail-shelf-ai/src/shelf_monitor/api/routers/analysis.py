"""
Analysis API Router - Shelf Image Analysis Endpoints

This module implements FastAPI endpoints for submitting and retrieving shelf analysis jobs.
Supports Challenge 1 (Out-of-Stock Detection) with gap detection using YOLOv8.

Endpoints:
    POST /api/v1/analysis/detect-gaps - Submit image for out-of-stock detection
    GET  /api/v1/analysis/jobs/{job_id} - Get analysis job status and results

Architecture:
    Request → Validate image → Save to disk → Create job record →
    Background task → ML processing → Update job with results

Features:
    - Image upload validation (format, size limits)
    - Asynchronous ML processing (non-blocking API)
    - Database persistence (AnalysisJob + Detection tables)
    - Structured error handling with educational messages
    - Response schemas for type-safe JSON

Related:
    - Detector: src/shelf_monitor/core/detector.py
    - CRUD: src/shelf_monitor/database/crud.py
    - Schemas: src/shelf_monitor/database/schemas.py
    - Tasks: T034 (router), T036 (workflow), T037 (ML processing)
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from src.shelf_monitor.api.dependencies import get_db
from src.shelf_monitor.config.settings import settings
from src.shelf_monitor.database import crud
from src.shelf_monitor.database.schemas import AnalysisJobResponse
from src.shelf_monitor.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["analysis"],
    responses={
        404: {"description": "Analysis job not found"},
        400: {"description": "Invalid request (bad image format or parameters)"}
    },
)

# Image validation constants
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# ============================================================================
# Endpoints
# ============================================================================



# ============================================================================
# Helper Functions
# ============================================================================


def save_uploaded_image(file: UploadFile, upload_dir: Path) -> str:
    """
    Save uploaded image to disk with unique filename.
    
    Creates upload directory if it doesn't exist.
    Generates unique filename with timestamp to avoid collisions.
    
    Args:
        file: Uploaded file from FastAPI
        upload_dir: Directory to save images (e.g., data/uploads/)
    
    Returns:
        Relative path to saved image (e.g., "data/uploads/shelf_20240115_103045.jpg")
    
    Raises:
        HTTPException: If file is too large or save fails
    
    Example:
        >>> path = save_uploaded_image(file, Path("data/uploads"))
        >>> print(path)
        data/uploads/shelf_20240115_103045_abc123.jpg
    """
    # Create upload directory if it doesn't exist
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename: shelf_YYYYMMDD_HHMMSS_original.ext
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(file.filename).suffix.lower()
    base_name = Path(file.filename).stem[:50]  # Limit base name length
    unique_filename = f"shelf_{timestamp}_{base_name}{file_ext}"
    
    file_path = upload_dir / unique_filename
    
    try:
        # Save file with size check
        bytes_written = 0
        with open(file_path, "wb") as buffer:
            for chunk in file.file:
                bytes_written += len(chunk)
                
                # Check size during write to avoid memory issues
                if bytes_written > MAX_FILE_SIZE_BYTES:
                    # Remove partial file
                    buffer.close()
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"File size exceeds {MAX_FILE_SIZE_MB}MB limit. "
                            f"Uploaded: {bytes_written / 1024 / 1024:.2f}MB. "
                            f"Please compress the image or use a smaller resolution."
                        ),
                    )
                
                buffer.write(chunk)
        
        logger.info(
            f"Image saved successfully: {unique_filename}",
            extra={
                "file_path": str(file_path),
                "size_mb": bytes_written / 1024 / 1024,
            },
        )
        
        # Return relative path from project root
        return str(file_path)
        
    except HTTPException:
        raise
    
    except Exception as e:
        # Clean up on error
        file_path.unlink(missing_ok=True)
        logger.error(
            f"Failed to save image: {str(e)}",
            extra={"filename": file.filename, "error_type": type(e).__name__},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded image: {str(e)}",
        )

def process_gap_detection_task(job_id: int, image_path: str, confidence_threshold: float) -> None:
    """
    Background task: Run ML gap detection and save results.
    
    This function runs asynchronously after the API returns a response.
    It performs the ML processing and updates the database with results.
    
    Steps:
        1. Update job status to PROCESSING
        2. Load ProductDetector with YOLO model
        3. Detect products in image
        4. Detect gaps between products
        5. Save Detection records to database
        6. Update job status to COMPLETED with summary
        7. Handle errors by updating job status to FAILED
    
    Args:
        job_id: Analysis job ID to update
        image_path: Path to uploaded image
        confidence_threshold: Minimum confidence for detections
    
    Example:
        >>> # Called automatically by BackgroundTasks
        >>> process_gap_detection_task(job_id=1, image_path="data/uploads/shelf.jpg", confidence_threshold=0.5)
    """
    from src.shelf_monitor.core.detector import ProductDetector
    from src.shelf_monitor.database.session import SessionLocal

    db = SessionLocal()
    
    try:
        crud.update_analysis_job(db, job_id=job_id, status="PROCESSING")
        logger.info(
            f"Starting gap detection for job {job_id}",
            extra={"job_id": job_id, "image_path": image_path},
        )

        # initalize detector with YOLO model
        detector = ProductDetector(confidence_threshold=confidence_threshold)

        # detect the products
        detections = detector.detect_product(image_path)
        logger.info(
            f"Detected {len(detections)} products",
            extra={"job_id": job_id, "detection_count": len(detections)},
        )

        # detect gaps
        from PIL import Image
        with Image.open(image_path) as img:
            image_width = img.width
        
        gaps = detector.detect_gaps(detections, image_width= image_width)

        significant_gaps = [g for g in gaps if g.is_significant]

        # Save detections to database
        for det in detections:
            crud.create_detection(
                db=db,
                analysis_job_id=job_id,
                bbox_x=det.bbox[0],
                bbox_y=det.bbox[1],
                bbox_width=det.bbox[2],
                bbox_height=det.bbox[3],
                confidence=det.confidence,
                label=det.label,
                product_id=det.product_id,
            )
        
        result_summary = {
            "total_products": len(detections),
            "gap_detecteed": len(gaps),
            "significant_gaps": len(significant_gaps),
            "gap_regions": [
                {
                    "x": gap.bbox[0],
                    "y": gap.bbox[1],
                    "width": gap.bbox[2],
                    "height": gap.bbox[3],
                    "gap_width": gap.gap_width,
                    "is_significant": gap.is_significant,
                }
                for gap in significant_gaps
            ],
        }

        crud.update_analysis_job(db, job_id=job_id, status="COMPLETED", result_summary=result_summary, completed_at=datetime.now())
    
    except Exception as e:
        # Update job status to FAILED with error message
        error_message = f"{type(e).__name__}: {str(e)}"
        crud.update_analysis_job(
            db=db,
            job_id=job_id,
            status="FAILED",
            error_message=error_message,
            completed_at=datetime.now(),
        )
        
        logger.error(
            f"Gap detection failed for job {job_id}: {error_message}",
            extra={"job_id": job_id, "error_type": type(e).__name__},
        )
    
    finally:
        db.close()