# Hướng dẫn sử dụng ứng dụng CIT Portal

## Giới thiệu

CIT Portal là ứng dụng web quản lý công việc nội bộ dành cho cán bộ nhân viên. Ứng dụng cung cấp các chức năng: quản lý task, báo cáo, giao tiếp nội bộ và quản lý tài liệu.

## Cài đặt và truy cập

### Yêu cầu hệ thống

- Trình duyệt: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Độ phân giải tối thiểu: 1280x720
- JavaScript phải được bật
- Cookies phải được bật

### Truy cập ứng dụng

1. Mở trình duyệt web
2. Truy cập: `https://portal.cit.hue.edu.vn`
3. Đăng nhập bằng tài khoản nội bộ hoặc SSO
4. Trang Dashboard sẽ hiển thị sau khi đăng nhập thành công

## Giao diện chính

### Thanh điều hướng (Navigation Bar)

Thanh điều hướng nằm ở phía trên màn hình bao gồm:
- **Logo CIT:** Nhấp để về trang chủ
- **Dashboard:** Tổng quan công việc
- **Tasks:** Quản lý công việc
- **Documents:** Quản lý tài liệu
- **Reports:** Báo cáo thống kê
- **Settings:** Cài đặt cá nhân
- **User Avatar:** Menu người dùng (Profile, Đổi mật khẩu, Đăng xuất)

### Dashboard

Dashboard hiển thị các widget chính:
- **My Tasks:** Danh sách công việc được giao
- **Overdue Tasks:** Công việc quá hạn (highlight đỏ)
- **Recent Activity:** Hoạt động gần đây
- **Quick Stats:** Thống kê nhanh (tổng tasks, đã hoàn thành, đang thực hiện)

## Quản lý công việc (Tasks)

### Tạo công việc mới

1. Vào Tasks > Create New Task
2. Điền thông tin:
   - Tiêu đề (bắt buộc)
   - Mô tả chi tiết
   - Độ ưu tiên: Low / Medium / High / Critical
   - Người thực hiện
   - Ngày hết hạn
   - Tags
3. Nhấn "Create Task"

### Cập nhật trạng thái

Các trạng thái công việc:
- **To Do:** Chưa bắt đầu
- **In Progress:** Đang thực hiện
- **Review:** Chờ xem xét
- **Done:** Hoàn thành
- **Cancelled:** Đã hủy

### Lọc và tìm kiếm

- Lọc theo trạng thái, ưu tiên, người thực hiện, ngày
- Tìm kiếm theo tiêu đề hoặc mô tả
- Sắp xếp theo ngày tạo, deadline, ưu tiên

## Quản lý tài liệu (Documents)

### Upload tài liệu

1. Vào Documents > Upload
2. Kéo thả file hoặc nhấn "Browse" để chọn file
3. Hỗ trợ định dạng: PDF, DOCX, XLSX, PNG, JPG
4. Kích thước tối đa: 50MB per file
5. Nhập mô tả và tag cho tài liệu
6. Nhấn "Upload"

### Phân quyền tài liệu

- **Public:** Tất cả người dùng có thể xem
- **Department:** Chỉ thành viên phòng ban
- **Private:** Chỉ người tạo và người được chia sẻ

## Báo cáo (Reports)

### Loại báo cáo

- **Weekly Report:** Báo cáo tuần tự động
- **Monthly Summary:** Tổng hợp tháng
- **Custom Report:** Báo cáo tùy chỉnh

### Tạo báo cáo tùy chỉnh

1. Vào Reports > Custom Report
2. Chọn loại dữ liệu: Tasks, Documents, Activities
3. Chọn khoảng thời gian
4. Chọn biểu đồ: Bar, Line, Pie, Table
5. Nhấn "Generate Report"
6. Export: PDF, Excel, CSV

## Thông báo

### Cấu hình thông báo

Vào Settings > Notifications để cấu hình:
- Email notifications: Bật/tắt
- Push notifications: Bật/tắt (cần cho phép trình duyệt)
- Notification frequency: Real-time / Daily digest / Weekly digest

### Loại thông báo

- Task được gán mới
- Task sắp hết hạn
- Comment mới trên task
- Tài liệu được chia sẻ
- System announcements

## Xử lý lỗi thường gặp

### Lỗi PAGE_NOT_LOADING

**Nguyên nhân:** Cache trình duyệt hoặc network issue
**Cách xử lý:** Clear cache (Ctrl+Shift+Delete), thử lại, kiểm tra mạng

### Lỗi UPLOAD_FAILED

**Nguyên nhân:** File quá lớn hoặc định dạng không hỗ trợ
**Cách xử lý:** Kiểm tra kích thước file (< 50MB), kiểm tra định dạng

### Lỗi PERMISSION_DENIED

**Nguyên nhân:** Không có quyền truy cập tài nguyên
**Cách xử lý:** Liên hệ admin để được cấp quyền phù hợp

## Phím tắt

| Phím tắt | Chức năng |
|-----------|-----------|
| Ctrl+N | Tạo task mới |
| Ctrl+K | Mở tìm kiếm |
| Ctrl+/ | Xem phím tắt |
| Esc | Đóng dialog/modal |
