# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Khuất Văn Vương
- **Student ID**: 2A202600087
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

### Vai trò: Chatbot Baseline + Streaming Backend + ReAct Agent Co-Developer

Tôi chịu trách nhiệm xây dựng toàn bộ luồng Chatbot Baseline (streaming), tích hợp OpenRouter provider, phát triển backend FastAPI với Server-Sent Events, và tham gia thiết kế vòng lặp ReAct cho Agent v2.

### Modules Implemented

#### 1. `src/chatbot/travel_chatbot.py` — Chatbot Baseline (Streaming)

Xây dựng module chatbot với kiến trúc tách biệt giữa logic hội thoại và LLM provider:

- **System prompt engineering**: Thiết kế prompt chuyên biệt cho tư vấn du lịch Việt Nam, bao gồm persona "travel expert", tone thân thiện, và knowledge base cơ bản về các điểm đến phổ biến.
- **Streaming generator**: Dùng Python generator (`yield`) để stream từng token từ LLM → người dùng thấy text xuất hiện real-time thay vì chờ toàn bộ response. Điều này cải thiện UX đáng kể — latency cảm nhận giảm từ ~5s xuống ~0.5s.
- **Provider abstraction**: Tách biệt cấu trúc giữa provider và chatbot → dễ dàng swap model (Qwen, Phi-3, GPT) mà không sửa logic hội thoại.

```python
def stream_response(self, user_message: str):
    messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": user_message}
    ]
    for chunk in self.provider.stream(messages):
        yield chunk
```

#### 2. `src/core/openrouter_provider.py` — OpenRouter API Integration

Xây dựng module kết nối API OpenRouter với các tính năng:

- **Streaming support**: Implement `stream()` method dùng `requests` với `stream=True` để đọc Server-Sent Events từ OpenRouter API.
- **Multi-model compatibility**: Hỗ trợ nhiều model miễn phí trên OpenRouter (Qwen, Phi-3, Mistral) thông qua cùng 1 interface.
- **Error handling**: Xử lý các lỗi HTTP 400 (invalid model), 429 (rate limit), 404 (model not found) với retry logic.
- **Token tracking**: Parse `usage` field từ response để theo dõi prompt_tokens, completion_tokens cho telemetry.

#### 3. `app.py` & `services/frontend/chat.html` — Backend + Frontend Streaming

Thiết lập backend FastAPI và frontend integration:

- **`/chat/stream` endpoint**: Dùng `StreamingResponse` (FastAPI) để push Server-Sent Events cho frontend.
- **Vanilla JS Fetch API**: Frontend đọc `ReadableStream` từ `/chat/stream`, parse từng chunk và append vào DOM real-time.
- **Tách biệt endpoint**: Streaming endpoint cho chatbot baseline, REST endpoint cho Agent mode.

```javascript
const response = await fetch("/chat/stream", {
  method: "POST",
  body: JSON.stringify({ message }),
});
const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  appendToChat(new TextDecoder().decode(value));
}
```

#### 4. `src/agent/agent.py` — ReAct Agent (Co-Developer)

Tham gia thiết kế và triển khai vòng lặp ReAct:

- **Vòng lặp xử lý**: Thiết kế luồng `Thought → Action → Observation → (loop)` với `max_steps` limit để tránh infinite loop.
- **Response parsing**: Viết regex parser để trích xuất `Action: tool_name(arg1, arg2)` từ LLM output, hỗ trợ cả format `tool {json}`.
- **Observation injection**: Nối kết quả tool execution trở lại prompt dưới dạng `Observation: [result]` để LLM tiếp tục reasoning.
- **Final Answer detection**: Phát hiện pattern `Final Answer:` để kết thúc loop và trả kết quả cho user.

### Code Interaction với ReAct Loop

Phần chatbot baseline và streaming backend tạo nền tảng so sánh A/B testing:

- **Chatbot baseline**: Gọi LLM trực tiếp, 1 lần, không tools → response nhanh nhưng có thể hallucinate.
- **Agent mode**: Dùng ReAct loop tôi tham gia thiết kế → response chậm hơn nhưng chính xác nhờ tools.

