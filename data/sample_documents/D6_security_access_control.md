# Hướng dẫn bảo mật và phân quyền hệ thống

## Tổng quan

Tài liệu mô tả chính sách bảo mật, quy trình phân quyền và xử lý các sự cố bảo mật trong hệ thống CIT. Việc tuân thủ các quy định bảo mật là bắt buộc đối với tất cả người dùng.

## Chính sách bảo mật

### Mật khẩu

Yêu cầu mật khẩu mạnh:
- Độ dài tối thiểu: 8 ký tự
- Phải bao gồm: chữ hoa, chữ thường, số
- Khuyến nghị: thêm ký tự đặc biệt
- Không sử dụng: thông tin cá nhân, từ điển, mật khẩu cũ
- Thời hạn: 90 ngày, nhắc nhở trước 7 ngày
- Lịch sử: không lặp lại 5 mật khẩu gần nhất

### Xác thực đa yếu tố (MFA)

Hệ thống hỗ trợ hai phương thức MFA:
1. **TOTP (Time-based OTP):** Sử dụng app Google Authenticator hoặc Authy
2. **Email OTP:** Mã gửi qua email đã đăng ký

MFA bắt buộc cho:
- Tài khoản Admin
- Truy cập từ IP lạ
- Thao tác nhạy cảm (xóa dữ liệu, thay đổi quyền)

## Phân quyền chi tiết

### Role-Based Access Control (RBAC)

#### Vai trò hệ thống

**Super Admin:**
- Quản lý toàn bộ hệ thống
- Cấp và thu hồi quyền
- Xem audit log
- Cấu hình hệ thống

**Department Admin:**
- Quản lý người dùng trong phòng ban
- Phân quyền tài nguyên phòng ban
- Xem báo cáo phòng ban

**Staff:**
- Sử dụng chức năng được cấp quyền
- Upload/download tài liệu
- Tạo và quản lý task

**Guest:**
- Chỉ xem tài liệu public
- Không thể tạo/sửa/xóa

#### Phân quyền theo resource

| Resource | Super Admin | Dept Admin | Staff | Guest |
|----------|-------------|------------|-------|-------|
| User Management | Full | Dept only | Self profile | View own |
| Documents | Full | Dept full | Own + shared | Public only |
| Tasks | Full | Dept full | Own + assigned | - |
| Reports | Full | Dept full | Own | - |
| System Config | Full | - | - | - |
| Audit Log | Full | Dept only | - | - |

### Attribute-Based Access Control (ABAC)

Ngoài RBAC, hệ thống còn hỗ trợ ABAC với các điều kiện:
- **Time-based:** Chỉ cho phép truy cập trong giờ làm việc (8:00-17:30)
- **Location-based:** Chỉ cho phép từ IP nội bộ hoặc VPN
- **Device-based:** Chỉ cho phép từ thiết bị đã đăng ký

## Xử lý sự cố bảo mật

### Sự cố BRUTE_FORCE_ATTACK

**Dấu hiệu:**
- Nhiều lần đăng nhập thất bại từ cùng IP
- Login attempts với username khác nhau
- Traffic bất thường trên port auth

**Cách xử lý:**
1. Kiểm tra log đăng nhập: `grep "auth failed" /var/log/cit/auth.log`
2. Block IP tấn công: `iptables -A INPUT -s ATTACKER_IP -j DROP`
3. Enable rate limiting trên nginx
4. Thông báo cho team security
5. Kiểm tra xem có tài khoản bị compromise không

### Sự cố DATA_LEAK

**Dấu hiệu:**
- Download bất thường số lượng lớn file
- Truy cập tài nguyên ngoài quyền
- API call frequency bất thường

**Cách xử lý:**
1. Tạm khóa tài khoản nghi ngờ
2. Audit log xem tài nguyên nào bị truy cập
3. Đánh giá phạm vi dữ liệu bị rò rỉ
4. Báo cáo cho management theo quy trình incident response
5. Đổi mật khẩu tất cả tài khoản liên quan

### Sự cố SQL_INJECTION

**Dấu hiệu:**
- Query log chứa các pattern: `' OR 1=1 --`, `UNION SELECT`
- Error message lộ thông tin database
- Dữ liệu bất thường trong bảng

**Cách xử lý:**
1. Kiểm tra input validation trên các endpoint
2. Đảm bảo sử dụng parameterized queries
3. Enable WAF rules cho SQL injection
4. Review code các module có input từ user

### Sự cố XSS_ATTACK

**Dấu hiệu:**
- Script tag trong input fields
- Redirect bất thường
- Cookie bị đánh cắp

**Cách xử lý:**
1. Enable Content-Security-Policy headers
2. Sanitize tất cả user input
3. Implement output encoding
4. Sử dụng HttpOnly và Secure flags cho cookies

## Audit Logging

### Log categories

- **Auth logs:** Đăng nhập, đăng xuất, thay đổi mật khẩu
- **Access logs:** Truy cập tài nguyên, download file
- **Modification logs:** Tạo, sửa, xóa dữ liệu
- **Admin logs:** Thay đổi quyền, cấu hình hệ thống

### Log retention

| Loại log | Retention |
|----------|-----------|
| Auth logs | 1 năm |
| Access logs | 6 tháng |
| Modification logs | 2 năm |
| Admin logs | 3 năm |

### Truy vấn audit log

```bash
# Xem log theo user
curl -X GET "https://portal.cit.hue.edu.vn/api/audit?user=john.doe" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Xem log theo thời gian
curl -X GET "https://portal.cit.hue.edu.vn/api/audit?from=2026-04-01&to=2026-04-29" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Kiểm tra bảo mật định kỳ

### Checklist hàng tháng

- [ ] Review user accounts và disable inactive accounts
- [ ] Kiểm tra failed login attempts
- [ ] Verify backup integrity
- [ ] Update security patches
- [ ] Review permission changes
- [ ] Test incident response procedures

### Penetration testing

- Thực hiện quarterly bởi team security
- Scope: web application, API, network infrastructure
- Report gửi cho CTO và IT Manager
- Remediation plan trong 14 ngày sau report
