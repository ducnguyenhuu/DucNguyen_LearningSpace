# Retail Shelf Monitoring - Project Specification

**Version**: 1.0.0  
**Date**: December 10, 2025  
**Project Type**: Research & Learning  
**Target Audience**: Junior Python Developers

---

## Executive Summary

This specification defines a **learning-focused** research project that implements retail shelf monitoring using Azure AI and Computer Vision. The project addresses 4 critical retail challenges using public datasets, with emphasis on educational value and production-standard code organization.

**Key Constraints**:
- Research project, NOT production deployment
- Public datasets only (SKU-110K, Grocery Store, RPC)
- Simple implementations with professional code structure
- Educational documentation mandatory for all components

---

## 1. Project Goals

### Primary Objectives

| Goal | Description | Success Criteria |
|------|-------------|------------------|
| **Learn Azure AI** | Hands-on experience with Azure AI services | Complete integration of Custom Vision, Document Intelligence, Azure ML |
| **Master Computer Vision** | Understand CV fundamentals and object detection | Working YOLO model trained on retail dataset |
| **Production Code Practices** | Learn professional Python development | Code follows PEP 8, type hints, modular structure |
| **Solve Real Problems** | Address actual retail challenges | 4 challenges implemented with measurable metrics |

### Learning Outcomes

By completing this project, developers will understand:
- Azure AI service integration (Custom Vision, Document Intelligence)
- Object detection with YOLO
- Azure ML for MLOps
- Production Python package structure
- Computer vision evaluation metrics
- API development with FastAPI

---

## 2. Challenge Specifications

### Challenge 1: Out-of-Stock Detection

**Business Context**: Retailers lose 4-8% annual revenue due to out-of-stock situations.

**Technical Specification**:
```yaml
Input: Shelf image (JPEG/PNG, min 640x480)
Output: List of empty shelf regions with bounding boxes
Method: Object detection → gap identification
Dataset: SKU-110K (11,762 images, 1.7M annotations)

Requirements:
  - Detect all products on shelf
  - Identify gaps between products as empty spaces
  - Flag gaps exceeding minimum width threshold
  - Return confidence scores for each detection

Metrics:
  - Precision: > 90%
  - Recall: > 85%
  - Detection latency: < 500ms per image
```

**Implementation Phases**:
1. **Phase 1**: Train Azure Custom Vision to detect products
2. **Phase 2**: Implement gap detection logic (simple threshold-based)
3. **Phase 3**: Refine with configurable parameters
4. **Phase 4**: Add validation and error handling

**Deliverables**:
- `core/detector.py`: Product detection class
- `notebooks/01_out_of_stock_detection.ipynb`: Experimentation notebook
- `docs/guides/challenge_1_oos_detection.md`: Implementation guide
- `tests/unit/test_detector.py`: Unit tests

---

### Challenge 2: Product Recognition

**Business Context**: Manual SKU identification is slow and error-prone in stores with thousands of products.

**Technical Specification**:
```yaml
Input: Shelf image
Output: List of detected products with SKU labels and bounding boxes
Method: Object detection + classification
Datasets: 
  - Primary: SKU-110K
  - Alternative: Grocery Store (5,125 images, 81 classes)

Requirements:
  - Detect multiple products in single image
  - Classify each detection to SKU level
  - Handle varying orientations and partial occlusions
  - Support both Azure Custom Vision and YOLOv8

Metrics:
  - mAP@0.5: > 85%
  - Classification accuracy: > 90%
  - Inference speed: > 10 FPS (local GPU)
```

**Implementation Phases**:
1. **Phase 1**: Azure Custom Vision object detection (rapid prototype)
2. **Phase 2**: Train YOLOv8 on SKU-110K for comparison
3. **Phase 3**: Add SKU classification layer
4. **Phase 4**: Optimize inference speed

**Deliverables**:
- `core/classifier.py`: SKU classification class
- `models/yolo.py`: YOLOv8 wrapper
- `services/azure_custom_vision.py`: Azure Custom Vision integration
- `notebooks/02_product_recognition.ipynb`: Training & evaluation notebook
- `docs/guides/challenge_2_product_recognition.md`: Implementation guide
- `tests/unit/test_classifier.py`: Unit tests

---

### Challenge 3: Stock Level Estimation

**Business Context**: Retailers need to know product quantities to plan restocking effectively.