Hai mode này chạy trên cùng 1 giao diện, cùng 1 model, chỉ khác kiến trúc → tạo điều kiện so sánh công bằng.

---

## II. Debugging Case Study (10 Points)

### Case 1: LLM Hallucinate Observation

- **Problem Description**: LLM không dừng lại sau khi sinh `Action`, mà tự sinh luôn cả `Observation` và `Final Answer`. Kết quả là ReAct loop bị phá vỡ — agent trả về kết quả tự bịa mà không hề gọi function calling thực tế.

- **Log Source**:

```text
Step 1:
  Thought: Tôi cần tìm chi phí khách sạn 3 sao tại Đà Nẵng cho 3 đêm.
  Action: get_hotel_price("Đà Nẵng", "3", "3")
  Observation: Khách sạn 3 sao tại Đà Nẵng giá 500,000 VNĐ/đêm.
              Tổng chi phí là 1,500,000 VNĐ. Gợi ý: Zen Diamond, Fivitel.
  ← (LLM tự sinh dòng này, KHÔNG phải tool trả về!)
  Final Answer: Chi phí khách sạn 3 sao cho 3 đêm là 1,500,000 VNĐ.
```

- **Diagnosis**: Xảy ra do 2 nguyên nhân gốc rễ:
  1. **System prompt thiếu ràng buộc dừng**: Prompt chỉ nói "use tools when needed" mà không có lệnh dừng cứng kiểu "STOP immediately after Action line. Do NOT generate Observation yourself."
  2. **Thiếu stop sequence**: Không set `stop=["Observation:"]` trong API request → LLM tiếp tục sinh text qua ranh giới Action/Observation.
  3. **Hệ quả**: Parser trích xuất Final Answer từ text LLM tự sinh → trả kết quả sai mà không có cảnh báo. Tệ hơn, số liệu "500,000 VNĐ/đêm" có thể đúng hoặc sai vì nó là hallucination, không phải data từ tool.

- **Solution (2 bước)**:
  1. **Cập nhật System Prompt**: Thêm ràng buộc cứng:
     ```
     CRITICAL: After writing "Action: tool_name(args)", you MUST STOP IMMEDIATELY.
     Do NOT write "Observation:" yourself. The system will provide the Observation.
     ```
  2. **Thêm stop sequence**: Khi gọi API, bổ sung `stop=["Observation:"]` → API tự động cắt response ngay khi model chuẩn bị sinh "Observation:", nhường quyền điều khiển lại cho script ReAct.

- **Kết quả sau fix**: Agent dừng đúng sau Action, chờ tool thực thi, nhận Observation thật → kết quả chính xác 100% từ data source.

### Case 2: Streaming Frontend

- **Problem Description**: Khi stream response tiếng Việt (có dấu), một số ký tự Unicode bị tách ra thành 2 chunk → text hiển thị sai trên FE.
- **Diagnosis**: `TextDecoder` mặc định không buffer multi-byte UTF-8 characters. Ký tự tiếng Việt dùng 2-3 bytes, nếu chunk cắt giữa → decode sai.
- **Solution**: Dùng `TextDecoder` với option `{stream: true}` để buffer incomplete multi-byte sequences qua các chunk liên tiếp:
  ```javascript
  const decoder = new TextDecoder("utf-8", { stream: true });
  ```

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning

Chatbot baseline sinh phản hồi theo cơ chế **next-token prediction** liên tục — nó không có bước dừng lại để "suy nghĩ". Khi nhận câu hỏi phức tạp ("Đà Nẵng 3 ngày, biển, 5 triệu"), chatbot cố gắng trả lời một lèo, dẫn đến:

- **Hallucination**: Bịa giá khách sạn 800k/đêm (thực tế data trả về 500k)
- **Thiếu tính toán**: Không cộng tổng chi phí, chỉ liệt kê chung chung.

ReAct agent buộc LLM phải viết khối **Thought** trước mỗi hành động. Điều này tạo ra hiệu ứng **Chain-of-Thought decomposition** — model tự phân rã yêu cầu phức tạp thành các bước nhỏ:

