# Hướng dẫn quản lý tệp tin và thư mục

## Tổng quan

Tài liệu mô tả cách quản lý hệ thống tệp tin trong CIT Portal, bao gồm upload, download, phân quyền và backup. Hệ thống sử dụng MinIO làm object storage và hỗ trợ tích hợp với các dịch vụ cloud storage.

## Cấu trúc thư mục

### Thư mục gốc

```
/cit-storage/
├── documents/          # Tài liệu công việc
│   ├── shared/         # Tài liệu chia sẻ
│   ├── templates/      # Mẫu tài liệu
│   └── archive/        # Lưu trữ
├── uploads/            # File upload từ người dùng
│   ├── images/
│   ├── pdfs/
│   └── others/
├── backups/            # Backup tự động
└── temp/               # File tạm thời (auto-delete sau 24h)
```

### Quy ước đặt tên file

- Sử dụng ký tự không dấu hoặc có dấu tiếng Việt
- Không chứa ký tự đặc biệt: \ / : * ? " < > |
- Tối đa 255 ký tự
- Khuyến nghị format: `[Ngày]_[Loại]_[Mô tả].[ext]`
- Ví dụ: `20260429_BC_BaoCaoThang4.pdf`

## Upload tệp tin

### Upload qua Web Interface

1. Vào Documents > Upload
2. Kéo thả file vào khu vực upload hoặc nhấn "Browse"
3. Hệ thống hỗ trợ upload nhiều file cùng lúc (tối đa 20 files)
4. Theo dõi tiến trình upload trên thanh progress

### Giới hạn upload

| Loại file | Kích thước tối đa | Định dạng hỗ trợ |
|-----------|-------------------|-------------------|
| Document | 50 MB | .pdf, .docx, .xlsx, .pptx |
| Image | 20 MB | .jpg, .png, .gif, .svg |
| Video | 500 MB | .mp4, .webm |
| Archive | 100 MB | .zip, .rar, .7z |

### Upload qua API

```bash
# Upload file sử dụng curl
curl -X POST https://portal.cit.hue.edu.vn/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/file.pdf" \
  -F "folder=documents/shared" \
  -F "description=Báo cáo tháng 4"
```

## Download tệp tin

### Download单个 file

1. Nhấp chuột phải vào file > Download
2. Hoặc nhấp vào icon Download ở thanh công cụ
3. File sẽ được download về máy với tên gốc

### Download nhiều file

1. Chọn nhiều file bằng checkbox
2. Nhấn "Download Selected"
3. Hệ thống sẽ nén thành file ZIP để download

### Download qua API

```bash
curl -X GET https://portal.cit.hue.edu.vn/api/files/{file_id}/download \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o downloaded_file.pdf
```

## Quản lý phiên bản

### Versioning

Mỗi khi upload file trùng tên, hệ thống tự động tạo phiên bản mới:
- Version 1.0: File gốc
- Version 1.1: Cập nhật nhỏ (sửa nội dung)
- Version 2.0: Cập nhật lớn (thay đổi cấu trúc)

### Xem lịch sử phiên bản

1. Nhấp chuột phải vào file > Version History
2. Xem danh sách tất cả phiên bản
3. Có thể download hoặc restore phiên bản cũ

## Phân quyền truy cập

### Cấp độ quyền

| Quyền | Mô tả |
|-------|--------|
| Read | Xem và download file |
| Write | Upload, edit, delete |
| Admin | Tất cả quyền + quản lý permissions |

### Thiết lập quyền

1. Nhấp chuột phải vào file/folder > Share
2. Thêm người dùng hoặc nhóm
3. Chọn cấp độ quyền cho từng người
4. Nhấn "Save"

## Lỗi FILE_NOT_FOUND

### Nguyên nhân

- File đã bị xóa hoặc di chuyển
- Đường dẫn không chính xác
- Permission không cho phép xem

### Cách xử lý

1. Kiểm tra thư mục Trash/Recycle Bin
2. Tìm kiếm file theo tên
3. Liên hệ admin nếu cần restore từ backup

## Lỗi STORAGE_FULL

### Nguyên nhân

- Đã vượt quá quota lưu trữ
- File tạm thời chiếm quá nhiều dung lượng

### Cách xử lý

1. Xóa file không cần thiết
2. Dọn dẹp thư mục temp
3. Archive file cũ sang cold storage
4. Yêu cầu admin tăng quota

## Lỗi UPLOAD_SIZE_EXCEEDED

### Nguyên nhân

File vượt quá giới hạn kích thước cho phép.

### Cách xử lý

1. Nén file trước khi upload
2. Chia file lớn thành nhiều phần nhỏ
3. Sử dụng API upload với multipart/form-data cho file > 50MB

## Backup và Recovery

### Backup tự động

- Hệ thống backup hàng ngày lúc 02:00 AM
- Retention: 7 ngày cho daily, 4 tuần cho weekly, 12 tháng cho monthly
- Backup location: `/cit-storage/backups/`

### Restore file

```bash
# Restore file từ backup
curl -X POST https://portal.cit.hue.edu.vn/api/files/restore \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"file_id": "abc123", "version": "1.0"}'
```

## Monitoring

### Metrics quan trọng

- Total storage used vs quota
- Upload/download throughput
- File count by type
- Error rate (upload failures, download failures)
