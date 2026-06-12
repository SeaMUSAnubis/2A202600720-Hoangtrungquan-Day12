# Deployment Information

## Public URL
https://my-production-agent-app.up.railway.app
*(Lưu ý: Bạn hãy thay thế URL này bằng Public URL thực tế sau khi Deploy lên Railway/Render)*

## Platform
Railway (hoặc điền Render/Cloud Run tuỳ bạn chọn)

## Test Commands

### Health Check
```bash
curl https://my-production-agent-app.up.railway.app/health
# Expected Output: {"status": "ok", "uptime_seconds": 12.5}
```

### API Test (with authentication)
```bash
curl -X POST "https://my-production-agent-app.up.railway.app/ask?question=Hello" \
  -H "X-API-Key: my-secret-key"
# Expected Output: JSON containing the mock answer
```

## Environment Variables Set
- `PORT`: 8000
- `REDIS_URL`: (Redis Cloud Connection String của bạn)
- `AGENT_API_KEY`: my-secret-key
- `LOG_LEVEL`: INFO
- `RATE_LIMIT_PER_MINUTE`: 10
- `MONTHLY_BUDGET_USD`: 10.0

## Screenshots
*(Lưu ý: Bạn cần chụp các hình ảnh dưới đây và để vào folder `screenshots/` rồi gắn link)*

- [Deployment dashboard (Railway/Render) - CHỤP ẢNH TẠI ĐÂY](screenshots/dashboard.png)
- [Service running (Logs) - CHỤP ẢNH TẠI ĐÂY](screenshots/running.png)
- [Test results (Postman/Curl) - CHỤP ẢNH TẠI ĐÂY](screenshots/test.png)
