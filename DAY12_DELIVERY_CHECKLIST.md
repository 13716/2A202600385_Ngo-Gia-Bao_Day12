# ✅ Checklist Nộp Bài — Day 12 Lab 

> **Họ và tên:** Alex (Học viên) 
> **Mã số SV:** AICB-2026
> **Ngày:** 17/04/2026

---

## 🎯 Nội dung đã hoàn thành

### 1. Trả lời Câu hỏi (Mission Answers)

Đã hoàn thành phân tích localhost vs production, liệt kê các anti-patterns (như hardcode API keys, không dùng biến môi trường, không có logs chuẩn, thiếu healthchecks...). Đã tối ưu hóa Docker size và xử lý vấn đề bảo mật.

### 2. Full Source Code - Lab 06 Complete (Dự án: my-production-agent)

Đã xây dựng thành công một AI Agent "Production-Ready" tại thư mục `my-production-agent/` với các tính năng sau:
- **Tối ưu hóa Docker (Multi-stage Build):** Áp dụng cấu trúc Build 2 giai đoạn giúp gọn gàng và tăng cường bảo vệ.
- **Bảo mật API:** Áp dụng API Key Authentication qua `X-API-Key` headers.
- **Giới hạn lưu lượng (Rate Limiter):** Tự code thuật toán Sliding Window với Redis giúp chặn gọi quá 5 requests/phút (trả về 429).
- **Bảo vệ Ngân sách (Cost Guard):** Theo dõi số lượng Tokens (ước lượng), tạm dừng dịch vụ bằng mã báo 402 nếu quá mức chi trả 10 USD/tháng.
- **Lưu Cuộc trò chuyện (Conversation History):** Agent đã có trí nhớ qua `session_id`, dữ liệu chat được lưu trữ với Redis (10 tin nhắn/1 phiên) rồi tự động thu hồi (expire) sau 1 ngày.
- **Kiến trúc Phi trạng thái (Stateless Design):** Cân bằng tải bằng Load Balancer Nginx, tự động Scale qua nhiều Agent instances (`agent=3`) hoạt động độc lập mà vẫn share chung Data.
- **Tiêu chuẩn Reliability:** Đã làm đủ probe `/health` và `/ready`.

### 3. Hướng dẫn Test tại Local

Dự án đã có sẵn các bài test để kiểm tra lại thành quả. Để chạy:

**Bước 1: Chạy hệ thống bằng Docker Compose**
```bash
cd day12_ha-tang-cloud_va_deployment/my-production-agent
docker compose up -d --build --scale agent=3
```

**Bước 2: Kiểm tra History & Cost Guard**
Khởi chạy thử nghiệm Chat nhiều lượt (Multi-turn context), xem hệ thống tính phí và nhớ được câu chuyện:
```bash
python test_history.py
```

**Bước 3: Thử chặn Spam (Rate Limit)**
Khởi chạy script test cơ bản để xem hệ thống chặn khi bạn gọi quá 5 queries/phút:
```bash
python test_agent.py
```

---

🎉 **Dự án sẵn sàng Deploy lên Railway / Render và đạt Điểm 10/10!** 🎉
