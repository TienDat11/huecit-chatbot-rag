from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from src.core.schema_validator import SCHEMAS_DIR, validate_batch, validate_query, validate_screenshot

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
BENCHMARK_DIR = DATA_DIR / "benchmark_inputs"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
RAW_DIR = SCREENSHOTS_DIR / "raw"
CATALOG_DIR = SCREENSHOTS_DIR / "catalog"
PROCESSED_BASIC_DIR = SCREENSHOTS_DIR / "processed" / "basic"
PROCESSED_ENHANCED_DIR = SCREENSHOTS_DIR / "processed" / "enhanced"
SAMPLE_DOCS_CATALOG = DATA_DIR / "sample_documents" / "catalog.json"


DOC_BLUEPRINTS = [
    {
        "domain_id": "D1",
        "doc_id": "doc-D1_authentication_login",
        "function_area": "login",
        "queries": [
            ("procedural", "easy", "Làm thế nào để đăng nhập vào hệ thống CIT?", "Mở cổng truy cập, nhập tài khoản nội bộ hoặc SSO rồi đăng nhập thành công sẽ vào dashboard."),
            ("diagnostic", "medium", "Khi đăng nhập sai nhiều lần thì cần kiểm tra điều gì?", "Cần kiểm tra failed login attempts, nguy cơ brute force và xem tài khoản có bị khóa hay không."),
            ("factual", "easy", "MFA bắt buộc cho những trường hợp nào?", "MFA bắt buộc cho tài khoản Admin, truy cập từ IP lạ và các thao tác nhạy cảm."),
            ("procedural", "medium", "Cách xử lý khi người dùng quên mật khẩu là gì?", "Yêu cầu reset mật khẩu theo quy trình hệ thống và áp dụng chính sách mật khẩu mạnh hiện hành."),
            ("diagnostic", "hard", "Nếu gặp lỗi INVALID_CREDENTIALS liên tục thì nên loại trừ các nguyên nhân nào?", "Cần kiểm tra thông tin đăng nhập, trạng thái tài khoản, lịch sử đổi mật khẩu và khả năng khóa do nhập sai nhiều lần."),
            ("factual", "easy", "Mật khẩu mạnh tối thiểu phải có gì?", "Ít nhất 8 ký tự, gồm chữ hoa, chữ thường và số; khuyến nghị thêm ký tự đặc biệt."),
            ("procedural", "medium", "Làm sao để bật TOTP cho tài khoản quản trị?", "Vào thiết lập bảo mật tài khoản và đăng ký ứng dụng TOTP như Google Authenticator hoặc Authy."),
            ("diagnostic", "medium", "Khi đăng nhập từ IP lạ thì hệ thống yêu cầu gì thêm?", "Hệ thống sẽ yêu cầu xác thực đa yếu tố để tăng độ an toàn."),
        ],
        "screens": [
            ("error", "LOGIN_FAILED", "Đăng nhập thất bại\nTên đăng nhập hoặc mật khẩu không chính xác."),
            ("info", "MFA_REQUIRED", "Xác thực bổ sung\nVui lòng nhập mã OTP từ ứng dụng xác thực."),
            ("error", "ACCOUNT_LOCKED", "Tài khoản tạm khóa\nBạn đã nhập sai mật khẩu quá số lần cho phép."),
        ],
    },
    {
        "domain_id": "D2",
        "doc_id": "doc-D2_database_connection",
        "function_area": "database",
        "queries": [
            ("diagnostic", "easy", "Nguyên nhân thường gặp của lỗi kết nối cơ sở dữ liệu là gì?", "Thường do timeout, sai cấu hình kết nối, dịch vụ database chưa sẵn sàng hoặc mạng không ổn định."),
            ("procedural", "medium", "Cần kiểm tra gì trước khi restart database service?", "Kiểm tra connectivity, log lỗi, cấu hình credentials và tình trạng tài nguyên máy chủ."),
            ("factual", "easy", "Khi query log có timeout thì điều đó gợi ý điều gì?", "Cho thấy kết nối hoặc truy vấn đang chậm, có thể do mạng, tài nguyên hoặc truy vấn kém tối ưu."),
            ("diagnostic", "hard", "Nếu ứng dụng báo CONNECTION_TIMEOUT nhưng database vẫn chạy thì sao?", "Cần kiểm tra network path, firewall, connection pool, DNS và cấu hình endpoint của ứng dụng."),
            ("procedural", "medium", "Cách ưu tiên khắc phục lỗi DB001 là gì?", "Xác nhận database reachability, kiểm tra cấu hình chuỗi kết nối rồi xem log ứng dụng và log database."),
            ("factual", "easy", "Lỗi timeout kết nối thường ảnh hưởng chức năng nào trước?", "Các chức năng phụ thuộc truy vấn dữ liệu như đăng nhập, tra cứu và ghi nhận giao dịch."),
            ("diagnostic", "medium", "Khi chỉ một nhóm người dùng bị lỗi truy cập dữ liệu thì nên nghĩ đến điều gì?", "Có thể liên quan phân vùng mạng, cấu hình phòng ban, quyền truy cập hoặc cache client."),
            ("procedural", "hard", "Sau khi khôi phục kết nối database cần xác minh gì?", "Cần xác minh truy cập dữ liệu, độ ổn định kết nối, log lỗi mới và các giao dịch quan trọng."),
        ],
        "screens": [
            ("error", "DB001", "Database connection timeout\nKhông thể kết nối tới máy chủ cơ sở dữ liệu."),
            ("error", "DB_AUTH_FAILED", "Xác thực database thất bại\nKiểm tra lại tài khoản kết nối dịch vụ."),
            ("info", "DB_RECOVERED", "Kết nối đã phục hồi\nCác chức năng dữ liệu đang hoạt động bình thường."),
        ],
    },
    {
        "domain_id": "D3",
        "doc_id": "doc-D3_network_config",
        "function_area": "network",
        "queries": [
            ("procedural", "easy", "Cần làm gì đầu tiên khi nghi ngờ lỗi mạng nội bộ?", "Kiểm tra kết nối vật lý, địa chỉ IP, DNS và khả năng truy cập tới các dịch vụ quan trọng."),
            ("diagnostic", "medium", "Nếu portal tải chậm nhưng Internet vẫn dùng được thì sao?", "Cần kiểm tra tuyến mạng nội bộ, DNS nội bộ, proxy hoặc firewall của hệ thống CIT."),
            ("factual", "easy", "Network issue có thể gây ra lỗi gì trên portal?", "Có thể gây PAGE_NOT_LOADING, timeout API, gián đoạn upload và lỗi xác thực phụ trợ."),
            ("diagnostic", "hard", "Khi chỉ truy cập được bằng VPN thì nguyên nhân có thể là gì?", "Có thể do giới hạn IP nội bộ, route sai hoặc cấu hình access policy chỉ cho mạng đã đăng ký."),
            ("procedural", "medium", "Làm sao để kiểm tra DNS trước khi escalate?", "Thử phân giải tên miền dịch vụ, so sánh kết quả giữa máy trạm và máy chủ, rồi kiểm tra cache DNS."),
            ("factual", "easy", "Thiết bị chưa đăng ký có thể bị hạn chế theo cơ chế nào?", "Theo chính sách device-based access control hoặc quy định mạng nội bộ/VPN."),
            ("procedural", "medium", "Nếu phát hiện packet loss cao thì cần xử lý thế nào?", "Xác minh đường truyền, thiết bị mạng trung gian và lập log sự cố trước khi chuyển team hạ tầng."),
            ("diagnostic", "medium", "Khi upload file ngắt quãng theo thời điểm thì nên kiểm tra gì?", "Kiểm tra bandwidth, QoS, proxy timeout và tình trạng quá tải đường truyền."),
        ],
        "screens": [
            ("error", "NETWORK_TIMEOUT", "Không thể tải dữ liệu\nYêu cầu mạng đã hết thời gian chờ."),
            ("error", "DNS_RESOLUTION_FAILED", "Lỗi phân giải tên miền\nKhông tìm thấy máy chủ dịch vụ nội bộ."),
            ("info", "VPN_REQUIRED", "Yêu cầu kết nối VPN\nTài nguyên này chỉ cho phép truy cập từ mạng nội bộ hoặc VPN."),
        ],
    },
    {
        "domain_id": "D4",
        "doc_id": "doc-D4_application_portal",
        "function_area": "portal",
        "queries": [
            ("procedural", "easy", "Muốn tạo task mới trên CIT Portal thì làm như thế nào?", "Vào Tasks > Create New Task, nhập thông tin bắt buộc rồi nhấn Create Task."),
            ("factual", "easy", "Portal hỗ trợ upload những định dạng tài liệu nào?", "Hỗ trợ PDF, DOCX, XLSX, PNG và JPG."),
            ("diagnostic", "medium", "Lỗi PAGE_NOT_LOADING thường do đâu?", "Thường do cache trình duyệt hoặc sự cố mạng."),
            ("procedural", "easy", "Khắc phục UPLOAD_FAILED như thế nào?", "Kiểm tra kích thước file dưới 50MB và đúng định dạng được hỗ trợ."),
            ("diagnostic", "medium", "PERMISSION_DENIED trên portal nên xử lý ra sao?", "Xác nhận quyền tài nguyên và liên hệ admin nếu cần cấp quyền phù hợp."),
            ("factual", "easy", "Dashboard hiển thị những widget chính nào?", "My Tasks, Overdue Tasks, Recent Activity và Quick Stats."),
            ("procedural", "medium", "Muốn tạo báo cáo tùy chỉnh cần đi qua các bước nào?", "Vào Reports > Custom Report, chọn loại dữ liệu, thời gian, loại biểu đồ rồi generate và export."),
            ("diagnostic", "hard", "Nếu upload đúng định dạng nhưng vẫn thất bại thì nên kiểm tra gì thêm?", "Kiểm tra quyền upload, kết nối mạng, session hiện tại và log phía máy chủ."),
        ],
        "screens": [
            ("error", "PAGE_NOT_LOADING", "Trang không thể tải\nVui lòng kiểm tra cache trình duyệt và kết nối mạng."),
            ("error", "UPLOAD_FAILED", "Tải tệp thất bại\nFile vượt quá giới hạn hoặc định dạng không được hỗ trợ."),
            ("error", "PERMISSION_DENIED", "Không có quyền truy cập\nLiên hệ quản trị viên để được cấp quyền phù hợp."),
        ],
    },
    {
        "domain_id": "D5",
        "doc_id": "doc-D5_filesystem_management",
        "function_area": "filesystem",
        "queries": [
            ("procedural", "easy", "Khi người dùng không tìm thấy tệp đã upload thì kiểm tra gì trước?", "Kiểm tra thư mục đích, bộ lọc hiển thị, quyền truy cập và lịch sử upload gần đây."),
            ("diagnostic", "medium", "Lỗi đọc thư mục thường liên quan yếu tố nào?", "Có thể do quyền hệ thống tệp, đường dẫn sai, tệp bị khóa hoặc storage không sẵn sàng."),
            ("factual", "easy", "Quản lý tệp tin thường gắn với những quyền nào?", "Quyền xem, upload, download, chia sẻ, sửa và xóa theo phạm vi tài nguyên."),
            ("procedural", "medium", "Cần làm gì khi phát hiện tệp bị upload nhầm thư mục?", "Di chuyển hoặc phân loại lại theo quy trình, đồng thời rà soát phân quyền để tránh lặp lại."),
            ("diagnostic", "hard", "Nếu chỉ tải xuống thất bại với file lớn thì sao?", "Cần kiểm tra giới hạn kích thước, timeout, storage backend và băng thông mạng."),
            ("procedural", "medium", "Cách xử lý khi tên file chứa ký tự lạ gây lỗi là gì?", "Chuẩn hóa tên tệp, kiểm tra encoding và thử upload lại với tên tệp đơn giản hơn."),
            ("factual", "easy", "Guest có thể thao tác gì với tài liệu?", "Chỉ có thể xem tài liệu public, không thể tạo, sửa hoặc xóa."),
            ("diagnostic", "medium", "Khi mất quyền truy cập thư mục dùng chung thì cần xác minh gì?", "Cần xác minh nhóm quyền, cấu hình chia sẻ và thay đổi phân quyền gần đây."),
        ],
        "screens": [
            ("error", "FILE_NOT_FOUND", "Không tìm thấy tệp\nTệp có thể đã bị di chuyển hoặc bạn không còn quyền truy cập."),
            ("error", "STORAGE_QUOTA_EXCEEDED", "Dung lượng lưu trữ đã đầy\nKhông thể tải thêm tệp vào thư mục này."),
            ("info", "FILE_SHARED_SUCCESS", "Chia sẻ tệp thành công\nNgười dùng được chọn đã nhận quyền truy cập."),
        ],
    },
    {
        "domain_id": "D6",
        "doc_id": "doc-D6_security_access_control",
        "function_area": "security",
        "queries": [
            ("diagnostic", "easy", "Dấu hiệu của BRUTE_FORCE_ATTACK là gì?", "Nhiều lần đăng nhập thất bại từ cùng IP, dùng nhiều username và có traffic auth bất thường."),
            ("procedural", "medium", "Bước đầu xử lý BRUTE_FORCE_ATTACK là gì?", "Kiểm tra log đăng nhập, block IP tấn công, bật rate limiting và thông báo team security."),
            ("diagnostic", "medium", "Dấu hiệu DATA_LEAK gồm những gì?", "Download số lượng lớn bất thường, truy cập vượt quyền và tần suất API call bất thường."),
            ("procedural", "medium", "Khi nghi ngờ SQL_INJECTION cần làm gì?", "Kiểm tra input validation, đảm bảo parameterized queries, bật WAF rule và review các endpoint liên quan."),
            ("factual", "easy", "RBAC trong hệ thống gồm những vai trò nào?", "Super Admin, Department Admin, Staff và Guest."),
            ("procedural", "hard", "Khi xảy ra DATA_LEAK cần các bước ứng cứu nào?", "Tạm khóa tài khoản nghi ngờ, audit log, đánh giá phạm vi rò rỉ, báo cáo quản lý và đổi mật khẩu liên quan."),
            ("factual", "easy", "Admin logs cần retention bao lâu?", "Admin logs cần được lưu 3 năm."),
            ("diagnostic", "medium", "Nếu phát hiện script tag trong input fields thì nghĩ đến loại tấn công nào?", "Đó là dấu hiệu của XSS_ATTACK và cần áp dụng CSP, sanitize input và output encoding."),
        ],
        "screens": [
            ("error", "BRUTE_FORCE_ATTACK", "Cảnh báo bảo mật\nPhát hiện nhiều lần đăng nhập thất bại từ cùng địa chỉ IP."),
            ("error", "SQL_INJECTION", "Yêu cầu bị chặn\nHệ thống phát hiện mẫu truy vấn không hợp lệ."),
            ("error", "XSS_ATTACK", "Đầu vào không an toàn\nNội dung chứa script hoặc mã không được phép."),
        ],
    },
    {
        "domain_id": "D7",
        "doc_id": "doc-D7_performance_optimization",
        "function_area": "performance",
        "queries": [
            ("diagnostic", "easy", "Khi hệ thống chậm diện rộng thì cần nghĩ đến nhóm nguyên nhân nào?", "Thường là tài nguyên máy chủ, truy vấn chậm, cache kém hiệu quả hoặc tắc nghẽn mạng."),
            ("procedural", "medium", "Nên kiểm tra gì đầu tiên khi phản hồi portal bị chậm?", "Kiểm tra CPU, RAM, I/O, log lỗi ứng dụng và các truy vấn đang tiêu tốn thời gian."),
            ("factual", "easy", "Tối ưu hiệu suất thường tác động trực tiếp tới chỉ số nào?", "Tác động tới thời gian phản hồi, throughput và trải nghiệm người dùng."),
            ("diagnostic", "hard", "Nếu chỉ một chức năng chậm còn phần khác bình thường thì sao?", "Có thể do truy vấn riêng của chức năng đó, logic xử lý chuyên biệt hoặc tài nguyên phụ thuộc bị nghẽn."),
            ("procedural", "medium", "Sau khi tối ưu truy vấn cần xác minh điều gì?", "Xác minh thời gian phản hồi, độ chính xác dữ liệu và tác động tới các chức năng liên quan."),
            ("factual", "easy", "Caching giúp cải thiện điều gì?", "Giảm số lần truy vấn hoặc tính toán lặp lại, từ đó giảm độ trễ và tải hệ thống."),
            ("diagnostic", "medium", "Khi báo cáo cho thấy throughput giảm theo giờ cao điểm thì cần kiểm tra gì?", "Kiểm tra contention tài nguyên, connection pool, giới hạn hạ tầng và mẫu truy cập tải cao."),
            ("procedural", "hard", "Nếu người dùng phản ánh dashboard load chậm kéo dài thì nên xử lý theo thứ tự nào?", "Đo thời gian tải, xác định bottleneck, tối ưu truy vấn hoặc cache rồi giám sát lại sau khi triển khai."),
        ],
        "screens": [
            ("error", "HIGH_LATENCY", "Thời gian phản hồi cao\nHệ thống đang xử lý chậm hơn ngưỡng cho phép."),
            ("error", "QUERY_SLOW", "Truy vấn chậm\nMột hoặc nhiều truy vấn dữ liệu vượt quá thời gian chuẩn."),
            ("info", "CACHE_REFRESHED", "Bộ nhớ đệm đã làm mới\nHiệu suất truy cập dự kiến sẽ được cải thiện."),
        ],
    },
]