**Technical Specification**:
```yaml
Input: Detection results from Challenge 2
Output: Stock count per SKU
Method: Count aggregation from detections
Dataset: Derived from Challenge 2 detections

Requirements:
  - Count products per SKU from detections
  - Estimate shelf depth (front-facing × estimated rows)
  - Track stock trends over time (optional)
  - Simple Python implementation (no ML model)

Metrics:
  - Count accuracy: > 90%
  - Mean Absolute Percentage Error (MAPE): < 15%
```

**Implementation Phases**:
1. **Phase 1**: Simple counting from detection list
2. **Phase 2**: Add depth estimation heuristics
3. **Phase 3**: Implement trend tracking (time series)
4. **Phase 4**: Add statistical validation

**Deliverables**:
- `core/stock_analyzer.py`: Stock counting and analysis
- `notebooks/03_stock_level_estimation.ipynb`: Analysis notebook
- `docs/guides/challenge_3_stock_estimation.md`: Implementation guide
- `tests/unit/test_stock_analyzer.py`: Unit tests

---

### Challenge 4: Price Tag Verification

**Business Context**: Incorrect price tags cause customer complaints and regulatory fines.

**Technical Specification**:
```yaml
Input: Shelf image with price tags
Output: Extracted prices with confidence scores
Method: Azure Document Intelligence (pre-trained OCR)
Dataset: None required (pre-trained model)

Requirements:
  - Detect price tag regions near products
  - Extract text using Azure Document Intelligence OCR
  - Parse price values from various formats ($X.XX, €X,XX)
  - Compare against reference database (simulated)
  - No custom training required

Metrics:
  - OCR accuracy: > 95%
  - Price extraction success rate: > 90%
  - Price match rate: > 95% (when database available)
```

**Implementation Phases**:
1. **Phase 1**: Azure Document Intelligence OCR integration
2. **Phase 2**: Price tag region detection (simple bounding box)
3. **Phase 3**: Price parsing and validation logic
4. **Phase 4**: Database comparison (mock data)

**Deliverables**:
- `core/ocr.py`: OCR and price extraction class
- `services/azure_document_intelligence.py`: Azure service integration
- `notebooks/04_price_tag_verification.ipynb`: Testing notebook
- `docs/guides/challenge_4_price_verification.md`: Implementation guide
- `tests/unit/test_ocr.py`: Unit tests

---

## 3. Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────┘

Data Layer:
  - Public datasets (SKU-110K, Grocery Store, RPC)
  - Azure Blob Storage (training images, models)

AI/ML Layer:
  - Azure Custom Vision (Challenge 1 & 2)
  - YOLOv8 Local/Azure ML (Challenge 2)
  - Python Analysis (Challenge 3)
  - Azure Document Intelligence (Challenge 4)
  - Azure Machine Learning (MLOps)

Application Layer:
  - Jupyter Notebooks (experimentation)
  - FastAPI Service (REST API)
  - Python CLI (utilities)
```

### Technology Stack

| Component | Technology | Justification |
|-----------|------------|---------------|
| **Language** | Python 3.10+ | Industry standard for ML/AI, rich ecosystem |
| **ML Framework** | PyTorch + Ultralytics | YOLOv8 standard, good documentation |
| **Azure AI** | Custom Vision, Document Intelligence | Free tier available, easy to learn |
| **MLOps** | Azure Machine Learning | Complete MLOps platform, learning value |
| **API** | FastAPI | Modern, fast, auto-documentation |
| **Storage** | Azure Blob Storage | Cost-effective, native Azure integration |
| **Testing** | pytest | Python standard, simple to use |
| **Notebooks** | Jupyter | Interactive experimentation |

---

## 4. Project Structure

### Directory Layout

```
retail-shelf-monitoring/
├── src/shelf_monitor/          # Main application package
│   ├── core/                   # Business logic (4 challenges)
│   ├── models/                 # ML model wrappers
│   ├── services/               # Azure service integrations
│   ├── api/                    # FastAPI application
│   ├── config/                 # Configuration management
│   └── utils/                  # Shared utilities
├── notebooks/                  # Jupyter notebooks (by challenge)
├── data/                       # Datasets (raw, processed, annotations)
├── models/                     # Trained model artifacts
├── tests/                      # Test suite (unit, integration)
├── scripts/                    # Utility scripts
├── docker/                     # Docker configuration
├── docs/                       # Documentation
│   ├── guides/                 # Implementation guides (mandatory)
│   ├── ARCHITECTURE.md         # System architecture
│   └── LEARNING_PATH.md        # Learning curriculum
└── .specify/                   # Project specifications
```

### Code Organization Standards

**Per Constitution Principle II**:
- One class per file
- Clear separation of concerns
- Type hints mandatory
- Docstrings (Google/NumPy style)
- Modular design (single responsibility)

**Example Module Structure**:
```python
# src/shelf_monitor/core/detector.py

