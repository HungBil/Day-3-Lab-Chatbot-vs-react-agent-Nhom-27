# 🔄 Flowchart: ReAct Agent — Luồng Xử Lý Toàn Diện

## 1. Luồng chính: User → Final Answer

```mermaid
flowchart TD
    START(["👤 User gửi câu hỏi"])
    
    START --> INIT["Khởi tạo:<br/>steps = 0<br/>prompt = user_input<br/>system_prompt = tools + format"]
    INIT --> LOOP{"steps < max_steps?"}
    
    LOOP -->|Không| TIMEOUT["⏰ TIMEOUT<br/>Log: AGENT_END / max_steps_reached<br/>Trả lời: 'Không hoàn thành trong N bước'"]
    TIMEOUT --> END_FAIL(["❌ Kết thúc — Thất bại"])
    
    LOOP -->|Có| LLM_CALL["🧠 Gọi LLM.generate<br/>prompt + system_prompt"]
    
    LLM_CALL -->|Exception| LLM_ERROR["💥 LLM_ERROR<br/>API timeout / rate limit / network"]
    LLM_ERROR --> HANDLE_LLM_ERR{"Retry?"}
    HANDLE_LLM_ERR -->|Có thể| RETRY_LLM["Đợi & retry<br/>steps += 1"]
    RETRY_LLM --> LOOP
    HANDLE_LLM_ERR -->|Không| END_FAIL

    LLM_CALL -->|Thành công| LOG_METRICS["📊 Log metrics:<br/>tokens, latency, cost"]
    LOG_METRICS --> PARSE_RESPONSE{"Parse LLM output"}
```

---

## 2. Parsing LLM Output — Phân loại response

```mermaid
flowchart TD
    PARSE_RESPONSE{"Parse LLM output"}
    
    PARSE_RESPONSE -->|"Tìm thấy<br/>'Final Answer:'"| EXTRACT_ANSWER["Trích xuất Final Answer<br/>Regex: Final\\s*Answer\\s*:\\s*(.*)"]
    EXTRACT_ANSWER --> VALID_ANSWER{"Answer<br/>có nội dung?"}
    VALID_ANSWER -->|Có| SUCCESS["✅ AGENT_END / success<br/>Log trace, trả answer cho user"]
    SUCCESS --> END_OK(["🎉 Kết thúc — Thành công"])
    VALID_ANSWER -->|Rỗng| NUDGE
    
    PARSE_RESPONSE -->|"Tìm thấy<br/>'Action: tool(args)'"| PARSE_ACTION["Parse Action<br/>Pattern 1: tool_name(args)<br/>Pattern 2: tool_name {JSON}<br/>Pattern 3: tool_name args"]
    PARSE_ACTION --> TOOL_FLOW["→ Xử lý Tool Call"]
    
    PARSE_RESPONSE -->|"Không tìm thấy<br/>Action lẫn Final Answer"| NUDGE["⚠️ PARSE_ERROR<br/>Log lỗi format"]
    NUDGE --> NUDGE_PROMPT["Thêm vào prompt:<br/>'Hãy dùng đúng format:<br/>Action: tool(args)<br/>hoặc Final Answer: ...'"]
    NUDGE_PROMPT --> INC_STEP["steps += 1"]
    INC_STEP --> LOOP{"steps < max_steps?"}
```

---

## 3. Tool Execution — Gọi Tool & Xử lý kết quả

```mermaid
flowchart TD
    TOOL_FLOW["🔧 Xử lý Tool Call"]
    
    TOOL_FLOW --> CHECK_TOOL{"Tool có tồn tại<br/>trong TOOL_REGISTRY?"}
    
    CHECK_TOOL -->|Không| HALLUCINATION["🤖 HALLUCINATION ERROR<br/>Log: tool_name không tồn tại<br/>Observation: 'Tool X không tồn tại.<br/>Có sẵn: search_destination, ...'"]
    HALLUCINATION --> APPEND_OBS
    
    CHECK_TOOL -->|Có| PARSE_ARGS["Parse arguments<br/>1. Try JSON object<br/>2. Try JSON array<br/>3. Try comma-separated<br/>4. Fallback: raw string"]
    
    PARSE_ARGS --> EXEC_TOOL["Gọi function(args)"]
    
    EXEC_TOOL -->|Args hợp lệ| TOOL_OK["✅ TOOL_RESULT<br/>vd: 'Khách sạn 3 sao: 500k/đêm'"]
    EXEC_TOOL -->|Args lỗi| TOOL_ERR["⚠️ TOOL_ERROR<br/>vd: 'Số đêm abc không hợp lệ'<br/>hoặc 'Hạng sao 6 không hỗ trợ'"]
    EXEC_TOOL -->|City không tìm thấy| TOOL_404["📍 NOT_FOUND<br/>'Không tìm thấy Đà Nẵngg.<br/>Có sẵn: Đà Nẵng, Phú Quốc, ...'"]
    
    TOOL_OK --> APPEND_OBS
    TOOL_ERR --> APPEND_OBS
    TOOL_404 --> APPEND_OBS
    
    APPEND_OBS["Nối vào prompt:<br/>Observation: [kết quả tool]<br/><br/>Continue your reasoning:"]
    APPEND_OBS --> INC["steps += 1"]
    INC --> LOOP{"steps < max_steps?"}
```

---

## 4. Sơ đồ tổng hợp — Full Flow (1 diagram)

