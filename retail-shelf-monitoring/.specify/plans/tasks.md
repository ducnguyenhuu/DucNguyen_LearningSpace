# Task Breakdown: Retail Shelf Monitoring

**Feature**: Retail Shelf Monitoring with Azure AI and Computer Vision  
**Plan**: [plan.md](./plan.md) | **Spec**: [SPECIFICATION.md](../../SPECIFICATION.md)  
**Timeline**: 12 weeks | **Target**: Junior Python developers learning ML + Backend + Database

---

## Overview

This learning project implements 4 ML challenges (Challenge 1: Out-of-Stock Detection, Challenge 2: Product Recognition, Challenge 3: Stock Estimation, Challenge 4: Price Verification) with a full-stack architecture (PostgreSQL database + FastAPI REST API + ML core). Tasks are organized by user story to enable independent implementation and testing.

**Note**: The term "User Story" (US1-US4) in this task document corresponds to "Challenge" (Challenge 1-4) in SPECIFICATION.md:
- User Story 1 (US1) = Challenge 1: Out-of-Stock Detection
- User Story 2 (US2) = Challenge 2: Product Recognition
- User Story 3 (US3) = Challenge 3: Stock Estimation
- User Story 4 (US4) = Challenge 4: Price Verification

**Implementation Strategy**:
- **MVP First**: Complete User Story 1 (Challenge 1: Out-of-Stock Detection) as minimum viable product
- **Sequential Delivery**: Each user story is independently testable before moving to next
- **Database-First**: Set up schema and seed data before ML challenges
- **API Parallel to ML**: Implement API endpoints alongside ML modules

---

## Task Format

```
- [ ] [TaskID] [P] [Story] Description with file path
```

- **TaskID**: Sequential number (T001, T002...)
- **[P]**: Parallelizable (different files, no dependencies)
- **[Story]**: User story label ([US1], [US2], etc.) for story-specific tasks
- **Description**: Clear action with exact file path

---

## Phase 1: Setup & Foundational Infrastructure

**Goal**: Establish development environment, SQLite database, and project structure before ML implementation.

### Setup Tasks

- [X] T001 Create virtual environment and install Python 3.10+ dependencies
- [X] T002 Initialize Git repository structure with .gitignore for data/, models/, .env
- [X] T003 Create .env.example template with Azure and database credential placeholders
- [X] T004 Create data/ directory for SQLite database (auto-created by SQLAlchemy)
- [X] T005 Initialize Alembic for database migrations in alembic/ directory
- [X] T006 Create Azure subscription and provision Custom Vision F0 resource
- [X] T007 Create Azure Document Intelligence F0 resource
- [X] T008 Configure .env file with Azure credentials and database connection string
- [X] T008a [P] Create .specify/plans/data-model.md with 8 entity definitions (5 DB tables: categories, products, analysis_jobs, detections, price_history + 3 dataclasses: Detection, GapRegion, StockCount)
- [X] T008b [P] Create .specify/plans/contracts/ directory with 7 Python module interface contracts (detector.py, classifier.py, stock_analyzer.py, ocr.py, products.py, analysis.py, crud.py)

### Foundational Tasks (Blocking Prerequisites)

- [X] T009 Create src/shelf_monitor/ package structure with __init__.py files
- [X] T010 [P] Implement database models in src/shelf_monitor/database/models.py (5 tables: Product, Category, AnalysisJob, Detection, PriceHistory) with CHECK constraints for bbox validation and price_difference GENERATED column
- [X] T011 [P] Create Pydantic schemas in src/shelf_monitor/database/schemas.py for validation
- [X] T012 [P] Implement CRUD operations in src/shelf_monitor/database/crud.py
- [X] T013 [P] Create database session management in src/shelf_monitor/database/session.py
- [ ] T014 Generate first Alembic migration for all 5 database tables
- [ ] T015 Apply database migrations (alembic upgrade head) to create schema
- [ ] T016 [P] Download SKU-110K dataset (11,762 images) to data/raw/SKU110K/ using scripts/download_dataset.py
- [ ] T017 [P] Preprocess dataset and split 70/15/15 (train/val/test) using scripts/prepare_data.py
- [ ] T018 Seed product catalog from SKU-110K annotations using scripts/seed_products.py
- [ ] T019 [P] Create FastAPI app skeleton in src/shelf_monitor/api/main.py with CORS
- [ ] T020 [P] Implement dependency injection for database sessions in src/shelf_monitor/api/dependencies.py
- [ ] T021 [P] Create health check router in src/shelf_monitor/api/routers/health.py
- [ ] T022 [P] Implement configuration management in src/shelf_monitor/config/settings.py
- [ ] T023 [P] Set up logging utilities in src/shelf_monitor/utils/logging.py
- [ ] T024 Verify FastAPI server starts and /api/v1/health endpoint returns 200
- [ ] T024a [P] Create .specify/plans/quickstart.md with installation steps, database setup, API startup commands, and Challenge 1 walkthrough example