from typing import List
from pathlib import Path

class ProductDetector:
    """
    Detects products in shelf images using Azure Custom Vision.
    
    This implements Challenge 1 (Out-of-Stock) and Challenge 2 
    (Product Recognition) by detecting product bounding boxes.
    
    Attributes:
        endpoint: Azure Custom Vision endpoint URL
        key: Azure Custom Vision API key
    """
    
    def __init__(self, endpoint: str, key: str) -> None:
        """Initialize detector with Azure credentials."""
        # Simple, clear implementation
        pass
    
    def detect(self, image_path: Path) -> List[Detection]:
        """
        Detect products in shelf image.
        
        Args:
            image_path: Path to input image
            
        Returns:
            List of Detection objects with bounding boxes and confidence
            
        Raises:
            ValueError: If image_path does not exist
            AzureError: If API call fails
        """
        # Implementation here
        pass
```

---

## 5. Data Requirements

### Public Datasets

| Dataset | Images | Annotations | Use Cases | Download |
|---------|--------|-------------|-----------|----------|
| **SKU-110K** | 11,762 | 1.7M bboxes | Challenge 1, 2, 3 | [GitHub](https://github.com/eg4000/SKU110K_CVPR19) |
| **Grocery Store** | 5,125 | 81 classes | Challenge 2 (alt) | [GitHub](https://github.com/marcusklasson/GroceryStoreDataset) |
| **RPC** | 83,739 | 200 SKUs | Challenge 2 (alt) | [Website](https://rpc-dataset.github.io/) |

### Data Preparation

```yaml
Directory Structure:
  data/raw/              # Original downloaded datasets
  data/processed/        # Preprocessed for training
    train/               # 70% split
    val/                 # 15% split
    test/                # 15% split
  data/annotations/      # COCO/YOLO format labels

Preprocessing Steps:
  1. Download dataset using scripts/download_dataset.py
  2. Convert annotations to YOLO format
  3. Split train/val/test
  4. Upload to Azure Blob Storage
  5. Register as Azure ML Dataset

Tools:
  - Python script: scripts/prepare_data.py
  - Format conversion: COCO → YOLO
  - Validation: Check for corrupt images
```

---

## 6. Development Workflow

### Phase-Based Development (Per Constitution Principle V)

**Phase 1: Get It Working**
- Minimal viable implementation
- Focus on core functionality
- Use simplest approach
- Manual testing acceptable

**Phase 2: Make It Clean**
- Add type hints
- Write docstrings
- Refactor for readability
- Add basic unit tests

**Phase 3: Make It Better**
- Optimize performance
- Handle edge cases
- Improve error messages
- Add integration tests

**Phase 4: Production-Ready**
- Comprehensive error handling
- Structured logging
- Input validation
- Complete test coverage

### Weekly Schedule

| Week | Focus | Challenges | Deliverables |
|------|-------|-----------|--------------|
| 1-2 | Environment + Azure Setup | - | Azure resources, dev environment, dataset downloaded |
| 3-4 | Detection Models | 1, 2 | Azure Custom Vision trained, OOS logic implemented |
| 5-6 | Advanced Detection + Counting | 2, 3 | YOLOv8 trained, stock analyzer working |
| 7-8 | OCR + API | 4 | Document Intelligence integrated, FastAPI endpoints |
| 9-10 | MLOps + Refinement | All | Azure ML pipelines, model registry, deployment |

---

## 7. Success Metrics

### Technical Metrics

| Challenge | Metric | Target | Measurement Method |
|-----------|--------|--------|-------------------|
| 1. OOS Detection | Precision | > 90% | TP / (TP + FP) on test set |
| 1. OOS Detection | Recall | > 85% | TP / (TP + FN) on test set |
| 2. Product Recognition | mAP@0.5 | > 85% | COCO evaluation on test set |
| 2. Product Recognition | Inference Speed | > 10 FPS | Average over 100 images |
| 3. Stock Estimation | MAPE | < 15% | Mean absolute % error |
| 4. Price Verification | OCR Accuracy | > 95% | Character-level accuracy |

### Learning Metrics

| Outcome | Assessment |
|---------|-----------|
| **Azure AI Understanding** | Can explain Custom Vision, Document Intelligence, Azure ML |
| **Computer Vision Skills** | Can train and evaluate YOLO models |
| **Python Proficiency** | Code follows PEP 8, uses type hints, proper structure |
| **MLOps Knowledge** | Can set up training pipelines, model registry |
| **API Development** | Can build and document FastAPI endpoints |

---

## 8. Documentation Requirements (MANDATORY)

### Per Constitution Principle III

For **every** implemented feature, create markdown guide in `docs/guides/`:

**Template**:
```markdown
# [Feature Name] - Implementation Guide

