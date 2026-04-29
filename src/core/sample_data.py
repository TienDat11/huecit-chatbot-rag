"""Sample data for testing and development."""

from datetime import datetime, timezone

SAMPLE_DOCUMENTS = [
    {
        "doc_id": "doc-sample-001",
        "title": "Hướng dẫn đăng nhập hệ thống",
        "domain_id": "D1",
        "function_area": "login",
        "source_type": "md",
        "source_path": "data/documents/raw/login_guide.md",
        "language": "vi",
        "parse_status": "success",
        "content": """# Hướng dẫn đăng nhập hệ thống

## Giới thiệu
Tài liệu hướng dẫn quy trình đăng nhập vào hệ thống quản lý.

## Yêu cầu
- Tài khoản đã được kích hoạt
- Mật khẩu hợp lệ
- Trình duyệt hỗ trợ

## Các bước thực hiện

### Bước 1: Truy cập trang đăng nhập
Mở trình duyệt và truy cập địa chỉ hệ thống.

### Bước 2: Nhập thông tin
Nhập tên đăng nhập và mật khẩu vào form.

### Bước 3: Xác thực
Nhấn nút "Đăng nhập" để xác thực.

## Xử lý lỗi thường gặp
- Lỗi SESSION_EXPIRED: Phiên làm việc hết hạn, đăng nhập lại
- Lỗi INVALID_CREDENTIALS: Kiểm tra lại thông tin đăng nhập
- Lỗi ACCOUNT_LOCKED: Tài khoản bị khóa, liên hệ admin""",
        "headings": [
            {"level": 1, "text": "Hướng dẫn đăng nhập hệ thống"},
            {"level": 2, "text": "Giới thiệu"},
            {"level": 2, "text": "Yêu cầu"},
            {"level": 2, "text": "Các bước thực hiện"},
            {"level": 3, "text": "Bước 1: Truy cập trang đăng nhập"},
            {"level": 3, "text": "Bước 2: Nhập thông tin"},
            {"level": 3, "text": "Bước 3: Xác thực"},
            {"level": 2, "text": "Xử lý lỗi thường gặp"},
        ],
        "sections": [
            {"heading_path": "Hướng dẫn đăng nhập hệ thống", "text": "Tài liệu hướng dẫn...", "level": 1},
            {"heading_path": "Hướng dẫn đăng nhập hệ thống > Giới thiệu", "text": "Tài liệu hướng dẫn quy trình đăng nhập vào hệ thống quản lý.", "level": 2},
            {"heading_path": "Hướng dẫn đăng nhập hệ thống > Yêu cầu", "text": "Tài khoản đã được kích hoạt\nMật khẩu hợp lệ\nTrình duyệt hỗ trợ", "level": 2},
            {"heading_path": "Hướng dẫn đăng nhập hệ thống > Các bước thực hiện > Bước 1", "text": "Mở trình duyệt và truy cập địa chỉ hệ thống.", "level": 3},
            {"heading_path": "Hướng dẫn đăng nhập hệ thống > Các bước thực hiện > Bước 2", "text": "Nhập tên đăng nhập và mật khẩu vào form.", "level": 3},
            {"heading_path": "Hướng dẫn đăng nhập hệ thống > Các bước thực hiện > Bước 3", "text": "Nhấn nút Đăng nhập để xác thực.", "level": 3},
            {"heading_path": "Hướng dẫn đăng nhập hệ thống > Xử lý lỗi thường gặp", "text": "Lỗi SESSION_EXPIRED...\nLỗi INVALID_CREDENTIALS...\nLỗi ACCOUNT_LOCKED...", "level": 2},
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "doc_id": "doc-sample-002",
        "title": "Khắc phục lỗi kết nối cơ sở dữ liệu",
        "domain_id": "D2",
        "function_area": "connection",
        "source_type": "pdf",
        "source_path": "data/documents/raw/db_connection_fix.pdf",
        "language": "vi",
        "parse_status": "success",
        "content": """# Khắc phục lỗi kết nối cơ sở dữ liệu

## Tổng quan
Hướng dẫn xử lý các lỗi kết nối database phổ biến.

## Lỗi CONNECTION_TIMEOUT

### Nguyên nhân
- Server database không phản hồi
- Firewall chặn kết nối
- Connection pool đã hết

### Cách xử lý
1. Kiểm tra database service đang chạy
2. Kiểm tra firewall rules
3. Tăng connection pool size

## Lỗi QUERY_FAILED

### Nguyên nhân
- SQL syntax lỗi
- Table không tồn tại
- Permission denied

### Cách xử lý
1. Kiểm tra SQL syntax
2. Verify table exists
3. Check user permissions""",
        "headings": [
            {"level": 1, "text": "Khắc phục lỗi kết nối cơ sở dữ liệu"},
            {"level": 2, "text": "Tổng quan"},
            {"level": 2, "text": "Lỗi CONNECTION_TIMEOUT"},
            {"level": 3, "text": "Nguyên nhân"},
            {"level": 3, "text": "Cách xử lý"},
            {"level": 2, "text": "Lỗi QUERY_FAILED"},
            {"level": 3, "text": "Nguyên nhân"},
            {"level": 3, "text": "Cách xử lý"},
        ],
        "sections": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    },
    {
        "doc_id": "doc-sample-003",
        "title": "",
        "domain_id": "D3",
        "source_type": "md",
        "parse_status": "partial",
        "content": "Nội dung ngắn",
        "headings": [],
        "sections": [],
    },
]

SAMPLE_SCREENSHOTS = [
    {
        "screen_id": "screen-sample-001",
        "doc_id": "doc-sample-001",
        "screen_type": "error",
        "domain_id": "D1",
        "function_area": "login",
        "error_codes": ["LOGIN_FAILED", "INVALID_CREDENTIALS"],
        "screen_context": "Màn hình lỗi khi nhập sai mật khẩu 3 lần",
        "source_path": "data/screenshots/raw/login_error_001.png",
        "ocr_ready": False,
        "annotation_status": "pending",
    },
    {
        "screen_id": "screen-sample-002",
        "doc_id": "doc-sample-002",
        "screen_type": "error",
        "domain_id": "D2",
        "function_area": "connection",
        "error_codes": ["DB001", "CONNECTION_TIMEOUT"],
        "screen_context": "Error page khi database connection timeout",
        "source_path": "data/screenshots/raw/db_timeout_001.png",
        "ocr_ready": False,
        "annotation_status": "pending",
    },
]