---

## Phase 2: User Story 1 - Out-of-Stock Detection (Challenge 1)

**User Story**: As a store manager, I want to detect empty shelf spaces so I can restock products before customers notice.

**Acceptance Criteria**:
- Azure Custom Vision model trained to detect product bounding boxes
- Gap detection algorithm identifies empty spaces >100px width
- REST API endpoint accepts image uploads and returns analysis results
- Detection results persisted to database (AnalysisJob + Detection tables)
- Jupyter notebook demonstrates end-to-end workflow
- Metrics: Precision >90%, Recall >85%, latency <500ms

**Independent Test Criteria**: Upload shelf image → API returns gaps list → Database contains job + detections → Visualize in notebook

### US1 Implementation Tasks

- [ ] T025 [P] [US1] Create Detection dataclass in src/shelf_monitor/core/detector.py
- [ ] T026 [P] [US1] Create GapRegion dataclass in src/shelf_monitor/core/detector.py
- [ ] T027 [US1] Implement ProductDetector.__init__() with Azure Custom Vision client
- [ ] T028 [US1] Upload 2,800 training images to Custom Vision project "OOS Detection" (use stratified random sample from SKU-110K train set, maintaining category distribution)
- [ ] T029 [US1] Train Custom Vision model (Iteration 1 with first 500 images from uploaded set)
- [ ] T030 [US1] Evaluate Custom Vision Iteration 1 and document metrics
- [ ] T031 [US1] Train Iteration 2-3 incrementally (1,500 → 2,800 images)
- [ ] T032 [US1] Publish Custom Vision iteration for prediction endpoint
- [ ] T033 [US1] Implement ProductDetector.detect_products() with retry logic (3x exponential backoff)
- [ ] T034 [P] [US1] Implement ProductDetector.detect_gaps() algorithm (sort by x, compute gaps, flag >100px)
- [ ] T035 [P] [US1] Create Azure Custom Vision service wrapper in src/shelf_monitor/services/azure_custom_vision.py
- [ ] T036 [P] [US1] Implement analysis router in src/shelf_monitor/api/routers/analysis.py (POST /detect with synchronous blocking processing for Phase 1)
- [ ] T037 [P] [US1] Create detections router in src/shelf_monitor/api/routers/detections.py (GET /detections)
- [ ] T038 [US1] Implement analysis job submission workflow (save image, create AnalysisJob, queue processing)
- [ ] T039 [US1] Implement ML processing task (detect products, detect gaps, save Detection records)
- [ ] T040 [P] [US1] Create unit tests in tests/unit/test_detector.py for gap detection logic
- [ ] T041 [P] [US1] Create integration tests in tests/integration/test_api_analysis.py for /detect endpoint
- [ ] T042 [P] [US1] Create Jupyter notebook notebooks/01_out_of_stock_detection.ipynb with 5 sections
- [ ] T043 [US1] Write implementation guide docs/guides/challenge_1_oos_detection.md (What/Why/How/Usage)
- [ ] T044 [US1] Run tests and verify Precision >90%, Recall >85% on test set
- [ ] T045 [US1] Commit Challenge 1 implementation with descriptive message

**Parallel Opportunities**:
- T025-T026 (dataclasses) + T035 (Azure service) + T036-T037 (API routers) can run concurrently
- T040-T042 (tests + notebook) can run after T034 (core logic complete)

---

## Phase 3: User Story 2 - Product Recognition (Challenge 2)

