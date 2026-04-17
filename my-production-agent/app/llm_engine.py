import google.generativeai as genai
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Cấu hình Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is missing. Real LLM will not work.")

async def ask_gemini(question: str, history: list = None) -> str:
    """
    Hàm gọi trí tuệ thật từ Google Gemini
    """
    if not settings.GEMINI_API_KEY:
        return "Lỗi máy chủ: Thiếu GEMINI_API_KEY. Vui lòng cấu hình trên Render."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Chuyển đổi chat history sang định dạng Gemini
        chat_session = model.start_chat(history=[]) # Có thể tối ưu thêm history ở đây
        
        # Gửi tin nhắn mới
        response = chat_session.send_message(question)
        return response.text
    except Exception as e:
        logger.error(f"Gemini Error: {str(e)}")
        return f"Xin lỗi, trí tuệ nhân tạo đang bận (Error: {str(e)[:50]}...)"