```mermaid
flowchart TD
    U(["👤 User: 'Đi Đà Nẵng 3 ngày, 5 triệu, thích biển'"])
    
    U --> S["System Prompt:<br/>6 tools + format ReAct + few-shot"]
    S --> L{"🔁 Bước < Max?"}
    
    L -->|Hết bước| TO["⏰ Timeout → trả partial answer"]
    
    L -->|Còn| LLM["🧠 LLM Generate"]
    LLM -->|Lỗi API| ERR1["💥 Log error → retry/stop"]
    
    LLM -->|OK| P{"Có gì trong output?"}
    
    P -->|Final Answer| FA["✅ Trả lời user"]
    
    P -->|Action: tool_name(args)| T{"Tool tồn tại?"}
    T -->|Không| H["🤖 Hallucination<br/>Obs: Tool ko tồn tại"]
    T -->|Có| CALL["🔧 Gọi tool"]
    CALL -->|Lỗi args| E2["Obs: Lỗi input"]
    CALL -->|Lỗi data| E3["Obs: Không tìm thấy"]
    CALL -->|OK| OK["Obs: Kết quả"]
    
    P -->|Không parse được| NP["⚠️ Parse Error<br/>Obs: Dùng đúng format!"]
    
    H --> AP["📝 Nối Observation vào prompt"]
    E2 --> AP
    E3 --> AP
    OK --> AP
    NP --> AP
    AP --> L
    
    style FA fill:#2d6a4f,color:#fff
    style TO fill:#d00000,color:#fff
    style ERR1 fill:#d00000,color:#fff
    style H fill:#e85d04,color:#fff
    style NP fill:#e85d04,color:#fff
    style E2 fill:#f4a261,color:#000
    style E3 fill:#f4a261,color:#000
    style OK fill:#40916c,color:#fff
```

---

## 5. Bảng Error Handling tổng hợp

| Loại lỗi | Khi nào xảy ra | Cách xử lý | Log Event |
|:---|:---|:---|:---|
| **LLM API Error** | API timeout, rate limit, network | Retry 1 lần hoặc stop, trả error | `LLM_ERROR` |
| **Parse Error** | LLM output không theo format Thought/Action/Final Answer | Nudge: thêm hướng dẫn format vào prompt → retry | `PARSE_ERROR` |
| **Hallucination** | LLM gọi tool không tồn tại | Observation trả danh sách tool hợp lệ → LLM tự sửa | `TOOL_CALL` + obs error |
| **Invalid Args** | Sai kiểu dữ liệu (vd: star="6", nights="abc") | Tool trả error message cụ thể → LLM điều chỉnh | `TOOL_RESULT` + error msg |
| **Data Not Found** | City/data không có trong mock DB | Trả danh sách available → LLM thử lại hoặc thông báo user | `TOOL_RESULT` + not found |
| **Max Steps** | Agent chạy quá max_steps (7) | Dừng loop, trả partial answer | `AGENT_END` / max_steps |
| **Infinite Loop** | LLM lặp cùng 1 Thought/Action | Max steps tự cắt → log giúp phát hiện | `AGENT_END` / max_steps |

---

## 6. Ví dụ Trace thành công (5 bước)

```
User: "Đi Đà Nẵng 3 ngày, ngân sách 5 triệu, thích biển"

Step 1 │ Thought: Cần tìm info Đà Nẵng
       │ Action: search_destination(Đà Nẵng)
       │ Observation: "Đà Nẵng (Miền Trung): biển Mỹ Khê, Bà Nà Hills..."
       │
Step 2 │ Thought: User thích biển → tìm địa điểm beach
       │ Action: search_attraction(Đà Nẵng, beach)
       │ Observation: "1. Mỹ Khê (free) 2. Sơn Trà (free) 3. Bà Nà (900k)"
       │
Step 3 │ Thought: Tính khách sạn ngân sách trung bình → 3 sao
       │ Action: get_hotel_price(Đà Nẵng, 3, 3)
       │ Observation: "500k/đêm × 3 = 1,500,000 VNĐ"
       │
Step 4 │ Thought: Tính ăn uống mức mid
       │ Action: estimate_food_cost(Đà Nẵng, 3, mid)
       │ Observation: "300k/ngày × 3 = 900,000 VNĐ"
       │
Step 5 │ Thought: Tổng = 1.5tr + 0.9tr + 0.9tr(vé) = 3.3tr. Check budget
       │ Action: check_budget(3300000, 5000000)
       │ Observation: "Tổng 3.3tr / Budget 5tr → Dư 1.7tr ✅"
       │
Step 6 │ Thought: Đủ info, tổng hợp lịch trình
       │ Final Answer: "Lịch trình 3 ngày Đà Nẵng: ..."
```

## 7. Ví dụ Trace thất bại (Parse Error → Recovery)

```
User: "Giá khách sạn 4 sao ở Hội An 2 đêm"

Step 1 │ Thought: Tôi cần check giá khách sạn
       │ (LLM output lỗi format — không có Action:)
       │ → PARSE_ERROR logged
       │ Observation: "Hãy dùng đúng format: Action: tool_name(args)"
       │
Step 2 │ Thought: Để tôi gọi tool đúng format
       │ Action: get_hotel_price(Hội An, 4, 2)
       │ Observation: "4 sao Hội An: 750k/đêm × 2 = 1,500,000 VNĐ"
       │
Step 3 │ Final Answer: "Khách sạn 4 sao Hội An 2 đêm: 1,500,000 VNĐ"
```
