# Contributing Guide — HueCIT Chatbot RAG

## ⚠️ QUAN TRỌNG: Git Workflow Rules

**BẮT BUỘC**: Đọc và tuân thủ [CLAUDE.md](CLAUDE.md) cho quy tắc Git workflow đầy đủ. Tất cả session Claude Code phải tuân thủ các quy tắc này.

### Tóm tắt nhanh
1. **KHÔNG commit trực tiếp vào `main`** — `main` chỉ nhận code từ `develop` khi release EPIC
2. **Branch từ `develop`**, merge ngược lại `develop`
3. **Tối đa 3 commits** (2 work + 1 merge)
4. **Không rebase** trên shared branches
5. **Squash commits** trước khi merge vào `develop`
6. **Branch tuyến tính** — không branch từ branch

---

## Quy trình làm việc

### 1. Tạo Branch từ `develop`

```bash
# ✅ ĐÚNG: Branch từ develop
git checkout develop
git pull origin develop
git checkout -b feature/<issue-number>-<short-description>
# Ví dụ: feature/A1-repo-structure

# ❌ SAI: Branch từ main
# git checkout main  <-- KHÔNG BAO GIỜ
```

### 2. Phát triển

- Code theo chuẩn trong `pyproject.toml` (black, isort, flake8)
- Viết tests cho mọi module mới
- Chạy `make check` trước khi commit
- **Giới hạn commits**: Tối đa 2 meaningful commits

### 3. Commit (Conventional Commits)

```bash
# Commit message format:
# <type>(<scope>): <description>

# Ví dụ:
git commit -m "feat(A1): add document quality scorer"
git commit -m "fix(C3): resolve token overlap in chunker"
git commit -m "docs(setup): update REPO_STRUCTURE.md"
```

| Type | Mô tả |
|------|--------|
| `feat` | Tính năng mới |
| `fix` | Bug fix |
| `refactor` | Tái cấu trúc |
| `docs` | Tài liệu |
| `test` | Tests |
| `chore` | Tooling/infra |
| `perf` | Tối ưu |

### 4. Merge về `develop`

```bash
# Review commits (phải <= 2 commits)
git log --oneline -5

# Nếu > 2 commits, squash:
git rebase -i HEAD~N
# HOẶC
git reset --soft HEAD~N
git commit -m "feat(A1): comprehensive change description"

# Merge to develop
git checkout develop
git pull origin develop
git merge --no-ff feature/A1-repo-structure

# Resolve conflicts nếu có
git add <resolved-files>
git merge --continue

# Push
git push origin develop

# Xóa feature branch
git branch -d feature/A1-repo-structure
git push origin --delete feature/A1-repo-structure
```

### 5. Release EPIC

```bash
# Khi EPIC hoàn thành và tested trên develop
git checkout main
git pull origin main
git merge --no-ff develop -m "release: EPIC X complete"
git tag -a v0.X.0 -m "EPIC X description"
git push origin main --tags
```

---

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

### Branch Naming
| Type | Format | Example |
|------|--------|---------|
| Feature | `feature/<epic>-<desc>` | `feature/A1-repo-structure` |
| Hotfix | `hotfix/<issue>-<desc>` | `hotfix/A1-critical-fix` |
| Release | `release/v<version>` | `release/v0.1.0` |

---

## Quality Commands

```bash
make format    # Format code
make lint      # Run linting
make type      # Type checking
make test      # Run tests
make check     # All quality checks
make security  # Security scan
```

---

## Labels

| Label | Ý nghĩa |
|-------|---------|
| `epic:A-F` | Thuộc Epic nào |
| `priority:P0-P3` | Mức ưu tiên |
| `type:bug/feat/docs/test/infra` | Loại công việc |
| `status:backlog/in-progress/review/done` | Trạng thái |
| `owner:dat` | Người phụ trách |
| `estimate:2h-24h` | Ước lượng effort |

---

## Project Management

### Source of Truth

**GitHub Issues** và **GitHub Projects** là nguồn chân lý cho tracking công việc:

- **GitHub Issues**: Labels (epic, priority, type, owner, estimate)
- **GitHub Projects**: Status tracking (backlog → in-progress → review → done)

### Status Workflow

```
backlog → in-progress → review → done
```

| Status | Mô tả |
|--------|-------|
| `backlog` | Task đã được định nghĩa, chờ assign |
| `in-progress` | Đang thực hiện |
| `review` | Task hoàn thành, chờ review |
| `done` | Task đã được merge/complete |

### Xem/Quản lý Projects

```bash
# Liệt kê Projects
gh project list --owner TienDat11

# Xem items trong Project
gh project view <PROJECT_NUMBER> --owner TienDat11

# Thêm issue vào Project
gh project add-item <PROJECT_NUMBER> --owner TienDat11 --url <ISSUE_URL>
```

### Required Scope

Để sử dụng `gh project` commands, cần authenticate với scope `read:project`:

```bash
# Refresh authentication với scope cần thiết
gh auth refresh -s read:project

# Verify scopes
gh auth status
```

---

## Review Process

1. Tất cả PR cần ít nhất 1 review
2. Pre-commit hooks phải pass
3. Tests phải pass
4. Không merge nếu có conversation mở
5. Squash commits nếu cần trước khi merge

---

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

### Quá nhiều commits trên branch
```bash
# Squash N commits gần nhất
git rebase -i HEAD~N

# HOẶC reset và re-commit
git reset --soft HEAD~N
git commit -m "feat(A1): all changes combined"
```

---

## Tài liệu tham khảo

- [CLAUDE.md](CLAUDE.md) — Quy tắc Git workflow chi tiết (BẮT BUỘC)
- [docs/REPO_STRUCTURE.md](docs/REPO_STRUCTURE.md) — Cấu trúc repository
- [Conventional Commits](https://www.conventionalcommits.org/) — Format commit message