**User Story**: As a store manager, I want to identify specific products on shelves so I can track inventory per SKU.

**Acceptance Criteria**:
- YOLOv8s model trained on full SKU-110K dataset (8,233 train images)
- SKU classification accuracy >90%, mAP@0.5 >85%
- Inference speed >10 FPS on GPU (M1/M2 or NVIDIA 6GB+ VRAM)
- API endpoint returns product detections with SKU labels
- Detection results linked to products table via SKU foreign key
- Jupyter notebook compares Azure Custom Vision vs YOLO performance
- Implementation guide documents YOLO training process

**Independent Test Criteria**: Upload shelf image → API returns SKU labels → Database links detections to products → Compare metrics in notebook

### US2 Implementation Tasks

- [ ] T046 [P] [US2] Create SKUClassifier class skeleton in src/shelf_monitor/core/classifier.py
- [ ] T047 [P] [US2] Create YOLOv8 wrapper in src/shelf_monitor/models/yolo.py
- [ ] T048 [US2] Convert SKU-110K annotations from COCO to YOLO format
- [ ] T049 [US2] Create data.yaml configuration for YOLOv8 training
- [ ] T050 [US2] Train YOLOv8s model (50 epochs, batch 16, pretrained COCO weights)
- [ ] T051 [US2] Monitor training progress and save checkpoints every 10 epochs
- [ ] T052 [US2] Evaluate YOLOv8 model on test set (mAP@0.5, inference FPS)
- [ ] T053 [US2] Implement SKUClassifier.classify_products() using YOLOv8 model
- [ ] T054 [P] [US2] Implement SKUClassifier.evaluate_model() for metrics calculation
- [ ] T055 [US2] Upload 1,200 images to Custom Vision project "Product Recognition"
- [ ] T056 [US2] Train Custom Vision classifier (Iterations 1-3, incremental)
- [ ] T057 [US2] Compare Custom Vision vs YOLO performance (accuracy, speed, cost)
- [ ] T058 [P] [US2] Update analysis router to support PRODUCT_RECOGNITION challenge type
- [ ] T059 [US2] Implement SKU classification workflow (classify → link to products table → save Detection)
- [ ] T060 [P] [US2] Create unit tests in tests/unit/test_classifier.py for classification logic
- [ ] T061 [P] [US2] Create integration tests for product recognition API endpoint
- [ ] T062 [P] [US2] Create Jupyter notebook notebooks/02_product_recognition.ipynb with YOLO training + comparison
- [ ] T063 [US2] Write implementation guide docs/guides/challenge_2_product_recognition.md
- [ ] T064 [US2] Write YOLO training guide docs/guides/yolo_training.md
- [ ] T065 [US2] Run tests and verify mAP@0.5 >85%, accuracy >90%
- [ ] T066 [US2] Commit Challenge 2 implementation

**Parallel Opportunities**:
- T046-T047 (class skeletons) + T048-T049 (data prep) can start immediately
- T055-T056 (Custom Vision) parallel to T050-T052 (YOLO training)
- T060-T062 (tests + notebook) parallel after T053 complete

**Dependencies**: T058-T059 depend on T053 (classifier implementation)

---

## Phase 4: User Story 3 - Stock Level Estimation (Challenge 3)

**User Story**: As a store manager, I want to know product quantities on shelves so I can plan restocking schedules.

**Acceptance Criteria**:
- Stock counting algorithm aggregates detections per SKU
- Count accuracy >90%, MAPE <15%
- Depth estimation heuristic (Phase 1: depth=1, Phase 2+: analyze heights)
- API endpoint returns product counts from analysis job
- Database query aggregates detections by SKU efficiently
- Jupyter notebook demonstrates counting logic and trend tracking
- Implementation guide explains aggregation algorithms

**Independent Test Criteria**: Submit analysis → API returns counts per SKU → Database aggregation query matches → Notebook visualizes stock levels

### US3 Implementation Tasks

