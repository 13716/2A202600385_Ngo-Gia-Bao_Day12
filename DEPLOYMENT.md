# Deployment Information

## Public URL
https://twoa202600385-ngo-gia-bao-day12.onrender.com

## Platform
Render (Web Service & Key Value)

## Test Commands

### Health Check
```bash
curl https://twoa202600385-ngo-gia-bao-day12.onrender.com/health
# Expected: {"status": "ok", "timestamp": "..."}
```

### Readiness Check (Redis Connection)
```bash
curl https://twoa202600385-ngo-gia-bao-day12.onrender.com/ready
# Expected: {"status": "ready"}
```

### API Test (with authentication & rate limit & cost guard logic)
```bash
curl -X POST https://twoa202600385-ngo-gia-bao-day12.onrender.com/ask \
  -H "X-API-Key: super-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "question": "Hello Render!"}'
```

## Environment Variables Set
- `PORT`: 8000
- `REDIS_URL`: redis://red-...
- `AGENT_API_KEY`: super-secret-key-123

## Screenshots
Đã chèn đầy đủ.