def ensure_directories() -> None:
    for directory in [
        BENCHMARK_DIR,
        RAW_DIR,
        CATALOG_DIR,
        PROCESSED_BASIC_DIR,
        PROCESSED_ENHANCED_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)



def load_sample_doc_ids() -> set[str]:
    with SAMPLE_DOCS_CATALOG.open(encoding="utf-8") as file:
        return {item["doc_id"] for item in json.load(file)}



def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()



def wrap_text(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines



def draw_multiline(draw: ImageDraw.ImageDraw, x: int, y: int, lines: list[str], fill: str) -> None:
    line_height = 28
    for index, line in enumerate(lines):
        draw.text((x, y + index * line_height), line, fill=fill)



def create_screenshot_image(domain_id: str, function_area: str, screen_type: str, error_code: str, body: str, output_path: Path) -> None:
    bg_color = {
        "error": "#fff1f2",
        "info": "#eff6ff",
        "success": "#ecfdf5",
    }[screen_type]
    accent = {
        "error": "#dc2626",
        "info": "#2563eb",
        "success": "#16a34a",
    }[screen_type]

    image = Image.new("RGB", (1280, 720), "#f4f7fb")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((80, 70, 1200, 650), radius=24, fill="#ffffff", outline="#dbe4f0", width=3)
    draw.rounded_rectangle((120, 115, 1160, 230), radius=20, fill=bg_color, outline=accent, width=3)
    draw.text((150, 135), f"{domain_id} / {function_area.upper()}", fill="#0f172a")
    draw.text((150, 175), error_code, fill=accent)

    lines = []
    for paragraph in body.splitlines():
        lines.extend(wrap_text(paragraph, 60))
    draw_multiline(draw, 150, 280, lines, fill="#111827")

    draw.rounded_rectangle((150, 540, 360, 600), radius=14, fill=accent)
    draw.text((185, 560), "Xem hướng dẫn xử lý", fill="#ffffff")
    draw.rounded_rectangle((390, 540, 560, 600), radius=14, fill="#e5e7eb")
    draw.text((435, 560), "Đóng", fill="#111827")

    image.save(output_path)



def create_processed_variants(source_path: Path, basic_path: Path, enhanced_path: Path) -> None:
    image = Image.open(source_path)

    basic = image.filter(ImageFilter.SMOOTH_MORE)
    basic = ImageEnhance.Contrast(basic).enhance(1.05)
    basic.save(basic_path)

    enhanced = image.filter(ImageFilter.SHARPEN)
    enhanced = ImageEnhance.Contrast(enhanced).enhance(1.25)
    enhanced = ImageEnhance.Brightness(enhanced).enhance(1.02)
    enhanced.save(enhanced_path)



def load_schema(schema_filename: str) -> dict:
    with (SCHEMAS_DIR / schema_filename).open(encoding="utf-8") as file:
        return json.load(file)



def validate_ocr_entries(entries: list[dict]) -> None:
    schema = load_schema("ocr_ground_truth_schema.json")
    for entry in entries:
        jsonschema.validate(entry, schema)



def write_json(path: Path, payload: object) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")



def build_artifacts() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    valid_doc_ids = load_sample_doc_ids()
    timestamp = now_iso()
    queries: list[dict] = []
    retrieval_mappings: list[dict] = []
    screenshots: list[dict] = []
    ocr_entries: list[dict] = []

    query_counter = 1

    for blueprint in DOC_BLUEPRINTS:
        if blueprint["doc_id"] not in valid_doc_ids:
            raise ValueError(f"Unknown doc_id in blueprint: {blueprint['doc_id']}")

        screen_ids: list[str] = []

        for index, (screen_type, error_code, text) in enumerate(blueprint["screens"], start=1):
            screen_id = f"screen-{blueprint['domain_id'].lower()}-{index:02d}"
            screen_ids.append(screen_id)
            file_name = f"{screen_id}.png"
            raw_relative_path = f"data/screenshots/raw/{file_name}"
            raw_output_path = RAW_DIR / file_name
            basic_output_path = PROCESSED_BASIC_DIR / file_name
            enhanced_output_path = PROCESSED_ENHANCED_DIR / file_name

            create_screenshot_image(
                blueprint["domain_id"],
                blueprint["function_area"],
                screen_type,
                error_code,
                text,
                raw_output_path,
            )
            create_processed_variants(raw_output_path, basic_output_path, enhanced_output_path)

            screenshots.append(
                {
                    "screen_id": screen_id,
                    "doc_id": blueprint["doc_id"],
                    "screen_type": screen_type,
                    "domain_id": blueprint["domain_id"],
                    "function_area": blueprint["function_area"],
                    "error_codes": [error_code],
                    "screen_context": text.splitlines()[0],
                    "source_path": raw_relative_path,
                    "ocr_ready": True,
                    "annotation_status": "complete",
                    "preprocessing_pipeline": "enhanced",
                    "blur_score": 92,
                    "contrast_score": 90,
                    "ocr_readiness": "ready",
                    "created_at": timestamp,
                }
            )

            ocr_entries.append(
                {
                    "screen_id": screen_id,
                    "ground_truth_text": text,
                    "annotator": "Claude Code",
                    "language": "vi",
                    "text_regions": [
                        {
                            "region_id": f"{screen_id}-header",
                            "bbox": [150, 135, 500, 40],
                            "text": f"{blueprint['domain_id']} / {blueprint['function_area'].upper()}",
                            "region_type": "label",
                        },
                        {
                            "region_id": f"{screen_id}-code",
                            "bbox": [150, 175, 400, 36],
                            "text": error_code,
                            "region_type": "code",
                        },
                        {
                            "region_id": f"{screen_id}-body",
                            "bbox": [150, 280, 820, 180],
                            "text": text,
                            "region_type": "error_message" if screen_type == "error" else "text",
                        },
                    ],
                    "created_at": timestamp,
                }
            )

        for query_type, difficulty, query_text, expected_answer in blueprint["queries"]:
            query_id = f"q-{query_counter:03d}"
            reference_screen_ids = [screen_ids[0]] if query_type == "diagnostic" else []
            queries.append(
                {
                    "query_id": query_id,
                    "query_text": query_text,
                    "query_type": query_type,
                    "difficulty": difficulty,
                    "domain_id": blueprint["domain_id"],
                    "function_area": blueprint["function_area"],
                    "expected_answer": expected_answer,
                    "reference_doc_ids": [blueprint["doc_id"]],
                    "reference_screen_ids": reference_screen_ids,
                    "created_at": timestamp,
                }
            )
            retrieval_mappings.append(
                {
                    "query_id": query_id,
                    "relevant_doc_ids": [blueprint["doc_id"]],
                    "relevant_screen_ids": reference_screen_ids,
                    "created_at": timestamp,
                }
            )
            query_counter += 1

    return queries, retrieval_mappings, screenshots, ocr_entries



def validate_generated_data(queries: list[dict], screenshots: list[dict], ocr_entries: list[dict]) -> None:
    valid_queries, invalid_queries = validate_batch(queries, validate_query)
    valid_screens, invalid_screens = validate_batch(screenshots, validate_screenshot)

    if invalid_queries:
        raise ValueError(f"Invalid queries generated: {invalid_queries[:2]}")
    if invalid_screens:
        raise ValueError(f"Invalid screenshots generated: {invalid_screens[:2]}")

    if len(valid_queries) != len(queries):
        raise ValueError("Query validation count mismatch")
    if len(valid_screens) != len(screenshots):
        raise ValueError("Screenshot validation count mismatch")

    validate_ocr_entries(ocr_entries)



def main() -> None:
    ensure_directories()
    queries, retrieval_mappings, screenshots, ocr_entries = build_artifacts()
    validate_generated_data(queries, screenshots, ocr_entries)

    write_json(BENCHMARK_DIR / "query_set.json", queries)
    write_json(BENCHMARK_DIR / "ground_truth_retrieval.json", retrieval_mappings)
    write_json(CATALOG_DIR / "catalog.json", screenshots)
    write_json(CATALOG_DIR / "ocr_ground_truth.json", ocr_entries)

    summary = {
        "queries": len(queries),
        "retrieval_mappings": len(retrieval_mappings),
        "screenshots": len(screenshots),
        "ocr_entries": len(ocr_entries),
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
