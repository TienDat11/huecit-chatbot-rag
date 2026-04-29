name: Bug Report
description: Báo cáo bug hoặc vấn đề trong dự án
labels: ["type:bug", "status:backlog"]
body:
  - type: textarea
    id: description
    attributes:
      label: Mô tả bug
      description: Mô tả rõ bug gặp phải
      placeholder: "Khi chạy lệnh X thì bị lỗi Y..."
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Các bước tái hiện
      description: Danh sách bước để tái hiện bug
      placeholder: |
        1. Chạy lệnh `python src/week1/quality_scorer.py ...`
        2. Xem output...
        3. Thấy lỗi...
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Kết quả kỳ vọng
      description: Kết quả đúng nên là gì
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Kết quả thực tế
      description: Kết quả thực tế gặp phải (kèm error log nếu có)
    validations:
      required: true

  - type: textarea
    id: environment
    attributes:
      label: Môi trường
      description: Thông tin môi trường chạy
      placeholder: |
        - OS: Windows 11
        - Python: 3.9.x
        - Command: ...
    validations:
      required: false

  - type: textarea
    id: fix_suggestion
    attributes:
      label: Đề xuất fix (optional)
      description: Nếu có ý tưởng cách fix, mô tả ở đây
    validations:
      required: false

  - type: dropdown
    id: severity
    attributes:
      label: Severity
      options:
        - Critical - Blocker, không thể tiếp tục
        - High - Ảnh hưởng chức năng chính
        - Medium - Ảnh hưởng chức năng phụ
        - Low - Cosmetic/minor
    validations:
      required: true