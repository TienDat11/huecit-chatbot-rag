# Tối ưu hóa hiệu suất hệ thống

## Tổng quan

Tài liệu hướng dẫn giám sát và tối ưu hiệu suất hệ thống CIT. Bao gồm các phương pháp xác định điểm nghẽn, tối ưu database, cache, và API response time.

## Kiến trúc hiệu suất

### Sơ đồ components

```
Client → CDN (CloudFlare) → Nginx → Application (Gunicorn)
  → Redis Cache → PostgreSQL
  → MinIO Storage
  → Elasticsearch (Search)
```

### Target SLA

| Metric | Target | Critical |
|--------|--------|----------|
| API Response Time (p50) | < 200ms | > 500ms |
| API Response Time (p99) | < 1000ms | > 3000ms |
| Uptime | 99.9% | < 99.5% |
| Error Rate | < 0.1% | > 1% |
| Throughput | > 1000 req/s | < 500 req/s |

## Giám sát hiệu suất

### Application Metrics

#### Response Time

```bash
# Kiểm tra response time trung bình
curl -o /dev/null -s -w "%{time_total}\n" https://portal.cit.hue.edu.vn/api/health

# Monitor real-time
watch -n 1 'curl -o /dev/null -s -w "%{time_total}\n" https://portal.cit.hue.edu.vn/api/health'
```

#### Memory Usage

```bash
# Kiểm tra memory của application
ps aux | grep gunicorn | awk '{sum += $6} END {print "Memory (MB):", sum/1024}'

# Kiểm tra overall system memory
free -h
```

#### CPU Usage

```bash
# Top processes by CPU
ps aux --sort=-%cpu | head -10

# System load
uptime
```

### Database Metrics

#### Slow Queries

```sql
-- Enable slow query log
ALTER SYSTEM SET log_min_duration_statement = 500;
SELECT pg_reload_conf();

-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

#### Connection Pool

```sql
-- Current connections
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state;

-- Active queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
```

#### Index Usage

```sql
-- Unused indexes
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Missing indexes (sequential scans)
SELECT relname, seq_scan, idx_scan, seq_scan::float / (idx_scan + 1) AS ratio
FROM pg_stat_user_tables
WHERE seq_scan > 100
ORDER BY ratio DESC;
```

## Tối ưu Database

### Indexing Strategy

```sql
-- Thêm index cho các column thường query
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_tasks_status_deadline ON tasks (status, deadline);
CREATE INDEX idx_documents_folder ON documents (folder_id, created_at);

-- Partial index cho active tasks
CREATE INDEX idx_tasks_active ON tasks (deadline)
WHERE status IN ('todo', 'in_progress');
```

### Query Optimization

#### Tránh N+1 queries

```python
# BAD: N+1 query
for task in tasks:
    user = get_user(task.user_id)  # Query mỗi task

# GOOD: Batch query
user_ids = [task.user_id for task in tasks]
users = get_users_batch(user_ids)  # 1 query duy nhất
```

#### Sử dụng EXPLAIN ANALYZE

```sql
EXPLAIN ANALYZE
SELECT t.*, u.username
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE t.status = 'active'
ORDER BY t.deadline ASC
LIMIT 20;
```

### Connection Pooling

```python
# Cấu hình SQLAlchemy pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Số connections duy trì
    max_overflow=10,       # Số connections overflow
    pool_timeout=30,       # Timeout khi chờ connection
    pool_recycle=3600,     # Recycle sau 1 giờ
    pool_pre_ping=True,    # Kiểm tra connection trước khi dùng
)
```

## Tối ưu Cache

### Redis Cache Strategy

#### Cache Patterns

1. **Cache-Aside:** App kiểm tra cache trước, miss thì query DB và lưu vào cache
2. **Write-Through:** Ghi vào cache và DB đồng thời
3. **Write-Behind:** Ghi vào cache trước, async ghi vào DB

#### Cache Configuration

```python
# Redis cache setup
import redis

cache = redis.Redis(
    host='10.0.4.20',
    port=6379,
    db=0,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5,
)

# Cache key convention
# user:{user_id}:profile
# task:{task_id}:detail
# dashboard:{user_id}:summary
```

#### Cache TTL Strategy

| Loại dữ liệu | TTL | Lý do |
|---------------|-----|-------|
| User profile | 1 giờ | Thay đổi ít |
| Task list | 5 phút | Thay đổi thường xuyên |
| Dashboard stats | 10 phút | Aggregate data |
| Static config | 24 giờ | Rất ít thay đổi |

### Nginx Caching

```nginx
# Static file caching
location /static/ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# API response caching (short)
location /api/public/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}
```

## Tối ưu API

### Pagination

```python
# GOOD: Cursor-based pagination (efficient)
@app.get("/api/tasks")
def list_tasks(cursor: str = None, limit: int = 20):
    query = Task.query
    if cursor:
        query = query.filter(Task.id > cursor)
    return query.order_by(Task.id).limit(limit).all()

# BAD: Offset pagination (slow for large offset)
@app.get("/api/tasks")
def list_tasks(page: int = 1, limit: int = 20):
    return Task.query.offset((page - 1) * limit).limit(limit).all()
```

### Response Compression

```nginx
# Enable gzip compression
gzip on;
gzip_types application/json text/plain text/css;
gzip_min_length 1024;
gzip_comp_level 6;
```

### Rate Limiting

```nginx
# Rate limit API endpoints
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;

location /api/ {
    limit_req zone=api burst=10 nodelay;
    proxy_pass http://app_server;
}
```

## Xử lý lỗi hiệu suất

### Lỗi SLOW_RESPONSE

**Dấu hiệu:** API response time > 2 giây

**Cách xử lý:**
1. Kiểm tra slow query log
2. Verify cache hit rate
3. Check CPU/Memory usage
4. Review query execution plan

### Lỗi HIGH_MEMORY

**Dấu hiệu:** Memory usage > 90%

**Cách xử lý:**
1. Identify memory-hungry processes
2. Check for memory leaks
3. Restart application if needed
4. Scale horizontally

### Lỗi DATABASE_OVERLOAD

**Dấu hiệu:** Connection pool exhausted, query timeout

**Cách xử lý:**
1. Kill long-running queries
2. Enable read replica để giảm tải primary
3. Optimize slow queries
4. Increase pool size tạm thời

## Load Testing

### Sử dụng k6

```javascript
// load-test.js
import http from 'k6/http';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up
    { duration: '5m', target: 100 },   // Sustain
    { duration: '2m', target: 200 },   // Spike
    { duration: '5m', target: 200 },   // Sustain
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  http.get('https://portal.cit.hue.edu.vn/api/tasks');
}
```

```bash
# Chạy load test
k6 run load-test.js
```

## Performance Checklist

### Hàng ngày
- [ ] Kiểm Grafana dashboard cho anomalies
- [ ] Review alert emails
- [ ] Check error rate trends

### Hàng tuần
- [ ] Analyze slow query log
- [ ] Review cache hit rates
- [ ] Check storage growth

### Hàng tháng
- [ ] Run full load test
- [ ] Review and optimize indexes
- [ ] Capacity planning cho tháng tới
- [ ] Update SLA metrics report
