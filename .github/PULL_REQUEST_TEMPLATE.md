## Mô tả thay đổi

> Mô tả ngắn gọn những gì PR này thay đổi và tại sao.

## Loại thay đổi

- [ ] feat: Tính năng mới
- [ ] fix: Bug fix
- [ ] refactor: Tái cấu trúc không thay đổi logic
- [ ] docs: Thay đổi tài liệu
- [ ] test: Thêm/sửa tests
- [ ] chore: Thay đổi tooling/infra
- [ ] perf: Tối ưu hiệu năng

## Issue liên quan

Closes #<issue_number>

## Acceptance Criteria đạt

- [ ] AC 1: <!-- Mô tả -->
- [ ] AC 2: <!-- Mô tả -->
- [ ] AC 3: <!-- Mô tả -->

## Test Evidence

### Tests chạy thành công
<!-- Paste output của lệnh test -->

```
pytest tests/<path> -v
# Paste output here
```

### Pre-commit pass
```
pre-commit run --all-files
# Paste output here
```

## Impact Scope

### Files thay đổi
<!-- Liệt kê files thay đổi chính -->

### Phạm vi ảnh hưởng
<!-- Module/tính năng nào bị ảnh hưởng? -->

## Rollback Plan

Nếu PR gây regression:
<!-- Mô tả cách revert -->

## Checklist

- [ ] Code tuân thủ quy ước dự án (black, isort, flake8)
- [ ] Tests mới/updated cho thay đổi này
- [ ] Tất cả tests pass
- [ ] Tài liệu liên quan đã cập nhật (nếu có)
- [ ] Không commit dữ liệu nhạy cảm (API keys, credentials)
- [ ] Không commit raw data hoặc output files