- [ ] T067 [P] [US3] Create ProductCount dataclass in src/shelf_monitor/core/stock_analyzer.py
- [ ] T068 [P] [US3] Create StockAnalyzer class in src/shelf_monitor/core/stock_analyzer.py
- [ ] T069 [P] [US3] Implement StockAnalyzer.count_products() (group by SKU, count occurrences)
- [ ] T070 [P] [US3] Implement StockAnalyzer.estimate_depth() (Phase 1: return 1)
- [ ] T071 [P] [US3] Create database query in crud.py to aggregate detections by SKU
- [ ] T072 [US3] Update analysis router to support STOCK_ESTIMATION challenge type
- [ ] T073 [US3] Implement stock estimation workflow (classify → count → save aggregated results)
- [ ] T074 [P] [US3] Create unit tests in tests/unit/test_stock_analyzer.py for counting logic
- [ ] T075 [P] [US3] Create integration tests for stock estimation API endpoint
- [ ] T076 [P] [US3] Create Jupyter notebook notebooks/03_stock_level_estimation.ipynb with counting demo
- [ ] T077 [US3] Write implementation guide docs/guides/challenge_3_stock_estimation.md
- [ ] T078 [US3] Run tests and verify count accuracy >90%, MAPE <15%
- [ ] T079 [US3] Commit Challenge 3 implementation

**Parallel Opportunities**:
- T067-T070 (core logic) all parallelizable (different methods)
- T074-T076 (tests + notebook) parallel after T069-T070 complete

**Dependencies**: T072-T073 depend on Challenge 2 (need SKU classifications)

---

## Phase 5: User Story 4 - Price Tag Verification (Challenge 4)

**User Story**: As a store manager, I want to verify price tags match expected prices so I can avoid customer complaints and fines.

**Acceptance Criteria**:
- Azure Document Intelligence Read API extracts text from price tags
- Price parsing regex handles multiple formats ($X.XX, €X,XX, £X.XX)
- OCR confidence threshold >0.8 for accepted prices
- Price history tracked over time in price_history table
- API endpoint returns price verification results
- Jupyter notebook demonstrates OCR + parsing + database tracking
- Implementation guide explains regex patterns and confidence filtering

**Independent Test Criteria**: Upload image with price tags → API extracts prices → Database stores in price_history → Notebook shows parsing accuracy >90%

### US4 Implementation Tasks

- [ ] T080 [P] [US4] Create PriceTag dataclass in src/shelf_monitor/core/ocr.py
- [ ] T081 [P] [US4] Create PriceOCR class in src/shelf_monitor/core/ocr.py
- [ ] T082 [P] [US4] Implement PriceOCR.__init__() with Document Intelligence client
- [ ] T083 [P] [US4] Implement PriceOCR.extract_prices() with retry logic (rate limit handling)
- [ ] T084 [P] [US4] Implement PriceOCR.parse_price() with regex patterns for $, €, £
- [ ] T085 [P] [US4] Create Azure Document Intelligence service wrapper in src/shelf_monitor/services/azure_document_intelligence.py
- [ ] T086 [P] [US4] Create CRUD operations for price_history table in crud.py
- [ ] T087 [US4] Update analysis router to support PRICE_VERIFICATION challenge type
- [ ] T088 [US4] Implement price verification workflow (OCR → parse → compare → save price_history)
- [ ] T089 [P] [US4] Create unit tests in tests/unit/test_ocr.py for price parsing logic
- [ ] T090 [P] [US4] Create integration tests for price verification API endpoint
- [ ] T091 [P] [US4] Create Jupyter notebook notebooks/04_price_tag_verification.ipynb with OCR demo
- [ ] T092 [US4] Write implementation guide docs/guides/challenge_4_price_verification.md
- [ ] T093 [US4] Run tests and verify OCR accuracy >95%, price extraction >90%
- [ ] T094 [US4] Commit Challenge 4 implementation

**Parallel Opportunities**:
- T080-T085 (core logic) all parallelizable (dataclass, OCR, parsing separate)
- T089-T091 (tests + notebook) parallel after T083-T084 complete

**Dependencies**: T087-T088 depend on T083-T084 (OCR + parsing logic)

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Complete API endpoints, testing infrastructure, documentation, and production-ready features.

### API Completion Tasks