## What
Brief description of what this implements.

## Why
Why this approach was chosen. What tradeoffs were made.

## How It Works
Step-by-step explanation of the implementation.

## Key Concepts
- Python concept 1 (e.g., type hints, context managers)
- Azure concept 1 (e.g., Custom Vision SDK)
- Design pattern used (if any)

## Usage Example
```python
# Working code example
```

## Common Issues
- Issue 1 and solution
- Issue 2 and solution

## Next Steps
What to learn next or how to extend this.
```

### Required Documentation Files

- [x] `README.md` - Project overview
- [x] `SPECIFICATION.md` - This document
- [x] `docs/ARCHITECTURE.md` - System architecture
- [x] `docs/LEARNING_PATH.md` - Learning curriculum
- [ ] `docs/guides/challenge_1_oos_detection.md` - Challenge 1 guide
- [ ] `docs/guides/challenge_2_product_recognition.md` - Challenge 2 guide
- [ ] `docs/guides/challenge_3_stock_estimation.md` - Challenge 3 guide
- [ ] `docs/guides/challenge_4_price_verification.md` - Challenge 4 guide
- [ ] `docs/guides/azure_setup.md` - Azure configuration guide
- [ ] `docs/guides/yolo_training.md` - YOLO training guide

---

## 9. Testing Strategy

### Testing Scope (Per Constitution)

**Unit Tests**: Core logic only
- Pure Python functions
- Business logic without external dependencies
- Focus: `core/`, `models/`, `utils/`

**Integration Tests**: Azure service interactions (optional)
- Test actual API calls with mock data
- Validate error handling
- Focus: `services/`

**Manual Testing**: Notebooks and API
- Jupyter notebooks for experimentation
- FastAPI Swagger UI for API testing

### Testing Standards

```python
# tests/unit/test_detector.py

import pytest
from shelf_monitor.core.detector import ProductDetector

def test_detector_initialization():
    """Test detector can be initialized with credentials."""
    detector = ProductDetector(endpoint="test", key="test")
    assert detector.endpoint == "test"

def test_detect_invalid_image_path():
    """Test detector raises error for non-existent image."""
    detector = ProductDetector(endpoint="test", key="test")
    with pytest.raises(ValueError):
        detector.detect(Path("nonexistent.jpg"))