```
Thought: Cần biết giá KS → gọi get_hotel_price
Thought: Cần biết chi phí ăn → gọi estimate_food_cost
Thought: Cộng tổng và so với ngân sách → gọi check_budget
```

Kết quả: Agent trả lời với **số liệu cụ thể, có nguồn từ tool**, thay vì ước chừng.

### 2. Reliability

Chatbot truyền thống vượt trội hơn về độ nhanh nhạy và ổn định khi hỏi đáp thông thường. ReAct agent đôi lúc gặp rủi ro nếu Action sinh ra sai format, tool gặp lỗi mạng, hoặc sinh ra infinite loop do liên tục gọi cùng một tool không trả ra kết quả. |

**Insight quan trọng**: Chatbot phù hợp cho **hỏi đáp nhanh, general knowledge**. Agent phù hợp cho **task cần tính toán, tra cứu, multi-step reasoning**. Trong production, nên dùng **router layer** để phân loại query trước khi chọn mode.

### 3. Observation

Observation là thành phần **biến LLM từ "người trả lời" thành "người giải quyết vấn đề"**. Cụ thể:

- Khi tool trả `"No destination data found for 'Đà Nẵng'"` → LLM tự hiểu lỗi encoding → bước tiếp gọi `search_destination("Da Nang")` → thành công.
- Khi tool trả `"Invalid number format"` → LLM tự tính `1500000 + 900000 = 2400000` → gọi lại `check_budget(2400000, 5000000)` → thành công.

Điều này cho thấy: **error message chất lượng = agent tự chữa lành**. Nếu tool chỉ trả "Error" chung chung, LLM không có thông tin để adapt. Design principle: **mỗi tool error phải nói rõ LÝ DO lỗi để agent tự sửa**.

---

## IV. Future Improvements (5 Points)

### Scalability

- **Message broker architecture**: Hiện tại các tool call chạy synchronous. Trong production với nhiều user đồng thời, cần tách tool execution qua message queue (Redis Queue hoặc Celery) để không block main thread.
- **Real-time data integration**: Kết nối với API thật (Skyscanner, Agoda, Google Places) thay vì mock data → Agent có data coverage rộng hơn, không bị "No data found" cho các thành phố mới.
- **Horizontal scaling**: Tách backend thành microservices: API Gateway → Agent Service → Tool Service → LLM Service. Mỗi service scale independent.

### Safety

- **Supervisor LLM**: Triển khai một LLM "giám sát" kiểm tra mỗi Action trước khi execute. Ví dụ: nếu Agent cố gọi tool với argument chứa SQL injection hoặc shell command → Supervisor chặn.
- **Pydantic validation**: Validate chặt input/output của mỗi tool bằng Pydantic schema. Hiện tại tool nhận raw string → dễ bị injection. Với Pydantic, format sai → reject ngay trước khi execute.
- **Cost guardrail**: Set budget limit (VD: max $0.10/session). Nếu tổng token usage vượt threshold → dừng agent, trả partial answer. Tránh trường hợp infinite loop tốn credit.

### Performance

- **Caching layer (Redis + Vector DB)**: Cache kết quả tool theo query hash. Nếu 10 user hỏi "Đà Nẵng 3 ngày 2 đêm", hệ thống trả cache thay vì chạy lại 5-6 tool calls. Dùng Vector DB (Qdrant/Pinecone) cho semantic matching — "Đà Nẵng 3 ngày" ≈ "Da Nang 3 days" → cache hit.
- **Tool relevance ranking**: Khi hệ thống có 20+ tools, không nên liệt kê tất cả trong prompt (tốn tokens). Dùng embedding similarity để chọn top-K tools liên quan nhất cho mỗi query → giảm prompt size 60-70%.
- **Parallel tool calls**: Khi so sánh 2 destinations, có thể gọi `search_destination("Da Nang")` và `search_destination("Nha Trang")` song song thay vì tuần tự → giảm 50% latency cho compare queries.

---