- [ ] T095 [P] Create products router in src/shelf_monitor/api/routers/products.py (5 endpoints)
- [ ] T096 [P] Implement POST /api/v1/products (create product)
- [ ] T097 [P] Implement GET /api/v1/products (list with pagination)
- [ ] T098 [P] Implement GET /api/v1/products/{sku} (get by SKU)
- [ ] T099 [P] Implement PUT /api/v1/products/{sku} (update product)
- [ ] T100 [P] Implement DELETE /api/v1/products/{sku} (delete product)
- [ ] T101 [P] Create integration tests in tests/integration/test_api_products.py for all product endpoints
- [ ] T102 [P] Create integration tests in tests/integration/test_database_crud.py for CRUD operations

### Testing Infrastructure

- [ ] T103 [P] Set up pytest configuration in pytest.ini with coverage settings
- [ ] T104 [P] Create conftest.py with test database fixtures (SQLite in-memory)
- [ ] T105 [P] Create FastAPI TestClient fixture for API tests
- [ ] T106 Run full test suite and verify >70% coverage for core/ and api/ modules
- [ ] T107 Fix any failing tests and improve coverage for critical paths

### Documentation Completion

- [ ] T108 [P] Write Azure setup guide docs/guides/azure_setup.md (resource creation, API keys)
- [ ] T109 [P] Write database design guide docs/guides/database_design.md (schema, SQL queries, migrations)
- [ ] T110 [P] Write API development guide docs/guides/api_development.md (FastAPI patterns, Pydantic, dependencies)
- [ ] T111 Update README.md with quickstart instructions and project overview
- [ ] T112 Create docs/ARCHITECTURE.md with full-stack architecture diagram
- [ ] T113 Review all 4 challenge notebooks for clarity and educational value

### Production Features (Optional - Week 11-12)

- [ ] T114 [P] Implement quota monitoring in azure_custom_vision.py (warn at 80% usage)
- [ ] T115 [P] Add structured logging to file (logs/app.log) with rotation
- [ ] T116 [P] Create image validation utilities in src/shelf_monitor/utils/image.py
- [ ] T117 Implement background job processing for async analysis (optional: Celery)
- [ ] T118 Add Azure ML pipeline for model retraining (optional: MLOps)
- [ ] T119 Deploy model to Azure Container Instances for inference (optional)

### Final Validation

- [ ] T120 Run all 4 notebooks end-to-end and verify outputs
- [ ] T121 Test all API endpoints via Swagger UI (/docs)
- [ ] T122 Verify database migrations work (alembic downgrade -1, upgrade head)
- [ ] T123 Review code quality: PEP 8, type hints, docstrings, <50 LOC functions
- [ ] T124 Check educational error messages (what + why + fix format)
- [ ] T125 Verify all 8 implementation guides complete (6 ML + azure_setup + database_design + api_development)
- [ ] T126 Final commit: "Complete retail shelf monitoring learning project"

---

## Dependencies Summary

### Story Completion Order

```
Setup (T001-T008)
  ↓
Foundational (T009-T024) [BLOCKING - must complete before user stories]
  ↓
User Story 1 (T025-T045) [MVP - Out-of-Stock Detection]
  ↓
User Story 2 (T046-T066) [Product Recognition - depends on US1 database schema]
  ↓
User Story 3 (T067-T079) [Stock Estimation - depends on US2 classifications]
  ↓
User Story 4 (T080-T094) [Price Verification - independent, can run parallel to US3]
  ↓
Polish (T095-T126) [Cross-cutting concerns after all stories complete]
```

### Critical Path

The minimum viable product (MVP) requires:
1. **Setup** (T001-T008): 1 week
2. **Foundational** (T009-T024): 1-2 weeks
3. **User Story 1** (T025-T045): 2 weeks

**MVP Timeline**: 4-5 weeks for working out-of-stock detection with database persistence and API.

Full project completion: 12 weeks (includes all 4 challenges + backend + documentation).

---

## Parallel Execution Examples

### During User Story 1 (Challenge 1)

**Parallel Set 1** (after T027 complete):
```
Terminal 1: T028-T032 (Custom Vision training - 5 iterations, ~2-3 hours)
Terminal 2: T034 (Gap detection algorithm implementation)
Terminal 3: T035 (Azure service wrapper)
Terminal 4: T036-T037 (API routers)
```