```

**Coverage Target**: > 70% for core modules (not strict requirement)

---

## 10. Azure Service Configuration

### Required Azure Resources

| Service | SKU | Purpose | Estimated Cost |
|---------|-----|---------|---------------|
| **Custom Vision** | F0 (Free) | Product detection training | $0 |
| **Document Intelligence** | F0 (Free) | Price tag OCR | $0 |
| **Blob Storage** | Standard LRS | Dataset and model storage | ~$0.20/month |
| **Azure ML** | Pay-as-you-go | Training compute, MLOps | ~$5-20/month* |

*Use spot instances and auto-shutdown to minimize costs.

### Setup Steps

1. Create Azure subscription (free tier)
2. Create resource group: `rg-retail-shelf-monitoring`
3. Create Custom Vision resource (Training + Prediction)
4. Create Document Intelligence resource
5. Create Storage Account
6. Create Azure ML Workspace
7. Configure `.env` with credentials

**Setup Guide**: See `docs/guides/azure_setup.md` (to be created)

---

## 11. Implementation Checklist

### Environment Setup
- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`requirements.txt`)
- [ ] Azure subscription created
- [ ] Azure resources provisioned
- [ ] `.env` file configured

### Challenge 1: Out-of-Stock Detection
- [ ] Azure Custom Vision project created
- [ ] SKU-110K dataset downloaded
- [ ] Training images uploaded to Custom Vision
- [ ] Model trained and evaluated
- [ ] Gap detection logic implemented
- [ ] Unit tests written
- [ ] Implementation guide documented
- [ ] Notebook completed

### Challenge 2: Product Recognition
- [ ] Azure Custom Vision classification project
- [ ] YOLOv8 training environment set up
- [ ] Model trained on SKU-110K
- [ ] Inference optimized
- [ ] Unit tests written
- [ ] Implementation guide documented
- [ ] Notebook completed

### Challenge 3: Stock Level Estimation
- [ ] Stock counting logic implemented
- [ ] Depth estimation heuristics added
- [ ] Unit tests written
- [ ] Implementation guide documented
- [ ] Notebook completed

### Challenge 4: Price Tag Verification
- [ ] Document Intelligence integrated
- [ ] Price parsing logic implemented
- [ ] Unit tests written
- [ ] Implementation guide documented
- [ ] Notebook completed

### FastAPI Application
- [ ] API structure created
- [ ] Endpoints implemented (`/detect`, `/count`, `/ocr`)
- [ ] Request/response schemas defined
- [ ] API documentation (Swagger) verified
- [ ] Manual testing completed

### MLOps & Deployment
- [ ] Azure ML pipelines configured
- [ ] Models registered in model registry
- [ ] Inference endpoint deployed (optional)
- [ ] Monitoring configured (optional)

---

## 12. Constraints & Boundaries

### In Scope (Per Constitution)
✅ 4 challenges with public datasets
✅ Azure AI services (Custom Vision, Document Intelligence, Azure ML)
✅ Local development with Jupyter notebooks
✅ Simple FastAPI demo API
✅ Basic MLOps with Azure ML
✅ Educational documentation for all components

### Out of Scope
❌ Real-time camera feeds
❌ IoT Hub / Edge deployment
❌ Multi-region deployment
❌ Kubernetes orchestration
❌ Microservices architecture
❌ Advanced monitoring (Application Insights)
❌ Enterprise authentication (Azure AD B2C)
❌ Production-scale performance optimization

---

## 13. Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Azure costs exceed budget** | High | Use free tiers, set budget alerts, auto-shutdown compute |
| **Dataset quality issues** | Medium | Use well-established public datasets (SKU-110K) |
| **Model performance below target** | Medium | Start with Azure Custom Vision, iterate with YOLO |
| **Complexity creep** | High | Constitution enforcement, regular reviews |
| **Time overrun** | Medium | Fixed 10-week timeline, prioritize Phase 1 completions |

---

## 14. Acceptance Criteria

### Project Completion Definition

The project is considered complete when:

1. **All 4 challenges implemented** with working code
2. **Technical metrics met** (or documented why not)
3. **Documentation complete**:
   - All implementation guides written
   - Code has docstrings and comments
   - README accurate and up-to-date
4. **Code quality verified**:
   - Follows PEP 8
   - Type hints present
   - Production structure maintained
5. **API functional**: FastAPI endpoints working
6. **Notebooks runnable**: All 4 challenge notebooks execute successfully
7. **Basic tests passing**: Unit tests for core modules

### Quality Gates

**Before merging code**:
- [ ] Code review checklist passed (5 questions from constitution)
- [ ] Implementation guide created
- [ ] Unit tests written (if applicable)
- [ ] Code runs successfully

**Before project completion**:
- [ ] All 14 acceptance criteria met
- [ ] Peer review completed (if available)
- [ ] Final documentation review

---

## 15. Future Enhancements (Post-Learning)

Once learning objectives are met, consider:

- **Real-time inference**: Deploy to Azure Container Instances
- **Model monitoring**: Track performance drift
- **Advanced features**: A/B testing, canary deployments
- **Production deployment**: IoT Hub, Edge devices
- **Web UI**: React/Vue dashboard
- **Mobile app**: Flutter application

**Important**: These are explicitly out of scope for the learning phase.

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **mAP** | Mean Average Precision - object detection metric |
| **MAPE** | Mean Absolute Percentage Error - regression metric |
| **SKU** | Stock Keeping Unit - unique product identifier |
| **OOS** | Out-of-Stock - empty shelf condition |
| **OCR** | Optical Character Recognition - text extraction from images |
| **MLOps** | Machine Learning Operations - ML lifecycle management |
| **YOLO** | You Only Look Once - real-time object detection architecture |

---

## Appendix B: Reference Architecture

See `docs/ARCHITECTURE.md` for detailed technical architecture.

---

## Appendix C: Learning Resources

- [Azure AI Documentation](https://docs.microsoft.com/azure/cognitive-services/)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [SKU-110K Paper](https://arxiv.org/abs/1904.00853)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-10 | System | Initial specification created from README.md |

---

**Approval**

This specification aligns with the Project Constitution and defines a complete, achievable learning project scope.

**Constitution Compliance**: ✅ All principles followed
- Learning-first approach maintained
- Production structure with simple implementation
- Educational documentation mandatory
- Code quality for learning ensured
- Incremental complexity enforced
