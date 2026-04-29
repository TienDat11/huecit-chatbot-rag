# HueCIT Chatbot RAG — Cấu trúc Repository

## Tổng quan

Repository được tổ chức theo chuẩn project Python cho hệ thống chatbot hỗ trợ kỹ thuật vận hành phần mềm (RAG + phân tích ảnh lỗi).

## Cấu trúc thư mục

```
huecit-chatbot-rag/
├── src/                          # Source code chính
│   ├── __init__.py
│   ├── core/                     # Core modules (config, logging, types)
│   ├── utils/                    # Utility functions
│   ├── week1/                    # Data Readiness Pipeline
│   │   ├── quality_scorer.py
│   │   ├── fixed_size_chunker.py
│   │   ├── structure_aware_chunker.py
│   │   └── ocr_preprocessing.py
│   ├── week2/                    # Knowledge Foundation
│   ├── week3/                    # Text MVP (RAG E2E)
│   ├── week4/                    # Vision Baseline
│   ├── week5/                    # Image MVP
│   ├── week6/                    # Quality Optimization
│   ├── week7/                    # Hardening
│   └── week8/                    # Demo & Handover
├── tests/                        # Test suite
│   ├── conftest.py               # Shared fixtures
│   ├── week1/                    # Tests cho week 1 modules
│   ├── week2/                    # Tests cho week 2 modules
│   └── ...                       # Tương tự cho các tuần khác
├── data/                         # Dữ liệu đầu vào (KHÔNG commit raw data)
│   ├── documents/
│   │   ├── raw/                  # PDF/DOCX/MD gốc
│   │   ├── processed/            # JSONL đã parse
│   │   └── catalog/              # Document catalog + quality scores
│   ├── screenshots/
│   │   ├── raw/                  # Screenshot gốc
│   │   ├── processed/
│   │   │   ├── basic/            # Basic pipeline output
│   │   │   └── enhanced/         # Enhanced pipeline output
│   │   └── catalog/              # Screenshot catalog
│   ├── schemas/                  # JSON schemas
│   └── benchmark_inputs/         # Input cho benchmark
├── output/                       # Kết quả chạy pipeline
│   └── week_1/                   # Output theo tuần
│       ├── chunking/
│       └── ocr/
├── notebooks/                    # Jupyter notebooks cho benchmark
├── reports/                      # Báo cáo, metrics, ablation studies
├── docs/                         # Tài liệu dự án
├── scripts/                      # Helper scripts
├── .github/                      # GitHub templates và workflows
├── pyproject.toml                # Project metadata và config
├── requirements.txt              # Runtime dependencies
├── requirements-dev.txt          # Dev dependencies
├── Makefile                      # Quality commands
├── .pre-commit-config.yaml       # Pre-commit hooks
├── .editorconfig                 # Editor config
├── .gitignore                    # Git ignore rules
├── CONTRIBUTING.md               # Hướng dẫn đóng góp
└── README.md                     # Tổng quan dự án
```

## Quy ước đặt tên

### File code
- Python modules: `snake_case.py` (ví dụ: `quality_scorer.py`)
- Test files: `test_<module_name>.py` (ví dụ: `test_quality_scorer.py`)
- Config files: lowercase, có dấu chấm (ví dụ: `.pre-commit-config.yaml`)

### File dữ liệu
- JSONL: `<type>_<date>.jsonl` (ví dụ: `docs_2026-04-29.jsonl`)
- CSV: `<type>_<week>.csv` (ví dụ: `metrics_week_1.csv`)
- Schemas: `<type>_schema.json` (ví dụ: `document_metadata_schema.json`)

### File output
- Metrics: `metrics_week_<N>.csv`
- Ablation: `ablation_week_<N>.md`
- Error analysis: `error_analysis_week_<N>.md`

### Thư mục
- Tên thư mục: `snake_case`
- Thư mục tuần: `week<N>` (ví dụ: `week1`, `week2`)

## Quy tắc tổ chức

1. **Mỗi tuần có thư mục riêng** trong `src/` và `tests/`
2. **Dữ liệu raw KHÔNG commit** vào git — chỉ commit schemas và catalogs
3. **Output KHÔNG commit** — thêm vào `.gitignore`
4. **Notebooks** đặt tên: `<STT>_<topic>.ipynb` (ví dụ: `01_rag_retrieval_benchmark.ipynb`)
5. **Shared utilities** đặt trong `src/utils/`, `src/core/`
6. **Test fixtures** đặt trong `tests/conftest/`

## Quick Reference

| Tôi cần... | Vị trí |
|---|---|
| Thêm module tuần N | `src/week<N>/` |
| Thêm test cho module | `tests/week<N>/` |
| Đặt tài liệu gốc | `data/documents/raw/` |
| Đặt ảnh lỗi gốc | `data/screenshots/raw/` |
| Xem kết quả benchmark | `output/week_<N>/` |
| Chạy notebook | `notebooks/` |
| Xem schemas | `data/schemas/` |