**Parallel Set 2** (after T034 complete):
```
Terminal 1: T040 (Unit tests for gap detection)
Terminal 2: T041 (Integration tests for API)
Terminal 3: T042 (Jupyter notebook creation)
Terminal 4: T043 (Implementation guide documentation)
```

### During User Story 2 (Challenge 2)

**Parallel Set 1** (after data prep T048-T049):
```
Terminal 1: T050-T052 (YOLO training - 2-4 hours GPU)
Terminal 2: T055-T056 (Custom Vision training - 1-2 hours)
Terminal 3: T046-T047 (Classifier class skeleton + wrapper)
```

**Parallel Set 2** (after T053 complete):
```
Terminal 1: T060 (Unit tests)
Terminal 2: T061 (Integration tests)
Terminal 3: T062 (Jupyter notebook)
Terminal 4: T063-T064 (Documentation guides)
```

### During Polish Phase

**Parallel Set** (T095-T110 all independent):
```
Terminal 1: T095-T100 (Products API endpoints)
Terminal 2: T108 (Azure setup guide)
Terminal 3: T109 (Database design guide)
Terminal 4: T110 (API development guide)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

For fastest time-to-value:
1. Complete T001-T024 (Setup + Foundational) - **2 weeks**
2. Complete T025-T045 (User Story 1) - **2 weeks**
3. Deploy and test MVP - **4 weeks total**

This delivers:
- Working out-of-stock detection
- Database persistence
- REST API
- Jupyter notebook demo
- Full documentation

### Incremental Delivery (All User Stories)

For complete learning experience:
1. Weeks 1-2: Setup + Foundational (T001-T024)
2. Weeks 3-4: User Story 1 (T025-T045)
3. Weeks 5-6: User Story 2 (T046-T066)
4. Weeks 7-8: User Story 3 + 4 (T067-T094) [parallel where possible]
5. Weeks 9-10: Polish + Testing (T095-T119)
6. Weeks 11-12: MLOps + Final Polish (T120-T126)

Each user story is independently testable at completion.

---

## Task Statistics

**Total Tasks**: 126

**By Phase**:
- Setup: 8 tasks (T001-T008)
- Foundational: 16 tasks (T009-T024)
- User Story 1: 21 tasks (T025-T045)
- User Story 2: 21 tasks (T046-T066)
- User Story 3: 13 tasks (T067-T079)
- User Story 4: 15 tasks (T080-T094)
- Polish: 32 tasks (T095-T126)

**Parallelizable Tasks**: ~60 tasks (48%) marked with [P]

**Independent User Stories**: 4 (Challenge 1-4), each with its own test criteria

**Estimated Duration**: 12 weeks (10 weeks ML + 2 weeks backend/polish)

---

## Success Criteria Mapping

| User Story | Tasks | Test Criteria | Metrics |
|------------|-------|---------------|---------|
| **US1: OOS Detection** | T025-T045 | Upload image → API returns gaps → DB contains results | Precision >90%, Recall >85% |
| **US2: Product Recognition** | T046-T066 | Upload image → API returns SKUs → DB links to products | mAP@0.5 >85%, Accuracy >90% |
| **US3: Stock Estimation** | T067-T079 | Submit analysis → API returns counts → DB aggregates | Count accuracy >90%, MAPE <15% |
| **US4: Price Verification** | T080-T094 | Upload image → API extracts prices → DB tracks history | OCR >95%, Extraction >90% |

---

## Notes

- **Database-First**: Complete T009-T018 (database setup) before any ML implementation
- **API Parallel to ML**: Implement API endpoints (T036-T037, T058, T072, T087) alongside ML modules
- **Sequential User Stories**: Complete each user story fully before next (prevents half-finished features)
- **Educational Focus**: Write documentation (T043, T063, T077, T092, T108-T110) immediately after implementation
- **Testing Pragmatism**: Unit tests for pure logic, integration tests for API, mock Azure calls
- **Constitution Compliance**: Keep functions <50 LOC, use type hints, educational error messages

**Status**: ✅ Task breakdown complete. Ready for implementation.

**Next Action**: Start with T001 (virtual environment setup) and work sequentially through Setup phase.
