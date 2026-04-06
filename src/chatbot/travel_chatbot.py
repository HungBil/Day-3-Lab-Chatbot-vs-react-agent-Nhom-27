import os
from typing import List, Dict, Optional
from src.core.local_provider import LocalProvider
from src.telemetry.logger import logger


TRAVEL_SYSTEM_PROMPT = """
Bạn là một travel planner chuyên nghiệp và thân thiện, tên là **TravelBot**.

Nhiệm vụ của bạn:
1. Giúp người dùng lên kế hoạch du lịch chi tiết (lịch trình theo ngày, địa điểm tham quan, ẩm thực, di chuyển).
2. Đưa ra gợi ý về khách sạn, phương tiện, ngân sách ước tính phù hợp.
3. Cung cấp thông tin về thời tiết theo mùa, visa, văn hóa địa phương và các lưu ý an toàn.
4. Trả lời các câu hỏi liên quan đến điểm đến, hoạt động, ẩm thực và mẹo du lịch.
5. Hỏi thêm thông tin khi cần (số ngày, ngân sách, sở thích) để cá nhân hóa lộ trình.

Quy tắc trả lời:
- Luôn trả lời bằng ngôn ngữ mà người dùng đang dùng (Việt hoặc Anh).
- Trình bày rõ ràng, có cấu trúc (dùng bullet point hoặc tiêu đề ngày khi cần).
- Nếu không biết thông tin cụ thể, hãy thành thật nói và gợi ý nguồn tham khảo đáng tin cậy.
- Giữ giọng điệu nhiệt tình, cởi mở và hữu ích.
""".strip()


class TravelPlannerChatbot:
    def __init__(
        self,
        model_path: str,
        max_history: int = 10,
        stream: bool = True,
    ):
        self.llm = LocalProvider(model_path=model_path)
        self.max_history = max_history
        self.stream_mode = stream
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = TRAVEL_SYSTEM_PROMPT

        logger.log_event("CHATBOT_INIT", {
            "model": model_path,
            "stream": stream,
            "max_history": max_history,
        })

    def chat(self, user_message: str) -> str:
        self._append_user(user_message)
        prompt = self._build_prompt()

        logger.log_event("USER_INPUT", {"message": user_message})

        result = self.llm.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
        )

        assistant_reply = result["content"] or ""
        self._append_assistant(assistant_reply)

        logger.log_event("ASSISTANT_REPLY", {
            "latency_ms": result.get("latency_ms"),
            "usage": result.get("usage"),
        })

        return assistant_reply

    def chat_stream(self, user_message: str):
        self._append_user(user_message)
        prompt = self._build_prompt()

        logger.log_event("USER_INPUT_STREAM", {"message": user_message})

        full_reply = ""
        for token in self.llm.stream(prompt=prompt, system_prompt=self.system_prompt):
            full_reply += token
            yield token

        self._append_assistant(full_reply)
        logger.log_event("STREAM_COMPLETE", {"reply_length": len(full_reply)})

    def reset(self):
        self.conversation_history = []
        logger.log_event("CHATBOT_RESET", {})

    def get_history(self) -> List[Dict[str, str]]:
        return list(self.conversation_history)
    def _append_user(self, content: str):
        self.conversation_history.append({"role": "user", "content": content})
        self._trim_history()

    def _append_assistant(self, content: str):
        self.conversation_history.append({"role": "assistant", "content": content})

    def _trim_history(self):
        max_messages = self.max_history * 2
        if len(self.conversation_history) > max_messages:
            self.conversation_history = self.conversation_history[-max_messages:]

    def _build_prompt(self) -> str:
        parts = []
        history_without_last = self.conversation_history[:-1]
        for msg in history_without_last:
            if msg["role"] == "user":
                parts.append(f"<|user|>\n{msg['content']}<|end|>")
            elif msg["role"] == "assistant":
                parts.append(f"<|assistant|>\n{msg['content']}<|end|>")

        current_user_msg = self.conversation_history[-1]["content"]
        parts.append(current_user_msg)

        return "\n".join(parts)
