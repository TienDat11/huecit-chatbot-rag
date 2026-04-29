# Cấu hình và xử lý sự cố mạng

## Tổng quan

Tài liệu hướng dẫn cấu hình mạng và xử lý các sự cố mạng phổ biến trong hạ tầng CIT. Hệ thống sử dụng kiến trúc multi-tier với load balancer, reverse proxy và các internal services.

## Kiến trúc mạng

### Topology

```
Internet → Firewall → Load Balancer (HAProxy)
  → Web Server 1 (Nginx)
  → Web Server 2 (Nginx)
  → API Gateway → Internal Services
```

### Phân đoạn mạng

| Segment | Subnet | Mô tả |
|---------|--------|-------|
| DMZ | 10.0.1.0/24 | Load balancer, reverse proxy |
| Web Tier | 10.0.2.0/24 | Web servers, API gateway |
| App Tier | 10.0.3.0/24 | Application servers |
| Data Tier | 10.0.4.0/24 | Database, cache servers |
| Management | 10.0.5.0/24 | Monitoring, logging, CI/CD |

## Lỗi NETWORK_TIMEOUT

### Nguyên nhân

1. DNS resolution thất bại
2. Route không tồn tại
3. Firewall rule chặn traffic
4. Target service không phản hồi

### Cách xử lý

#### Kiểm tra DNS

```bash
# Kiểm tra DNS resolution
nslookup api.cit.hue.edu.vn
dig api.cit.hue.edu.vn
# Kiểm tra /etc/resolv.conf
cat /etc/resolv.conf
# Flush DNS cache
systemd-resolve --flush-caches
```

#### Kiểm tra kết nối

```bash
# Ping test
ping -c 4 10.0.2.10
# Port test
telnet 10.0.2.10 443
# Hoặc sử dụng nc
nc -zv 10.0.2.10 443
# Traceroute
traceroute 10.0.2.10
```

## Lỗi DNS_RESOLUTION_FAILED

### Nguyên nhân

- DNS server không phản hồi
- Record không tồn tại
- TTL hết hạn và không refresh được

### Cách xử lý

```bash
# Kiểm tra DNS servers
cat /etc/resolv.conf
# Test với DNS server cụ thể
nslookup api.cit.hue.edu.vn 8.8.8.8
# Kiểm tra local hosts file
cat /etc/hosts
```

## Lỗi SSL_CERTIFICATE_ERROR

### Nguyên nhân

- Certificate hết hạn
- Certificate không khớp domain
- Chain certificate thiếu
- Self-signed certificate không được trust

### Cách xử lý

```bash
# Kiểm tra certificate
openssl s_client -connect api.cit.hue.edu.vn:443 -showcerts
# Kiểm tra ngày hết hạn
echo | openssl s_client -connect api.cit.hue.edu.vn:443 2>/dev/null | openssl x509 -noout -dates
# Renew certificate (Let's Encrypt)
certbot renew --nginx
```

## Load Balancer Configuration

### HAProxy Configuration

```
frontend http_front
    bind *:80
    redirect scheme https code 301 if !{ ssl_fc }

frontend https_front
    bind *:443 ssl crt /etc/ssl/certs/cit.pem
    default_backend web_servers

backend web_servers
    balance roundrobin
    option httpchk GET /health
    server web1 10.0.2.10:8080 check
    server web2 10.0.2.11:8080 check
```

### Health Check

```bash
# Kiểm tra trạng thái HAProxy
echo "show stat" | socat stdio /var/run/haproxy.sock
# Kiểm tra backend servers
echo "show backend" | socat stdio /var/run/haproxy.sock
```

## VPN Configuration

### Kết nối VPN nội bộ

1. Tải OpenVPN client từ trang nội bộ
2. Import cấu hình VPN (.ovpn file)
3. Kết nối với credentials được cấp
4. Verify connection: `curl ifconfig.me` phải trả về IP nội bộ

### Xử lý lỗi VPN

- **Lỗi AUTH_FAILED:** Kiểm tra username/password
- **Lỗi TLS_ERROR:** Certificate hết hạn hoặc sai cấu hình
- **Lỗi TUN_ERROR:** Kiểm tra TUN/TAP driver đã cài

## Network Monitoring

### Công cụ monitoring

- **Zabbix:** Giám sát uptime, latency, bandwidth
- **Grafana:** Dashboard trực quan cho network metrics
- **AlertManager:** Cảnh báo khi network có vấn đề

### Threshold cảnh báo

| Metric | Warning | Critical |
|--------|---------|----------|
| Latency | > 100ms | > 500ms |
| Packet Loss | > 1% | > 5% |
| Bandwidth Usage | > 80% | > 95% |
| DNS Resolution | > 50ms | > 200ms |
