name: Feature / Task
description: Tạo issue mới cho feature hoặc task trong dự án
labels: ["status:backlog"]
body:
  - type: textarea
    id: context
    attributes:
      label: "1) Bối cảnh"
      description: Mô tả bối cảnh và lý do cần task này
      placeholder: "Giai đoạn Foundation cần chuẩn hóa..."
    validations:
      required: true

  - type: textarea
    id: goal
    attributes:
      label: "2) Mục tiêu"
      description: Mục tiêu cụ thể cần đạt được
      placeholder: "- Thiết lập...\n- Chuẩn hóa...\n- Tối ưu..."
    validations:
      required: true

  - type: textarea
    id: scope
    attributes:
      label: "3) Phạm vi"
      description: Chi tiết in-scope và out-of-scope
      value: |
        ### In-scope
        -

        ### Out-of-scope
        -
    validations:
      required: true

  - type: textarea
    id: deliverables
    attributes:
      label: "4) Deliverables"
      description: Các artifact cần bàn giao
      placeholder: "- [ ] File/module 1\n- [ ] Tài liệu 2\n- [ ] Test 3"
    validations:
      required: true

  - type: textarea
    id: acceptance
    attributes:
      label: "5) Acceptance Criteria"
      description: Tiêu chí chấp nhận — phải measurable
      placeholder: "- [ ] AC 1: ...\n- [ ] AC 2: ...\n- [ ] AC 3: ..."
    validations:
      required: true

  - type: textarea
    id: risks
    attributes:
      label: "6) Rủi ro & kiểm soát"
      description: Rủi ro tiềm ẩn và cách kiểm soát
      value: |
        - **Rủi ro:** ...
          - **Kiểm soát:** ...
    validations:
      required: false

  - type: textarea
    id: dod
    attributes:
      label: "7) Definition of Done"
      description: Tiêu chí hoàn thành cuối cùng
      value: |
        - [ ] AC đạt đủ.
        - [ ] Tài liệu liên quan cập nhật.
        - [ ] Được review và approved bởi owner Epic.
    validations:
      required: true

  - type: dropdown
    id: epic
    attributes:
      label: Epic
      description: Epic nào task này thuộc về?
      options:
        - A - Setup & Governance
        - B - Data Readiness
        - C - RAG Text Pipeline
        - D - Vision/OCR Pipeline
        - E - Integration & Quality
        - F - QA & Hardening
    validations:
      required: true

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      options:
        - P0 - Must do now
        - P1 - Should do this sprint
        - P2 - Normal
        - P3 - Nice to have
    validations:
      required: true

  - type: dropdown
    id: estimate
    attributes:
      label: Estimate
      options:
        - "2h"
        - "4h"
        - "8h"
        - "16h"
        - "24h"
    validations:
      required: true

  - type: dropdown
    id: owner
    attributes:
      label: Owner
      options:
        - Đạt
        - Team
    validations:
      required: true