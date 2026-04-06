# 📖 HƯỚNG DẪN CHẠY DỰ ÁN — Voyanta Travel Planner

## 🏗️ Cấu trúc dự án

```
Day-3-Lab-Chatbot-vs-react-agent-Nhom-27/
├── src/
│   ├── agent/agent.py          # ReAct Agent v2 (logic suy luận + tools)
│   ├── core/                   # LLM providers (OpenAI, Gemini, Local)
│   ├── tools/travel_tools.py   # 6 travel tools (tìm điểm đến, giá KS...)
│   └── telemetry/              # Logger + metrics tracker
├── services/
│   ├── backend/app.py          # HTTP server: /api/chat, /api/health
│   └── frontend/               # Giao diện web (index.html, chat.html)
├── report/
│   └── flowchart.md            # Flowchart Mermaid + 5 use case traces
├── .env                        # Cấu hình API key (KHÔNG commit file này)
└── HUONGDAN.md                 # File này
```

---

## ⚡ Yêu cầu hệ thống

- **Python** 3.9 trở lên
- **pip** (đi kèm Python)
- Kết nối internet (để gọi API LLM)

---

## 🚀 Hướng dẫn chạy nhanh (5 bước)

### Bước 1: Clone repo

```bash
git clone https://github.com/HungBil/Day-3-Lab-Chatbot-vs-react-agent-Nhom-27.git
cd Day-3-Lab-Chatbot-vs-react-agent-Nhom-27
```

### Bước 2: Cài thư viện

```bash
pip install openai python-dotenv google-generativeai
```

### Bước 3: Tạo file `.env`

Tạo file `.env` ở thư mục gốc với nội dung sau:

```env
# Dùng OpenRouter (hỗ trợ nhiều model miễn phí)
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# Hoặc dùng OpenAI trực tiếp
# OPENAI_API_KEY=sk-your-openai-key

# Hoặc dùng Google Gemini
# GEMINI_API_KEY=your-gemini-key

# Cấu hình model
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=openai/gpt-4.1-mini

LOG_LEVEL=INFO
```

> ⚠️ **Lưu ý:** Không bao giờ commit file `.env` lên GitHub. File này đã được thêm vào `.gitignore`.

### Bước 4: Chạy server

```bash
python services/backend/app.py
```

Nếu thành công sẽ thấy:
```
Initializing LLM provider...
Ready! Provider: openai, Model: openai/gpt-4.1-mini

🚀 Travel Planner server running at http://localhost:8000
   Frontend:  http://localhost:8000/index.html
   Chat:      http://localhost:8000/chat.html
   API:       POST http://localhost:8000/api/chat
   Health:    GET  http://localhost:8000/api/health
```

### Bước 5: Mở trình duyệt

- **Trang chủ:** http://localhost:8000/index.html
- **Chat:** http://localhost:8000/chat.html

---

## 🤖 Cách dùng giao diện Chat

### Chuyển đổi chế độ

Trên đầu trang chat có nút **segmented control**:

| Chế độ | Ký hiệu | Mô tả |
|:---|:---|:---|
| **💬 Chatbot** | Nền tím | LLM trả lời trực tiếp, không dùng tools |
| **🤖 Agent** | Nền xanh | ReAct loop: suy luận + gọi tools + kiểm tra ngân sách |

### Ví dụ câu hỏi để test

**TC1 – Multi-step (Agent mạnh):**
```
Tôi muốn đi Đà Nẵng 3 ngày vào tháng 6, thích biển, ngân sách 5 triệu. Gợi ý lịch trình và tính tổng chi phí.
```

**TC2 – Ngân sách tràn:**
```
Tôi chỉ có 1 triệu, muốn ở Phú Quốc 3 đêm khách sạn 5 sao.
```

**TC3 – Câu đơn giản (Chatbot cũng làm được):**
```
Thời tiết Sa Pa tháng 12 như thế nào?
```

**TC4 – So sánh 2 điểm đến:**
```
Cho tôi 7 triệu, đi 4 ngày, thích văn hóa. Nên chọn Hội An hay Nha Trang?
```

**TC5 – Input mơ hồ (Agent xử lý tốt hơn):**
```
Tôi muốn đi biển khoảng 3 ngày.
```

---

## 🔧 Cấu hình LLM Provider

Chỉnh `DEFAULT_PROVIDER` và `DEFAULT_MODEL` trong file `.env`:

| Provider | DEFAULT_PROVIDER | Ví dụ DEFAULT_MODEL |
|:---|:---|:---|
| OpenRouter | `openai` | `openai/gpt-4.1-mini` |
| OpenAI | `openai` | `gpt-4o` |
| Google Gemini | `google` | `gemini-2.0-flash` |
| Local (GGUF) | `local` | _(đặt LOCAL_MODEL_PATH)_ |

Sau khi sửa `.env`, khởi động lại server bằng `Ctrl+C` rồi chạy lại.

---

## 📊 Xem logs & metrics

- **Log file:** `logs/YYYY-MM-DD.log` — ghi tất cả sự kiện theo JSON
- **API metrics:** Gửi POST tới `http://localhost:8000/api/metrics`
- **Health check:** GET `http://localhost:8000/api/health`

---

## 🐛 Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|:---|:---|:---|
| `NameError: name 'os' is not defined` | Thiếu import | Đã fix trong code |
| `Error 400: model not found` | Sai model ID | Kiểm tra model ID trên openrouter.ai/models |
| `Error 429: rate limit` | Hết quota model free | Đổi model khác trong `.env` |
| `Error 404: File not found` | Sai đường dẫn FE | Chạy từ thư mục gốc, không phải `services/backend/` |
| `No destination data found` | City tiếng Việt | Đã fix: normalize tự động (Đà Nẵng → da nang) |

---

## 📁 API Endpoints

| Endpoint | Method | Body | Mô tả |
|:---|:---|:---|:---|
| `/api/chat` | POST | `{"message": "...", "mode": "agent"}` | Gửi tin nhắn (mode: agent/chatbot) |
| `/api/health` | GET | — | Kiểm tra server |
| `/api/metrics` | POST | — | Xem thống kê phiên |
| `/*` | GET | — | Serve static files (FE) |

---

## 👥 Phân công nhóm

| Người | Nhánh | Nhiệm vụ |
|:---|:---|:---|
| Nhân | `nhan-branch` | Travel tools, LLM providers, telemetry |
| Hưng | `feat/agent-v2-integration` | ReAct Agent v2, Backend API, FE Integration |
| FE Team | `feat/fe/travel-planner` | Giao diện Voyanta (index.html, styles.css) |
