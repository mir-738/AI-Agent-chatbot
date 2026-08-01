import json
from datetime import datetime
from openai import OpenAI
from config import *
from tools import AVAILABLE_TOOLS, TOOLS_DESCRIPTION
from memory import Memory

class Robot:
    def __init__(self, name=BOT_NAME, tone=BOT_TONE, tools=None, memory_path=MEMORY_FILE):
        self.name = name
        self.tone = tone
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        self.tools = tools if tools is not None else AVAILABLE_TOOLS
        self.tools_desc = TOOLS_DESCRIPTION if self.tools else []

        # 初始化记忆模块：短期记忆最多保留 100 条（无天数限制）
        self.memory = Memory(filepath=memory_path, max_short_term=100)

        # 构建系统提示（包含记忆）
        self._base_system_prompt = SYSTEM_PROMPT_TEMPLATE.format(name=self.name, tone=self.tone)
        self.history = [{"role": "system", "content": self._build_system_prompt()}]

    def _build_system_prompt(self):
        """将记忆文本合并到系统提示中"""
        # 长期记忆全部注入，短期记忆仅取最近 5 条（避免上下文过长）
        memory_text = self.memory.format_for_prompt(short_max=10)
        return self._base_system_prompt + "\n\n" + memory_text

    def _trim_history(self):
        """只保留最近 MAX_HISTORY 条对话（不含系统提示）"""
        system_msg = self.history[0]
        rest = self.history[1:]
        if len(rest) > MAX_HISTORY:
            rest = rest[-MAX_HISTORY:]
        self.history = [system_msg] + rest

    def _remember(self, user_input, bot_reply):
        # 排除列表（这些不视为个人信息）
        exclude_phrases = ["我喜欢你", "我喜欢他", "我喜欢她", "我喜欢它"]

        if any(phrase in user_input for phrase in exclude_phrases):
            # 当作普通对话处理
            summary = f"用户：{user_input} | 机器人：{bot_reply[:50]}"
            self.memory.add_short_term(summary)
            return

        if any(kw in user_input for kw in ["我叫", "我的名字是", "我住在", "我喜欢"]):
            self.memory.add_long_term(f"用户个人信息：{user_input}", keywords=["个人信息"])
        else:
            summary = f"用户：{user_input} | 机器人：{bot_reply[:50]}"
            self.memory.add_short_term(summary)

    def chat(self, user_input):
        """处理一次用户输入，返回机器人的最终回复文本"""
        # 1. 将用户消息加入历史
        self.history.append({"role": "user", "content": user_input})

        # 2. 第一次调用模型（可能返回工具调用要求）
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=self.history,
            tools=self.tools_desc if self.tools_desc else None,
            temperature=0.7
        )

        msg = response.choices[0].message

        # 3. 检查是否需要调用工具
        if msg.tool_calls:
            # 先保存助手消息（含工具调用请求）
            self.history.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in msg.tool_calls
                ]
            })

            tool_results = []
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"[工具调用] 正在调用 {func_name}，参数：{args}")

                if func_name in self.tools:
                    result = self.tools[func_name](**args)
                else:
                    result = f"工具 {func_name} 未找到"

                print(f"[工具结果] {result}")

                # 将工具结果加入历史
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
                tool_results.append((func_name, result))

            # 4. 再次调用模型，明确要求基于工具结果生成回复
            final_response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=self.history,
                temperature=0.7
            )
            final_msg = final_response.choices[0].message.content

            # 如果模型返回空，手动构建回复
            if not final_msg or final_msg.strip() == "":
                # 根据工具结果构建简洁回复
                if len(tool_results) == 1:
                    final_msg = tool_results[0][1]
                else:
                    final_msg = "\n".join([f"{name}: {res}" for name, res in tool_results])
        else:
            final_msg = msg.content

        # 5. 将最终助手回复加入历史
        self.history.append({"role": "assistant", "content": final_msg})

        # 6. 自动记忆本轮对话
        self._remember(user_input, final_msg)

        # 7. 裁剪历史长度
        self._trim_history()

        return final_msg

    def refresh_system_prompt(self):
        """手动刷新系统提示中的记忆部分（记忆更新后可调用）"""
        self.history[0] = {"role": "system", "content": self._build_system_prompt()}