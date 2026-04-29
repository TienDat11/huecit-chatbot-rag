# Khắc phục lỗi kết nối cơ sở dữ liệu

## Tổng quan

Tài liệu hướng dẫn xử lý các lỗi kết nối database phổ biến trong hệ thống CIT. Hệ thống sử dụng PostgreSQL làm cơ sở dữ liệu chính với connection pooling qua PgBouncer.

## Kiến trúc kết nối

### Sơ đồ kết nối

```
Application → PgBouncer (Pool) → PostgreSQL Primary
                                  → PostgreSQL Replica (Read-only)
```

### Thông số cấu hình

| Tham số | Giá trị mặc định | Mô tả |
|---------|-----------------|-------|
| max_connections | 100 | Số kết nối tối đa |
| pool_size | 20 | Kích thước connection pool |
| connection_timeout | 30s | Thời gian chờ kết nối |
| idle_timeout | 600s | Thời gian ngắt kết nối nhàn rỗi |

## Lỗi CONNECTION_TIMEOUT

### Nguyên nhân

1. **Database service không chạy:** PostgreSQL service bị dừng hoặc crash
2. **Firewall chặn kết nối:** Rules iptables hoặc security group chặn port 5432
3. **Connection pool hết:** Tất cả connections đang được sử dụng
4. **Network latency cao:** Mạng chậm hoặc mất gói tin

### Cách xử lý

#### Kiểm tra database service

```bash
# Kiểm tra trạng thái PostgreSQL
systemctl status postgresql
# Khởi động lại nếu cần
systemctl restart postgresql
# Kiểm tra log
tail -f /var/log/postgresql/postgresql-15-main.log
```

#### Kiểm tra connection pool

```bash
# Xem số kết nối hiện tại
SELECT count(*) FROM pg_stat_activity;
# Xem các kết nối đang chờ
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

#### Kiểm tra firewall

```bash
# Kiểm tra port 5432 đang mở
netstat -tlnp | grep 5432
# Kiểm tra iptables rules
iptables -L -n | grep 5432
```

## Lỗi QUERY_FAILED

### Nguyên nhân

1. **SQL syntax lỗi:** Câu truy vấn viết sai cú pháp
2. **Table không tồn tại:** Bảng chưa được tạo hoặc bị xóa
3. **Permission denied:** User không có quyền truy cập
4. **Deadlock:** Xung đột khi nhiều transaction truy cập cùng dữ liệu

### Cách xử lý

#### Kiểm tra SQL syntax

```sql
-- Sử dụng EXPLAIN ANALYZE để kiểm tra
EXPLAIN ANALYZE SELECT * FROM users WHERE username = 'test';
```

#### Kiểm tra permissions

```sql
-- Xem quyền của user
SELECT * FROM information_schema.role_table_grants
WHERE grantee = 'cit_app_user';
-- Cấp quyền nếu cần
GRANT SELECT, INSERT, UPDATE ON users TO cit_app_user;
```

## Lỗi CONNECTION_POOL_EXHAUSTED

### Nguyên nhân

- Số lượng request đồng thời vượt quá pool_size
- Connections không được giải phóng đúng cách (connection leak)
- Long-running queries chiếm connections

### Cách xử lý

1. Tăng pool_size trong cấu hình PgBouncer
2. Kiểm tra code có close connection sau khi dùng
3. Thiết lập query timeout để tránh long-running queries
4. Sử dụng connection pool monitoring

```bash
# Cấu hình PgBouncer
# /etc/pgbouncer/pgbouncer.ini
[databases]
cit_db = host=127.0.0.1 port=5432 dbname=cit_production

[pgbouncer]
pool_mode = transaction
max_client_conn = 200
default_pool_size = 25
reserve_pool_size = 5
```

## Lỗi REPLICATION_LAG

### Nguyên nhân

- Replica không đồng bộ kịp với Primary
- Network bandwidth giữa Primary và Replica không đủ
- Heavy write workload trên Primary

### Cách xử lý

```sql
-- Kiểm tra replication lag
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;
-- Nếu lag > 30 giây, cần kiểm tra network và disk I/O
```

## Backup và Recovery

### Backup định kỳ

```bash
# Full backup hàng ngày
pg_dump -U postgres cit_production > backup_$(date +%Y%m%d).sql
# Backup với compress
pg_dump -U postgres -Fc cit_production > backup_$(date +%Y%m%d).dump
```

### Restore từ backup

```bash
# Restore từ SQL file
psql -U postgres cit_production < backup_20260429.sql
# Restore từ dump file
pg_restore -U postgres -d cit_production backup_20260429.dump
```

## Monitoring

### Metrics quan trọng

- Số active connections
- Query response time (p50, p95, p99)
- Replication lag
- Cache hit ratio
- Deadlock count

### Công cụ monitoring

- PgBouncer admin console: `SHOW STATS;`
- PostgreSQL pg_stat_statements
- Grafana dashboard tích hợp
