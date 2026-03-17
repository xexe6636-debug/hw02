# hw02 — DeepSeek Chatbot 示例

> 一个最小可运行的命令行 Chatbot，演示如何通过 **DeepSeek 官方 API** 或 **火山引擎（ARK）** 调用 DeepSeek 模型完成多轮对话。

---

## 目录结构

```
hw02/
├── chatbot_deepseek.py   # 主程序（单文件，含完整注释）
├── requirements.txt      # Python 依赖
└── README.md             # 本文件
```

---

## 采用的 API / 平台

| 方案 | 提供方 | Base URL | 接口协议 |
|------|--------|----------|----------|
| 方案 A（默认） | DeepSeek 官方 | `https://api.deepseek.com` | OpenAI 兼容 |
| 方案 B | 火山引擎（火山方舟 ARK） | `https://ark.cn-beijing.volces.com/api/v3` | OpenAI 兼容 |

两种方案均使用 `openai` Python SDK，仅需切换 `base_url` 和 `api_key`。

---

## 运行环境

- Python **3.9+**（推荐 3.11）
- 已安装 `pip`

---

## 安装依赖

```bash
pip install -r requirements.txt
```

> `openai` 为必须依赖；`rich` 为可选（美化输出），缺失时自动降级为纯文本。

---

## 配置 API Key

### 方案 A：DeepSeek 官方 API

1. 前往 [https://platform.deepseek.com](https://platform.deepseek.com) 注册并创建 API Key。
2. 设置环境变量：

```bash
# Linux / macOS
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"

# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

### 方案 B：火山引擎（ARK）

1. 登录 [https://console.volcengine.com/ark](https://console.volcengine.com/ark)，开通**模型接入**服务。
2. 在"API Key 管理"页面创建 API Key。
3. 在"模型推理 > 我的推理接入点"中创建一个 DeepSeek 推理接入点，记录 **Endpoint ID**（格式：`ep-xxxxxxxx-xxxxx`）。
4. 设置环境变量：

```bash
export ARK_API_KEY="your-ark-api-key"           # 火山引擎 API Key
export ARK_MODEL_ID="ep-xxxxxxxx-xxxxx"          # 推理接入点 ID（脱敏）
```

> ⚠️ **安全提示**：请勿将 API Key 明文提交到 Git 仓库，推荐使用 `.env` 文件配合 `python-dotenv`，并将 `.env` 加入 `.gitignore`。

---

## 运行命令

### 交互式多轮对话（默认：DeepSeek 官方 API + 流式输出）

```bash
python chatbot_deepseek.py
```

### 使用火山引擎 ARK

```bash
python chatbot_deepseek.py --provider ark
```

### 关闭流式输出（一次性返回完整回复）

```bash
python chatbot_deepseek.py --no-stream
```

### 单次问答示例（非交互，适合快速验证）

```bash
python chatbot_deepseek.py --example
```

---

## 示例输入 / 输出

```
============================================================
  🚀  DeepSeek Chatbot  |  Provider: DeepSeek 官方 API
  Model: deepseek-chat
  输入 'quit' 或 'exit' 退出，输入 'clear' 清空对话历史
============================================================

👤 You: 你好，请介绍一下自己

🤖 Assistant: 你好！我是 DeepSeek，一款由深度求索（DeepSeek）公司开发的人工智能助手。
我可以帮助你回答问题、撰写文章、进行代码开发、数据分析等各类任务。
有什么我可以帮助你的吗？

👤 You: 用 Python 写一个冒泡排序

🤖 Assistant: 以下是一个简单的 Python 冒泡排序实现：

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# 示例
nums = [64, 34, 25, 12, 22, 11, 90]
print(bubble_sort(nums))  # [11, 12, 22, 25, 34, 64, 90]

👤 You: exit
👋 再见！
```

---

## 核心实现说明

| 功能 | 实现位置 |
|------|----------|
| 发送文本问题 → 调用模型 → 获取回复 | `DeepSeekChatbot.chat()` |
| 多轮对话历史管理 | `self.history` 列表，每轮追加 `user`/`assistant` 消息 |
| 流式输出（逐字打印） | `DeepSeekChatbot._chat_stream()` |
| 切换 Provider（DeepSeek / ARK） | `--provider` 参数 + `_build_client()` |

---

## 注意事项

1. **网络**：DeepSeek 官方 API 国内直连；火山引擎 ARK 同样国内可用。
2. **费用**：两个平台均按 Token 计费，初次使用请关注免费额度。
3. **模型选择**：
   - DeepSeek 官方支持 `deepseek-chat`（V3）和 `deepseek-reasoner`（R1）。
   - ARK 上需提前创建推理接入点并绑定对应模型版本。
4. **`.env` 用法**（可选）：安装 `pip install python-dotenv`，在项目根目录创建 `.env`：
   ```
   DEEPSEEK_API_KEY=sk-xxxx
   ARK_API_KEY=your-key
   ARK_MODEL_ID=ep-xxxx
   ```
   在脚本顶部加入：
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```
