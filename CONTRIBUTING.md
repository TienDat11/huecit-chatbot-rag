# Contributing Guide — HueCIT Chatbot RAG

## Quy trình làm việc

### 1. Tạo Branch
```bash
# Từ main, tạo branch mới
git checkout main
git pull origin main
git checkout -b feature/<issue-number>-<short-description>
# Ví dụ: feature/A1-repo-structure
```

### 2. Phát triển
- Code theo chuẩn trong `pyproject.toml` (black, isort, flake8)
- Viết tests cho mọi module mới
- Chạy `make check` trước khi commit

### 3. Commit
```bash
# Commit message format:
# <type>(<scope>): <description>
# Ví dụ:
# feat(week1): add document quality scorer
# fix(chunking): fix token overlap calculation
# docs(setup): update REPO_STRUCTURE.md

git add <specific-files>
git commit -m "type(scope): description"
```

### 4. Push & PR
```bash
git push origin feature/<branch-name>
# Tạo PR trên GitHub sử dụng PR template
```

## Quy ước Code

### Formatting
- **Black**: auto-format, line-length = 100
- **isort**: import sorting, profile = black
- **flake8**: linting, max-line-length = 100

### Naming
- Files: `snake_case.py`
- Tests: `test_<module>.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Commits
| Type | Mô tả |
|------|--------|
| `feat` | Tính năng mới |
| `fix` | Bug fix |
| `refactor` | Tái cấu trúc |
| `docs` | Tài liệu |
| `test` | Tests |
| `chore` | Tooling/infra |
| `perf` | Tối ưu |

### Branch Naming
- Feature: `feature/<issue>-<description>`
- Fix: `fix/<issue>-<description>`
- Release: `release/v<version>`

## Quality Commands

```bash
make format    # Format code
make lint      # Run linting
make type      # Type checking
make test      # Run tests
make check     # All quality checks
make security  # Security scan
```

## Cấu trúc Project

Xem chi tiết tại [docs/REPO_STRUCTURE.md](docs/REPO_STRUCTURE.md).

## Labels

| Label | Ý nghĩa |
|-------|---------|
| `epic:A-F` | Thuộc Epic nào |
| `priority:P0-P3` | Mức ưu tiên |
| `type:bug/feat/docs/test/infra` | Loại công việc |
| `status:backlog/in-progress/review/done` | Trạng thái |
| `owner:dat` | Người phụ trách |
| `estimate:2h-24h` | Ước lượng effort |

## Review Process

1. Tất cả PR cần ít nhất 1 review
2. Pre-commit hooks phải pass
3. Tests phải pass
4. Không merge nếu có conversation mở
5. Squash merge cho feature branches

## Troubleshooting

### Pre-commit fails
```bash
# Auto-fix
pre-commit run --all-files

# Skip hooks (KHÔNG khuyến nghị)
git commit --no-verify
```

### Tests fail
```bash
# Chạy test cụ thể
pytest tests/week1/test_quality_scorer.py -v -k "test_name"

# Chạy với output chi tiết
pytest tests/ -v --tb=long
```