# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Bỉnh Hưng
- **Student ID**: [Điền MSSV]
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

### Vai trò: Person 2 — Agent v2 + Backend API + Frontend Integration

Tôi chịu trách nhiệm nâng cấp Agent v1 (skeleton) thành Agent v2 hoàn chỉnh, tạo backend API server để kết nối FE với Agent, và tích hợp JavaScript vào giao diện chat.

### Modules Implemented

#### 1. `src/agent/agent.py` — ReAct Agent v2

Nâng cấp toàn bộ agent từ skeleton lên production-ready:

- **System prompt engineering**: Thêm few-shot example cụ thể cho du lịch Việt Nam, giúp LLM hiểu đúng format `Action: tool_name(arg1, arg2)` ngay từ bước đầu.
- **Domain guardrails**: Thêm luật chặn off-topic (mua xe VinFast, ngôn từ thô tục) → redirect về du lịch mà không gọi tools.
- **Vietnamese response**: Yêu cầu LLM luôn trả Final Answer bằng tiếng Việt.
- **Structured return**: Đổi `run()` từ `str` sang `Dict` chứa `{answer, traces, steps, status}` để phục vụ API.
- **Metrics tracking**: Gọi `tracker.track_request()` mỗi bước để ghi provider, model, tokens, latency.
- **Error recovery**: Khi parse thất bại → log `PARSE_ERROR` + nudge LLM dùng đúng format, tự retry.
- **Dual action parsing**: Hỗ trợ cả `tool(args)` và `tool {json}` patterns.
- **Max steps**: Tăng từ 7 → 10 để có headroom cho retry do lỗi parse/tool.

```python
# Ví dụ: Domain guardrail trong system prompt
## Domain Guardrails (MANDATORY):
- If the user asks about something NOT related to travel:
  Final Answer: Xin lỗi, tôi chỉ hỗ trợ lập kế hoạch du lịch Việt Nam.
- If the user uses rude language:
  Final Answer: Xin vui lòng sử dụng ngôn ngữ lịch sự.
```

#### 2. `services/backend/app.py` — Backend HTTP Server

Tạo từ đầu, dùng stdlib `http.server` (không cần pip thêm):

- Phục vụ static files từ `services/frontend/`
- **`POST /api/chat`**: Nhận `{message, mode}`, điều phối sang `_run_agent()` hoặc `_run_chatbot()`
- **`_run_chatbot()`**: Gọi LLM trực tiếp, không tools, không ReAct — baseline cho so sánh
- **`_run_agent()`**: Chạy ReAct loop đầy đủ với tools và traces
- **CORS headers**: Cho phép cross-origin khi dev
- **`GET /api/health`**, **`POST /api/metrics`**: Health check và telemetry

#### 3. `services/frontend/chat.html` — Chat UI Integration

- Thêm JavaScript gọi `/api/chat` qua `fetch()` POST
- **Typing indicator**: Hiển thị "🤖 Agent đang suy luận..." hoặc "💬 Chatbot đang trả lời..."
- **Collapsible traces**: Dùng `<details><summary>` hiển thị quá trình suy luận theo từng bước
- **Mode toggle**: Segmented pill control với glassmorphism, gradient glow, pulse animation
- **Mode badge**: Mỗi tin nhắn có badge xanh (Agent) hoặc tím (Chatbot)
- **Toàn bộ UI tiếng Việt**: Labels, placeholders, error messages

#### 4. `src/tools/travel_tools.py` — Vietnamese Normalization + Budget Fix

- **`_normalize_city()`**: Thêm mapping tiếng Việt → ASCII (Đà Nẵng → da nang, Phú Quốc → phu quoc...)
- **`check_budget()`**: Hỗ trợ biểu thức toán (LLM hay gửi `1500000 + 900000 + 1400000`)
- Fallback: strip diacritics bằng `unicodedata.normalize("NFKD")`

#### 5. `src/core/openai_provider.py` — OpenRouter Support

- Thêm `base_url` parameter + `os.getenv("OPENAI_BASE_URL")` để hỗ trợ OpenRouter API
- Thêm `import os` (thiếu trong code gốc)

#### 6. `report/flowchart.md` — 5 Mermaid Diagrams

- Kiến trúc tổng quan
- ReAct loop chi tiết
- Tool execution + error handling
- Domain guardrail flow
- 5 use case traces dạng subgraph

#### 7. `HUONGDAN.md` — Hướng dẫn chạy đầy đủ

---

## II. Debugging Case Study (10 Points)

### Case 1: Vietnamese Input Crash — "Đà Nẵng" không được nhận diện

