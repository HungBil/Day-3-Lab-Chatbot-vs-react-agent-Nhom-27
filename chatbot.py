import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from src.chatbot.travel_chatbot import TravelPlannerChatbot  # noqa: E402

BANNER = """
╔══════════════════════════════════════════════════════════╗
║          ✈  TRAVEL PLANNER CHATBOT  ✈  (Baseline)       ║
║              Powered by Phi-3-mini (Local GGUF)          ║
╠══════════════════════════════════════════════════════════╣
║  Gõ câu hỏi về chuyến đi và nhấn Enter để bắt đầu.      ║
║  Lệnh đặc biệt:                                          ║
║    /reset  — Xóa lịch sử hội thoại                       ║
║    /history — Xem lịch sử hội thoại                      ║
║    /quit   — Thoát chương trình                          ║
╚══════════════════════════════════════════════════════════╝
""".strip()


def print_streamed(chatbot: TravelPlannerChatbot, user_input: str):
    """In phản hồi stream trực tiếp ra terminal."""
    print("\n🤖 TravelBot: ", end="", flush=True)
    for token in chatbot.chat_stream(user_input):
        print(token, end="", flush=True)
    print("\n")


def print_history(chatbot: TravelPlannerChatbot):
    history = chatbot.get_history()
    if not history:
        print("  (Chưa có lịch sử hội thoại)\n")
        return
    print()
    for i, msg in enumerate(history, 1):
        role_label = "👤 Bạn" if msg["role"] == "user" else "🤖 Bot"
        print(f"  [{i}] {role_label}: {msg['content'][:120]}{'...' if len(msg['content']) > 120 else ''}")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    model_path = os.getenv(
        "LOCAL_MODEL_PATH",
        "./models/Phi-3-mini-4k-instruct-q4.gguf"
    )
    if not os.path.isabs(model_path):
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model_path)

    if not os.path.exists(model_path):
        print(f"❌ Lỗi: Không tìm thấy file model tại: {model_path}")
        sys.exit(1)

    print(f"⏳ Đang tải model local: {os.path.basename(model_path)} ...")
    chatbot = TravelPlannerChatbot(
        model_path=model_path,
        stream=True,
    )

    print(BANNER)
    print(f"  Model: {os.path.basename(model_path)}\n")

    while True:
        try:
            user_input = input("👤 Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Tạm biệt! Chúc bạn có chuyến đi vui vẻ!")
            break

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("👋 Tạm biệt! Chúc bạn có chuyến đi vui vẻ!")
            break
        elif user_input.lower() == "/reset":
            chatbot.reset()
            print("✅ Đã xóa lịch sử hội thoại.\n")
            continue
        elif user_input.lower() == "/history":
            print_history(chatbot)
            continue

        print_streamed(chatbot, user_input)


if __name__ == "__main__":
    main()
