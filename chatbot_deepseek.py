"""
chatbot_deepseek.py
-------------------
一个简单的命令行 Chatbot，演示如何调用 DeepSeek 模型（OpenAI 兼容接口）。
同时支持通过火山引擎（火山方舟 ARK）调用 DeepSeek 兼容模型。

运行方式:
    python chatbot_deepseek.py                      # 默认使用 DeepSeek 官方 API
    python chatbot_deepseek.py --provider ark        # 使用火山引擎 ARK API
    python chatbot_deepseek.py --provider deepseek   # 使用 DeepSeek 官方 API（显式）
    python chatbot_deepseek.py --no-stream           # 关闭流式输出

环境变量:
    DEEPSEEK_API_KEY   : DeepSeek 官方 API Key
    ARK_API_KEY        : 火山引擎 API Key
    ARK_MODEL_ID       : 火山引擎模型 endpoint_id（如 ep-xxxxxxxx）
"""

import os
import sys
import argparse
from typing import List, Dict

# ---------------------------------------------------------------------------
# 依赖检查
# ---------------------------------------------------------------------------
try:
    from openai import OpenAI
except ImportError:
    print("[错误] 未找到 openai 包，请先运行: pip install openai")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    USE_RICH = True
except ImportError:
    USE_RICH = False

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

# ① DeepSeek 官方 API（OpenAI 兼容）
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL    = "deepseek-chat"        # 或 "deepseek-reasoner"

# ② 火山引擎 ARK（OpenAI 兼容）
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
# ARK_MODEL_ID 从环境变量读取，格式: ep-xxxxxxxx-xxxxx

SYSTEM_PROMPT = (
    "You are a helpful assistant. "
    "请用中文回答用户问题，除非用户用其他语言提问。"
)


# ---------------------------------------------------------------------------
# Chatbot 类
# ---------------------------------------------------------------------------

class DeepSeekChatbot:
    """封装对话历史并调用 DeepSeek/ARK 兼容 API。"""

    def __init__(self, provider: str = "deepseek", stream: bool = True):
        self.provider = provider
        self.stream   = stream
        self.history: List[Dict[str, str]] = []
        self.client, self.model = self._build_client()
        self.console = Console() if USE_RICH else None

    # ------------------------------------------------------------------
    # 初始化客户端
    # ------------------------------------------------------------------
    def _build_client(self):
        if self.provider == "ark":
            api_key  = os.environ.get("ARK_API_KEY", "").strip()
            model_id = os.environ.get("ARK_MODEL_ID", "").strip()
            if not api_key:
                raise EnvironmentError(
                    "使用火山引擎时，请设置环境变量 ARK_API_KEY。\n"
                    "示例: export ARK_API_KEY='your-ark-key'"
                )
            if not model_id:
                raise EnvironmentError(
                    "使用火山引擎时，请设置环境变量 ARK_MODEL_ID。\n"
                    "示例: export ARK_MODEL_ID='ep-xxxxxxxx-xxxxx'"
                )
            client = OpenAI(api_key=api_key, base_url=ARK_BASE_URL)
            return client, model_id

        else:  # deepseek
            api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
            if not api_key:
                raise EnvironmentError(
                    "请设置环境变量 DEEPSEEK_API_KEY。\n"
                    "示例: export DEEPSEEK_API_KEY='sk-xxxxxxxx'"
                )
            client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
            return client, DEEPSEEK_MODEL

    # ------------------------------------------------------------------
    # 发送消息并获取回复
    # ------------------------------------------------------------------
    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history

        if self.stream:
            return self._chat_stream(messages)
        else:
            return self._chat_sync(messages)

    def _chat_sync(self, messages: List[Dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def _chat_stream(self, messages: List[Dict]) -> str:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        )

        chunks = []
        print("\n🤖 Assistant: ", end="", flush=True)
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                chunks.append(delta.content)
        print()  # 换行

        reply = "".join(chunks)
        self.history.append({"role": "assistant", "content": reply})
        return reply

    # ------------------------------------------------------------------
    # 对话循环
    # ------------------------------------------------------------------
    def run(self):
        provider_label = "火山引擎 ARK" if self.provider == "ark" else "DeepSeek 官方 API"
        print("=" * 60)
        print(f"  🚀  DeepSeek Chatbot  |  Provider: {provider_label}")
        print(f"  Model: {self.model}")
        print("  输入 'quit' 或 'exit' 退出，输入 'clear' 清空对话历史")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n👤 You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 再见！")
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit"):
                print("👋 再见！")
                break
            if user_input.lower() == "clear":
                self.history.clear()
                print("✅ 对话历史已清空。")
                continue

            try:
                if not self.stream:
                    reply = self.chat(user_input)
                    print(f"\n🤖 Assistant: {reply}")
                else:
                    self.chat(user_input)   # 流式输出已在内部打印
            except Exception as e:
                print(f"\n[API 错误] {e}")


# ---------------------------------------------------------------------------
# 单次调用示例（非交互）
# ---------------------------------------------------------------------------

def single_query_example(provider: str = "deepseek"):
    """演示单次问答：发送问题 → 调用模型 → 打印回复。"""
    bot = DeepSeekChatbot(provider=provider, stream=False)
    question = "用一句话解释什么是大语言模型（LLM）？"
    print(f"\n[单次示例] 问题: {question}")
    answer = bot.chat(question)
    print(f"[单次示例] 回复: {answer}\n")


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="DeepSeek Chatbot Demo")
    parser.add_argument(
        "--provider",
        choices=["deepseek", "ark"],
        default="deepseek",
        help="API 提供方: deepseek（官方）或 ark（火山引擎）",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="禁用流式输出，改为一次性返回完整回复",
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="仅运行单次问答示例（非交互模式）",
    )
    args = parser.parse_args()

    if args.example:
        single_query_example(provider=args.provider)
        return

    bot = DeepSeekChatbot(provider=args.provider, stream=not args.no_stream)
    bot.run()


if __name__ == "__main__":
    main()
