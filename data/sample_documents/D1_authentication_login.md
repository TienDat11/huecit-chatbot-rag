# Hướng dẫn xác thực và đăng nhập hệ thống

## Giới thiệu

Tài liệu này mô tả chi tiết quy trình xác thực người dùng trong hệ thống quản lý CIT. Hệ thống hỗ trợ nhiều phương thức xác thực bao gồm đăng nhập bằng tài khoản nội bộ, LDAP và Single Sign-On (SSO).

## Yêu cầu hệ thống

- Trình duyệt web: Chrome 90+, Firefox 88+, Edge 90+
- Kết nối mạng ổn định
- Tài khoản đã được quản trị viên kích hoạt
- Mật khẩu tuân thủ chính sách bảo mật: tối thiểu 8 ký tự, bao gồm chữ hoa, chữ thường và số

## Quy trình đăng nhập

### Bước 1: Truy cập trang đăng nhập

Mở trình duyệt và truy cập địa chỉ: `https://cit.hue.edu.vn/auth/login`

Trang đăng nhập sẽ hiển thị form nhập liệu với các trường:
- Tên đăng nhập (username)
- Mật khẩu (password)
- Phương thức xác thực (nội bộ / LDAP / SSO)

### Bước 2: Nhập thông tin đăng nhập

Nhập tên đăng nhập và mật khẩu vào form tương ứng. Lưu ý:
- Tên đăng nhập không phân biệt hoa thường
- Mật khẩu có phân biệt hoa thường
- Không chia sẻ thông tin đăng nhập với người khác

### Bước 3: Xác thực hai yếu tố (2FA)

Đối với các tài khoản có bật xác thực hai yếu tố, hệ thống sẽ yêu cầu nhập mã OTP:
- Mã OTP được gửi qua email đã đăng ký
- Mã OTP có hiệu lực trong 5 phút
- Tối đa 3 lần nhập sai, cần yêu cầu mã mới

### Bước 4: Hoàn tất đăng nhập

Sau khi xác thực thành công, hệ thống sẽ:
- Chuyển hướng đến trang Dashboard
- Tạo session token có thời hạn 8 giờ
- Ghi log hoạt động đăng nhập

## Xử lý lỗi thường gặp

### Lỗi SESSION_EXPIRED

**Mô tả:** Phiên làm việc hết hạn sau 8 giờ không hoạt động.

**Cách xử lý:**
1. Đăng xuất khỏi hệ thống
2. Đăng nhập lại với thông tin xác thực
3. Kiểm tra múi giờ hệ thống nếu lỗi lặp lại

### Lỗi INVALID_CREDENTIALS

**Mô tả:** Thông tin đăng nhập không chính xác.

**Cách xử lý:**
1. Kiểm tra Caps Lock đang tắt
2. Xác nhận tên đăng nhập chính xác
3. Sử dụng chức năng "Quên mật khẩu" nếu cần
4. Liên hệ quản trị viên nếu vẫn không đăng nhập được

### Lỗi ACCOUNT_LOCKED

**Mô tả:** Tài khoản bị khóa sau 5 lần đăng nhập thất bại liên tiếp.

**Cách xử lý:**
1. Chờ 30 phút để tài khoản tự động mở khóa
2. Hoặc liên hệ quản trị viên để mở khóa thủ công
3. Kiểm tra xem có ai đang cố gắng truy cập trái phép không

### Lỗi SSO_FAILED

**Mô tả:** Xác thực Single Sign-On thất bại.

**Cách xử lý:**
1. Kiểm tra cookie của trình duyệt
2. Xóa cache và thử lại
3. Đảm bảo tài khoản SSO đã được liên kết với hệ thống CIT

## Quản lý phiên làm việc

### Gia hạn session

Session tự động gia hạn khi người dùng có hoạt động. Để gia hạn thủ công:
- Nhấp vào nút "Gia hạn phiên" ở góc phải trên
- Hoặc gọi API: `POST /api/auth/renew-session`

### Đăng xuất tất cả thiết bị

Để đăng xuất khỏi tất cả các thiết bị đang kết nối:
1. Vào Cài đặt > Bảo mật > Quản lý phiên
2. Nhấp "Đăng xuất tất cả"
3. Xác nhận hành động

## Phân quyền người dùng

Hệ thống có 4 vai trò chính:

| Vai trò | Mô tả | Quyền hạn |
|---------|--------|-----------|
| Admin | Quản trị viên | Toàn quyền hệ thống |
| Manager | Quản lý | Quản lý phòng ban, báo cáo |
| Staff | Nhân viên | Sử dụng chức năng cơ bản |
| Viewer | Người xem | Chỉ xem dữ liệu |

## Câu hỏi thường gặp

**Q: Làm sao để thay đổi mật khẩu?**
A: Vào Cài đặt > Bảo mật > Đổi mật khẩu. Nhập mật khẩu hiện tại và mật khẩu mới.

**Q: Tôi quên mật khẩu phải làm sao?**
A: Nhấp "Quên mật khẩu" trên trang đăng nhập, nhập email đã đăng ký để nhận link đặt lại mật khẩu.

**Q: Bao lâu thì phải đổi mật khẩu một lần?**
A: Mật khẩu có hiệu lực 90 ngày. Hệ thống sẽ nhắc nhở trước 7 ngày khi mật khẩu sắp hết hạn.
