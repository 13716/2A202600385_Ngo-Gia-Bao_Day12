import google.generativeai as genai
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Cấu hình Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

async def ask_gemini(question: str, history: list = None) -> str:
    if not settings.GEMINI_API_KEY:
        return "Lỗi: Vui lòng cấu hình GEMINI_API_KEY trên Render."

    # Danh sách các model để thử (từ mới đến cũ để đảm bảo không lỗi 404)
    model_names = ["gemini-1.5-flash", "gemini-pro"]
    
    last_error = ""
    for name in model_names:
        try:
            logger.info(f"Trying Gemini model: {name}")
            model = genai.GenerativeModel(name)
            
            # Khởi tạo chat với system instruction đơn giản
            chat = model.start_chat(history=[])
            response = chat.send_message(question)
            
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Model {name} failed: {last_error}")
            continue # Thử model tiếp theo
            
    return f"Xin lỗi, chatbot đang bảo trì. (Chi tiết lỗi: {last_error[:100]})"
