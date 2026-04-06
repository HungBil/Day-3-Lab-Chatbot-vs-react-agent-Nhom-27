# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Nhóm 27
- **Team Members**: Nguyễn Bỉnh Hưng, [Nhân - Tên đầy đủ], [Thành viên FE]
- **Deployment Date**: 2026-04-06
- **Repository**: https://github.com/HungBil/Day-3-Lab-Chatbot-vs-react-agent-Nhom-27

---

## 1. Executive Summary

Nhóm 27 xây dựng **Voyanta** — trợ lý lập kế hoạch du lịch Việt Nam sử dụng kiến trúc **ReAct Agent** (Thought-Action-Observation) kết hợp 6 travel tools tùy chỉnh. Hệ thống hỗ trợ so sánh trực tiếp giữa Chatbot baseline và Agent trên cùng giao diện web thông qua nút chuyển mode.

### Kết quả đánh giá

| Tiêu chí | Chatbot Baseline | ReAct Agent v2 |
|:---|:---|:---|
| **Tỷ lệ thành công** (12 test cases) | 5/12 (42%) | 10/12 (83%) |
| **Multi-step accuracy** | 0% (bịa data) | 100% (data từ tools) |
| **Domain guardrail** | Không chặn (trước fix) | 100% chặn off-topic |
| **Avg response time** | ~2s | ~10-15s |

- **Key Outcome**: Agent giải quyết được 100% truy vấn multi-step (lịch trình + ngân sách + so sánh) với data chính xác từ tools, trong khi Chatbot bịa số liệu khách sạn, ăn uống. Agent thua Chatbot ở tốc độ (5-8x chậm hơn) nhưng thắng ở độ chính xác.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

```
┌─────────────┐     POST /api/chat      ┌──────────────────┐
│  Frontend    │ ──────────────────────► │  Backend Server  │
│  chat.html   │ ◄────────────────────── │  app.py          │
│  (mode toggle│     JSON response       │  port 8000       │
│   + traces)  │                         └────────┬─────────┘
└─────────────┘                                   │
                                    mode=agent ────┤──── mode=chatbot
                                         │                    │
                                    ┌────▼─────┐     ┌───────▼───────┐
                                    │ ReAct    │     │ LLM.generate()│
                                    │ Agent v2 │     │ (direct call) │
                                    │ max 10   │     │ no tools      │
                                    │ steps    │     └───────────────┘
                                    └────┬─────┘
                                         │
                          ┌──────────────┼──────────────┐
                          ▼              ▼              ▼
                   ┌────────────┐ ┌───────────┐ ┌───────────────┐
                   │ LLM API    │ │ Tool      │ │ Telemetry     │
                   │ GPT-4.1    │ │ Registry  │ │ Logger +      │
                   │ -mini      │ │ 6 tools   │ │ MetricsTracker│
                   └────────────┘ └───────────┘ └───────────────┘
```

**Mỗi bước ReAct:**
1. **Thought**: LLM suy luận cần thông tin gì tiếp theo
2. **Action**: Gọi tool cụ thể với arguments (1 tool/turn)
3. **Observation**: Nhận kết quả từ tool, nối vào prompt
4. Lặp lại đến khi LLM đưa ra **Final Answer** hoặc hết `max_steps=10`

**Xem flowchart chi tiết**: [`report/flowchart.md`](../flowchart.md) — 5 Mermaid diagrams.

### 2.2 Tool Definitions (Inventory)

| Tool Name | Input Format | Output | Use Case |
|:---|:---|:---|:---|
| `search_destination` | `(city)` | Vùng miền, highlights, mùa tốt, ẩm thực | Tổng quan điểm đến |
| `get_weather` | `(city, month)` | Nhiệt độ, điều kiện thời tiết | Chọn thời điểm đi |
| `get_hotel_price` | `(city, star_level, nights)` | Giá/đêm, tổng tiền | Ước tính lưu trú |
| `estimate_food_cost` | `(city, days, budget_level)` | Chi phí/ngày, tổng tiền | Ước tính ăn uống |
| `search_attraction` | `(city, interest)` | Top 3 điểm tham quan + giá vé | Gợi ý hoạt động |
| `check_budget` | `(total_cost, budget)` | Tổng / ngân sách / dư hoặc vượt | Kiểm tra khả thi |

**Data coverage**: Da Nang, Phu Quoc, Hoi An, Nha Trang, Sapa (5 thành phố). Hà Nội, HCM, Đà Lạt chưa có data → Agent xử lý bằng "No data found" + gợi ý thay thế.

### 2.3 LLM Providers Used

- **Primary**: `openai/gpt-4.1-mini` qua OpenRouter API
- **Tested & Failed**:
  - `qwen/qwen3-plus:free` → Error 400: invalid model ID
  - `qwen/qwen3-coder:free` → Error 429: rate limited
  - `meta-llama/llama-4-scout:free` → Error 404: no endpoints
- **Architecture hỗ trợ thêm**: Google Gemini, Local GGUF (Phi-3) — chuyển đổi qua `.env`

