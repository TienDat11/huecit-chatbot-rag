# HueCIT Chatbot RAG

Hệ thống chatbot hỗ trợ kỹ thuật vận hành phần mềm sử dụng RAG (Retrieval-Augmented Generation) và phân tích ảnh lỗi.

## Tổng quan

Dự án xây dựng chatbot với hai năng lực chính:
1. **Hỏi đáp văn bản** — Trả lời câu hỏi hướng dẫn sử dụng dựa trên tài liệu nội bộ (RAG pipeline).
2. **Phân tích ảnh lỗi** — Nhận ảnh screenshot lỗi, nhận dạng ngữ cảnh chức năng/lỗi, và đưa hướng dẫn khắc phục.

**Thời gian**: 8 tuần (2 tháng) | **Team**: 2 người

## Quick Start

### Yêu cầu
- Python 3.9+
- 16GB+ RAM
- 50GB+ disk space

### Cài đặt
```bash
# Clone repo
git clone https://github.com/TienDat11/huecit-chatbot-rag.git
cd huecit-chatbot-rag

# Tạo virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Cài pre-commit hooks
pre-commit install
```

### Chạy tests
```bash
# Chạy tất cả tests
make test

# Chạy tests cho tuần cụ thể
pytest tests/week1/ -v
```

### Quality commands
```bash
make lint          # Chạy linting
make format        # Format code
make test          # Chạy tests
make check         # Chạy tất cả checks
```

## Cấu trúc dự án

Xem chi tiết tại [docs/REPO_STRUCTURE.md](docs/REPO_STRUCTURE.md).

```
huecit-chatbot-rag/
├── src/           # Source code (week1-week8)
├── tests/         # Test suite
├── data/          # Dữ liệu đầu vào
├── output/        # Kết quả pipeline
├── notebooks/     # Jupyter notebooks
├── docs/          # Tài liệu
└── scripts/       # Helper scripts
```

## Epics

| Epic | Mô tả | Tuần |
|------|--------|------|
| A | Setup & Governance | 1 |
| B | Data Readiness | 1-2 |
| C | RAG Text Pipeline | 2-3 |
| D | Vision/OCR Pipeline | 4-5 |
| E | Integration & Quality | 6-7 |
| F | QA & Hardening | 7-8 |

## Đóng góp

Xem [CONTRIBUTING.md](CONTRIBUTING.md) để biết quy trình đóng góp.

## License

Internal project — HueCIT 2026