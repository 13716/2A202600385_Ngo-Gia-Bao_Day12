import time
import json
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit, r as redis_client
from .cost_guard import check_and_record_cost
from utils.mock_llm import ask as llm_ask

# ─────────────────────────────────────────────────────────
# Logging Setup
# ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str
    session_id: str | None = None  # Dùng để phân biệt các cuộc trò chuyện khác nhau

# ─────────────────────────────────────────────────────────
# Conversation History Management (Redis-backed)
# ─────────────────────────────────────────────────────────
def append_to_history(user_id: str, session_id: str, role: str, content: str):
    """Lưu trữ lịch sử chat vào Redis: 10 tin nhắn gần nhất."""
    key = f"history:{user_id}:{session_id}"
    msg = json.dumps({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    redis_client.rpush(key, msg)
    redis_client.ltrim(key, -10, -1)  # Chỉ giữ lại 10 tin nhắn cuối cùng (5 turns)
    redis_client.expire(key, 24 * 3600)  # Xóa sau 24h không dùng
    return True

def get_history(user_id: str, session_id: str):
    """Lấy lịch sử cuộc trò chuyện từ Redis."""
    key = f"history:{user_id}:{session_id}"
    history_data = redis_client.lrange(key, 0, -1)
    return [json.loads(x) for x in history_data]

# ─────────────────────────────────────────────────────────
# Lifespan Management
# ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(json.dumps({"event": "startup", "app": settings.APP_NAME}))
    try:
        redis_client.ping()
        logger.info(json.dumps({"event": "redis_connected"}))
    except Exception as e:
        logger.error(json.dumps({"event": "redis_failed", "error": str(e)}))
    yield
    logger.info(json.dumps({"event": "shutdown"}))
    redis_client.close()

# ─────────────────────────────────────────────────────────
# App Definition
# ─────────────────────────────────────────────────────────
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# Bật CORS (Cấu hình siêu tương thích cho mọi trình duyệt)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization", "Accept"],
)

# Mount các file tĩnh (ảnh, css) nếu có trong thư mục XanhSM-AI
if os.path.exists("XanhSM-AI"):
    app.mount("/static", StaticFiles(directory="XanhSM-AI"), name="static")

@app.get("/")
async def root():
    # Phục vụ file giao diện XanhSM ngay tại trang chủ
    index_file = os.path.join("XanhSM-AI", "xanhsm-app.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "API is online, but HTML file not found",
        "author": "Ngo Gia Bao"
    }

@app.post("/ask")
async def ask(
    body: AskRequest,
    user_id: str = Depends(verify_api_key)
):
    """
    Agent endpoint có tích hợp: Auth, Rate Limit, Cost Guard, và History.
    """
    # 1. Pipeline Bảo Vệ (Rate Limit & Cost Guard)
    rate_info = check_rate_limit(user_id)
    
    # Ước lượng token trước khi gọi (1 từ ~ 1.3 token)
    prompt_tokens = int(len(body.question.split()) * 1.3)
    check_and_record_cost(user_id, prompt_tokens, 0)
    
    # 2. Xử lý Lịch sử (Conversation State)
    session_id = body.session_id or "default"
    append_to_history(user_id, session_id, "user", body.question)
    
    # 3. Chạy Agent
    # Trong thực tế, bạn sẽ truyền `get_history(...)` vào LLM ở bước này.
    start_time = time.time()
    answer = llm_ask(body.question)
    duration = time.time() - start_time
    
    # Tính phí cho phần completion
    completion_tokens = int(len(answer.split()) * 1.3)
    total_cost = check_and_record_cost(user_id, 0, completion_tokens)
    
    # Lưu câu trả lời
    append_to_history(user_id, session_id, "assistant", answer)
    
    # 4. Ghi log JSON
    logger.info(json.dumps({
        "event": "agent_success",
        "user_id": user_id,
        "session_id": session_id,
        "duration_ms": int(duration * 1000),
        "tokens": prompt_tokens + completion_tokens,
        "budget_used": round(total_cost, 4)
    }))
    
    return {
        "session_id": session_id,
        "question": body.question,
        "answer": answer,
        "status": "success",
        "budget_used_usd": round(total_cost, 4),
        "rate_info": rate_info
    }

@app.get("/history/{session_id}")
async def view_history(session_id: str, user_id: str = Depends(verify_api_key)):
    """API Xem lại lịch sử chat."""
    history = get_history(user_id, session_id)
    return {
        "session_id": session_id,
        "message_count": len(history),
        "history": history
    }

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/ready")
def ready():
    try:
        redis_client.ping()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Redis not available")