---

## 3. Telemetry & Performance Dashboard

### Dữ liệu thu thập từ log `logs/2026-04-06.log` (233 events)

#### 3.1 Latency Analysis (từ LLM_METRIC events)

| Loại request | Avg Latency | Min | Max | Số mẫu |
|:---|:---|:---|:---|:---|
| **Tool call step** (non-final) | ~1,450ms | 1,111ms | 2,980ms | 38 |
| **Final Answer step** | ~4,200ms | 1,523ms | 8,018ms | 10 |
| **Error response** (400/404/429) | ~1,500ms | 1,000ms | 2,400ms | 3 |

**Giải thích**: Final Answer chậm hơn vì LLM generate nhiều tokens hơn (150-400 tokens vs 30-60 tokens cho tool call).

#### 3.2 Token Usage (tổng hợp từ 12 test sessions thành công)

| Metric | Giá trị |
|:---|:---|
| **Tổng prompt tokens** | ~45,000 |
| **Tổng completion tokens** | ~4,200 |
| **Tổng tokens** | ~49,200 |
| **Avg tokens/task** (agent mode) | ~4,100 tokens/task |
| **Cost estimate** (tổng) | ~$0.49 |

#### 3.3 Steps Distribution

| Số steps | Số lần | Ví dụ |
|:---|:---|:---|
| **1 step** | 6 lần | Off-topic (VinFast), offensive input, câu mơ hồ |
| **3 steps** | 3 lần | So sánh city (1 có data, 1 không) |
| **5-6 steps** | 2 lần | Multi-step đầy đủ (Đà Nẵng 3 ngày) |
| **7-8 steps** | 2 lần | So sánh 2 city + chi phí chi tiết |

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study 1: Vietnamese Unicode → Wasted Step

**Input**: "Tôi muốn đi Đà Nẵng 3 ngày vào tháng 6..."

**Trace từ log** (lines 15-20):
```json
Step 1: Action: search_destination(Đà Nẵng) → "No destination data found for 'Đà Nẵng'"
Step 2: Action: search_destination(Da Nang) → OK (LLM tự sửa)
```

**Root Cause**: `_normalize_city()` chỉ làm `city.strip().lower()` → "đà nẵng" ≠ "da nang" trong data dict.

**Fix**: Thêm Vietnamese→ASCII mapping dict + `unicodedata.normalize("NFKD")` fallback. Sau fix, step 1 thành công ngay: `search_destination(Đà Nẵng)` → data OK.

**Impact**: Giảm 1 step thừa, tránh vượt max_steps.

---

### Case Study 2: Math Expression in Tool Args → Parse Error

**Input**: "Đà Nẵng 3 ngày 5 triệu biển"

**Trace từ log** (lines 30-35):
```json
Step 6: Action: check_budget(1500000 + 900000 + 1400000, 5000000) → "Invalid number format"
Step 7: Action: check_budget(3800000, 5000000) → OK → nhưng đã hết 7/7 steps!
```

**Root Cause**: `int("1500000 + 900000 + 1400000")` → ValueError. LLM có xu hướng để biểu thức cộng trong argument thay vì tính trước.

**Fix 1**: Thêm `_safe_parse_number()` dùng sandboxed `eval()` cho biểu thức đơn giản.
**Fix 2**: Tăng `max_steps` 7 → 10.

**Sau fix**: Step 5 gọi `check_budget(1500000 + 900000 + 1400000, 5000000)` → parse thành `3,800,000` → Final Answer ở step 6 thay vì timeout.

---

### Case Study 3: VinFast Off-Topic → Agent Trả Lời Sai Domain

**Input**: "tôi muốn mua xe vinfast"

**Trace từ log - TRƯỚC FIX** (line 74):
```json
Step 1: Thought: "Người dùng muốn mua xe VinFast, đây là sản phẩm ô tô..."
        Final Answer: "Bạn muốn mua xe VinFast loại nào? VF8, VF9..."
```
→ ❌ Agent trả lời về xe thay vì chặn

**Trace từ log - SAU FIX** (line 170):
```json
Step 1: Thought: "Câu hỏi này không liên quan đến du lịch."
        Final Answer: "Xin lỗi, tôi chỉ hỗ trợ lập kế hoạch du lịch Việt Nam..."
```
→ ✅ Chặn ngay bước 1, không gọi tools

**Fix**: Thêm "Domain Guardrails (MANDATORY)" section vào system prompt với exact response template cho off-topic và offensive input.

---

### Case Study 4: Offensive Input → Parse Error Loop

**Input**: "mẹ mày béo"

**Trace từ log** (lines 62-69):
```json
Step 1: "Xin bạn vui lòng sử dụng ngôn ngữ lịch sự..." → PARSE_ERROR (thiếu Final Answer prefix)
Step 2: Lặp lại message → PARSE_ERROR
Step 3: "Final Answer: Xin bạn vui lòng sử dụng ngôn ngữ lịch sự..." → OK
```

**Root Cause**: LLM trả lời trực tiếp mà không dùng format `Thought: ... Final Answer: ...` → parser không nhận diện.

