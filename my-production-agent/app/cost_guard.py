from datetime import datetime
from fastapi import HTTPException
from .config import settings
from .rate_limiter import r as redis_client

def check_and_record_cost(user_id: str, prompt_tokens: int, completion_tokens: int):
    """
    Theo dõi chi phí sử dụng hàng tháng của từng user bằng Redis.
    Giá token: GPT-3.5-turbo (Mock) = $0.0015/1K prompt + $0.0020/1K completion
    Nếu quá $10/tháng -> Trả về lỗi 402 Payment Required.
    """
    cost_prompt = (prompt_tokens / 1000.0) * 0.0015
    cost_completion = (completion_tokens / 1000.0) * 0.0020
    total_cost = cost_prompt + cost_completion

    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    # Lấy tổng chi phí trong tháng hiện tại
    current_cost = float(redis_client.get(key) or 0)
    
    # Kiểm tra vượt ngân sách
    if current_cost + total_cost > settings.MONTHLY_BUDGET_USD:
        raise HTTPException(
            status_code=402, 
            detail={
                "error": "Monthly budget exceeded.",
                "limit": settings.MONTHLY_BUDGET_USD,
                "used": current_cost
            }
        )
    
    # Cộng dồn và lưu chi phí mới
    if total_cost > 0:
        redis_client.incrbyfloat(key, total_cost)
        redis_client.expire(key, 32 * 24 * 3600)  # Lưu trữ key trong 32 ngày
        
    return current_cost + total_cost
