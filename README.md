# Day 12 — Deployment & Microservices: Đưa AI Agent Lên Cloud

> **Sinh viên:** Ngô Gia Bảo  
> **Mã số SV:** 2A202600385  
> **Nền tảng:** Render & Docker  

🚀 **Link Public API (Render):** `https://twoa202600385-ngo-gia-bao-day12.onrender.com`

Đồ án này là ứng dụng hoàn chỉnh cho khóa học Hệ thống và Đám mây (Day 12), nơi xây dựng một Agent "chuẩn Production" có khả năng chống chịu tải cao, thiết kế Stateless, có trí nhớ Chat và giao tiếp độc lập với các Frontend UI, ví dụ như giao diện **XanhSM-AI**.

---

## 🎯 Chức Năng Nổi Bật

1. **Docker Tối Ưu (Multi-stage Build)**  
   Dockerfile được thiết kế theo 2 bước (Builder & Runtime), sử dụng non-root user `appuser` để khóa chặt tính bảo mật và tối ưu dung lượng siêu nhỏ.

2. **Thiết Kế Phi Trạng Thái (Stateless & Redis)**  
   Lịch sử trò chuyện (`Conversation History`) cực nhẹ nhờ lưu ở cụm cơ sở dữ liệu phân tán (Redis). Bất kể Nginx có Load Balance (Cân bằng tải) sang bao nhiêu instance Agent khác nhau, hệ thống vẫn "nhớ" được người dùng đang nói gì.

3. **Rate Limiting (Sliding Window)**  
   Tối giản spam hiệu quả với giới hạn 5 requests/phút áp dụng công nghệ *Sliding Window* bằng `ZSET` của Redis (Kiểm thử báo lỗi chuẩn `429 Too Many Requests`).

4. **Bảo Vệ Ngân Sách (Cost Guard)**  
   Mỗi token gọi AI (mock) đều được tính toán và cộng dồn ra USD. Nếu vượt quá giới hạn 10 USD/tháng, sẽ từ chối gọi vào mô hình LLM qua lỗi `402 Payment Required`.

5. **API Gateway & CORS**  
   Bảo vệ truy cập thông qua Auth Header `X-API-Key`. Đồng thời, đã mở cổng `CORS` để chia sẻ cho các Backend Frontend ngoài luồng kết nối vào dễ dàng (VD: Dự án XanhSM-AI.html đã được tích hợp gọi thẳng lên Cloud API này).

---

## 📁 Cấu Trúc Dự Án (Điểm nhấn)

```text
2A202600385_Ngo-Gia-Bao_Day12/
├── my-production-agent/          # 🌟 DỰ ÁN CUỐI CÙNG HOÀN THIỆN
│   ├── app/                      
│   │   ├── main.py               # (FastAPI: CORS, Gateway, Routing)
│   │   ├── rate_limiter.py       # (Thuật toán Sliding Window)
│   │   ├── cost_guard.py         # (Chặn vượt quá 10$)
│   │   └── config.py             
│   ├── Dockerfile                # (Đã tối ưu 2-stage )
│   ├── docker-compose.yml        # (Sinh 3 Agent + Nginx Load Balancer)
│   ├── nginx.conf                # (Load Balancer File)
│   ├── test_history.py           # (File Test chạy ngữ cảnh Chatbot)
│   └── test_agent.py             # (File Test Rate limit 429)
├── XanhSM-AI/                    
│   └── xanhsm-app.html           # 🚗 Giao diện UI đã nối link thẳng vào Render
├── DEPLOYMENT.md                 # Yêu cầu Deployment của Lab
└── DAY12_DELIVERY_CHECKLIST.md   # Phiếu nộp bài
```

---

## 💻 Hướng Dẫn Chạy Trên Local Của Bạn

Dự án này sử dụng Nginx để cân bằng tải chia đều sức ép qua **3 Agent Instances** song song:

```bash
# 1. Khởi chạy 3 Agent thông qua Docker Compose
cd my-production-agent
docker compose up -d --build --scale agent=3

# 2. Chạy bài Test Rate Limit
python test_agent.py

# 3. Chạy bài Test Trí Nhớ & Tiêu Hao Ngân Sách
python test_history.py

# 4. Tắt Server nếu không dùng
docker compose down
```

## 🌐 Trải nghiệm Trực tiếp (Cloud UI)

Không cần cài đặt, bạn chỉ việc tải file `XanhSM-AI/xanhsm-app.html` trên repo này xuống, bấm đúp chuột lên để hiện ra Giao Diện Chatbot và nhắn tin. Bộ não của bạn XanhSM đang nằm trên Render Mỹ sẽ xử lý ngay lập tức!