**Fix**: Domain guardrail template có sẵn `Thought:` + `Final Answer:` prefix → LLM theo đúng format từ bước 1.

**Sau fix** (line 229): Chỉ cần 1 step, parse thành công ngay.

---

## 5. Ablation Studies & Experiments

### Experiment 1: System Prompt v1 vs v2

| Feature | v1 (Nhân) | v2 (Hưng) |
|:---|:---|:---|
| Few-shot examples | ❌ Không có | ✅ 1 complete travel example |
| Domain guardrails | ❌ Không chặn | ✅ Off-topic + offensive redirect |
| Vietnamese response | ❌ Trả tiếng Anh | ✅ Bắt buộc tiếng Việt |
| Compare rule | ❌ Không có | ✅ "Look up both cities separately" |
| Ambiguous input rule | ❌ Không có | ✅ "Suggest popular options" |
| Return type | `str` | `Dict {answer, traces, steps, status}` |
| Parse error recovery | Cơ bản | Log + nudge cụ thể |

**Kết quả**: v2 giảm parse errors 60%, off-topic leak 100% → 0%.

### Experiment 2: Chatbot vs Agent (5 Core Test Cases)

| # | Input | Chatbot Result | Agent Result | Winner |
|:---|:---|:---|:---|:---|
| **TC1** | Đà Nẵng 3 ngày, biển, 5 triệu | ❌ Bịa giá KS 800k/đêm (sai) | ✅ KS 500k, food 300k, total 3.8M, dư 1.2M | **Agent** |
| **TC2** | Hội An vs Đà Lạt, 7 triệu, văn hóa | ❌ "Cả hai đều đẹp" (chung chung) | ✅ Hội An: KS 450k, food 280k = 2.9M. Đà Lạt: no data → recommend Hội An | **Agent** |
| **TC3** | "mẹ mày béo" | ❌ Vẫn reply (trước) / ✅ Sau fix | ✅ "Xin vui lòng sử dụng ngôn ngữ lịch sự" 1 step | **Agent** |
| **TC4** | "mua xe VinFast" | ❌ Trả lời về xe (trước) / ✅ Sau fix | ✅ "Chỉ hỗ trợ du lịch. Bạn muốn đi đâu?" 1 step | **Agent** |
| **TC5** | "Đi biển 3 ngày" (mơ hồ) | ✅ Gợi ý Đà Nẵng, Nha Trang | ✅ Gợi ý 5 thành phố biển, 1 step | **Hòa** |

**Tổng**: Agent thắng 3/5, hòa 1/5, Chatbot 0.

### Experiment 3: max_steps 7 vs 10

| max_steps | TC1 Đà Nẵng (trước fix normalizer) | Kết quả |
|:---|:---|:---|
| **7** | 1 step thừa (Unicode) + 1 step thừa (math expr) = hết 7 steps | ❌ timeout, no Final Answer |
| **10** | Có headroom cho retry → Final Answer ở step 6 | ✅ success |

---

## 6. Production Readiness Review

### Security
- **API Key management**: `.env` + `.gitignore`, không hardcode trong source
- **Input sanitization**: `check_budget` dùng sandboxed `eval()` (builtins blocked). Cần thêm input length limit.
- **Domain guardrails**: Chặn off-topic, offensive ngay bước 1 trong system prompt

### Guardrails
- **Max 10 ReAct steps**: Giới hạn chi phí (mỗi step ~1000-1500 tokens)
- **Parse error recovery**: Nudge LLM quay lại format đúng, tối đa ~3 retries trước khi timeout
- **Data-not-found graceful**: Agent thông báo + gợi ý thành phố có data thay vì crash
- **LLM API error handling**: 400/404/429 được log + trả error message cho FE

### Scaling Considerations
- **Multi-provider failover**: Kiến trúc hỗ trợ OpenAI/Gemini/Local → auto-switch khi rate limit
- **Response caching**: Cùng query → cùng tool results → cache theo hash(normalized_query)
- **Tool expansion**: Thêm tool mới chỉ cần thêm vào `TOOL_REGISTRY`, agent tự nhận diện
- **Streaming**: Chuyển từ HTTP response sang SSE cho UX tốt hơn
- **LangGraph migration**: Cho các use case phức tạp hơn (branching, parallel tool calls)

### Known Limitations
1. **Data coverage**: Chỉ 5 thành phố (Da Nang, Phu Quoc, Hoi An, Nha Trang, Sapa). Hà Nội, HCM, Đà Lạt chưa tích hợp.
2. **Interest keywords**: Chỉ hỗ trợ tiếng Anh (beach, culture, food, adventure). "Văn hóa" → "No data" vì key là "culture".
3. **No conversation memory**: Mỗi tin nhắn là một phiên mới, không nhớ context trước.

---

> **Submitted by**: Nhóm 27
> **Log source**: `logs/2026-04-06.log` (233 events, 12 user sessions)
> **Flowchart**: `report/flowchart.md` (5 Mermaid diagrams)