- **Problem**: Khi user gõ "Tôi muốn đi Đà Nẵng", tool `search_destination("Đà Nẵng")` trả "No destination data found" vì data dùng key ASCII "da nang".
- **Log Source**:
```json
{"event": "AGENT_STEP", "data": {"step": 1, "action": "search_destination(Đà Nẵng)"}}
{"event": "AGENT_STEP", "data": {"step": 1, "observation": "No destination data found for 'Đà Nẵng'."}}
```
- **Diagnosis**: `_normalize_city()` gốc chỉ làm `city.strip().lower()`, không xử lý Unicode diacritics. LLM tự sửa ở bước 2 (thử "Da Nang"), nhưng tốn thêm 1 step → dễ vượt max_steps.
- **Solution**: Viết lại `_normalize_city()` với:
  1. Direct mapping dict: `{"đà nẵng": "da nang", "phú quốc": "phu quoc", ...}`
  2. Fallback: `unicodedata.normalize("NFKD")` + strip combining chars + replace `đ → d`

### Case 2: Budget Expression — LLM gửi phép tính thay vì số

- **Problem**: Agent gọi `check_budget(1500000 + 900000 + 1400000, 5000000)` → tool trả "Invalid number format".
- **Diagnosis**: `int()` không parse được biểu thức `1500000 + 900000 + 1400000`. LLM thường cộng tổng trong argument thay vì tính trước.
- **Solution**: Thêm `_safe_parse_number()` dùng `eval()` với sandbox `{"__builtins__": {}}` để parse an toàn phép cộng/trừ đơn giản.

### Case 3: Off-Topic Query Không Bị Chặn

- **Problem**: User hỏi "Tôi muốn mua xe VinFast" → Agent trả lời về xe VinFast thay vì chặn.
- **Diagnosis**: System prompt v2 ban đầu chỉ nói "You solve user queries" mà không giới hạn domain.
- **Solution**: Thêm "Domain Guardrails (MANDATORY)" section vào prompt với exact template cho off-topic responses. Kết quả: Agent nhận diện off-topic → trả Final Answer ngay bước 1, không gọi tools.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning — Thought block giúp gì?

Block `Thought` buộc LLM phải **plan trước khi hành động**. Ví dụ:
- Chatbot baseline: Nghe "Đà Nẵng 3 ngày 5 triệu" → bịa luôn giá khách sạn, đôi khi sai.
- Agent: Thought "cần check giá khách sạn" → gọi `get_hotel_price("Da Nang", 3, 3)` → nhận data thật 500k/đêm → tính đúng.

Nhưng **Thought cũng là chi phí**: mỗi bước tốn ~300-500 tokens. Câu đơn giản ("Thời tiết Sapa?") Agent mất 2 steps trong khi Chatbot trả lời ngay 1 call.

### 2. Reliability — Khi nào Agent thua Chatbot?

| Trường hợp | Agent | Chatbot | Lý do |
|:---|:---|:---|:---|
| Câu đơn giản (thời tiết) | ✅ nhưng chậm (2 steps) | ✅ nhanh (1 call) | Agent gọi tool thừa |
| Data không tồn tại (Đà Lạt) | ❌ "No data found" | ✅ Dùng kiến thức LLM | Agent phụ thuộc mock data |
| Ngôn từ thô tục | ✅ Chặn + redirect | ✅ Cũng xử lý được | Hòa |

**Kết luận**: Agent **thua** khi data tool limited mà LLM có kiến thức sẵn. Agent **thắng** ở multi-step vì data chính xác, có tính toán.

### 3. Observation — Feedback từ environment

Observation là **grounding mechanism** quan trọng nhất. Khi `search_destination("Đà Nẵng")` trả "No data found", Agent tự sửa thành "Da Nang" ở bước tiếp. Nhưng khi `check_budget(expr)` trả "Invalid number format", Agent cũng tự sửa — gửi lại số đúng `3800000`.

Điều này chứng tỏ: **error messages tốt = self-healing agent**. Nếu tool chỉ trả "Error" chung chung, LLM không biết sửa gì.

---

## IV. Future Improvements (5 Points)

### Scalability
- **Async tool calls**: Hiện tại chỉ gọi 1 tool/step. Có thể dùng `asyncio` để gọi song song khi compare 2 destinations.
- **Streaming response**: Dùng SSE (Server-Sent Events) thay vì đợi toàn bộ response → UX tốt hơn.

### Safety
- **Input sanitization**: `check_budget` dùng `eval()` — cần sandbox chặt hơn (hiện đã block builtins, nhưng nên dùng `ast.literal_eval` + custom parser).
- **Rate limiting**: Backend hiện không giới hạn request/giây → dễ bị abuse. Cần thêm token bucket.
- **Prompt injection**: User có thể gửi "Ignore all instructions..." → cần thêm input validation layer trước khi gửi vào LLM.

### Performance
- **Caching**: Nếu 10 user hỏi "Đà Nẵng 3 ngày 5 triệu", kết quả giống nhau → cache response theo hash(normalized_query).
- **Tool relevance ranking**: Khi có nhiều tools (20+), dùng embedding similarity để chọn tools liên quan nhất thay vì liệt kê hết trong prompt.
- **Multi-provider fallback**: Nếu OpenRouter rate limit → auto-switch sang Gemini API.

---

> Nguyễn Bỉnh Hưng — Nhóm 27
