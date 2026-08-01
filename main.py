"""
主程序入口
启动聊天机器人，基于 LangGraph 架构实现对话循环。
"""

from bot import Robot
from config import BOT_TONE, BOT_NAME
from langgraph.graph import StateGraph, END
from typing import TypedDict


class ChatState(TypedDict):
    user_input: str
    bot_reply: str
    should_exit: bool
    interrupted: bool   # 标记是否因键盘中断而退出


def main():
    # 初始化机器人
    bot = Robot(
        name=BOT_NAME,
        tone=BOT_TONE,
        memory_path="memory.json"
    )

    print(f"{bot.name} 已上线！输入 'exit' 或 '退出' 结束对话。\n")

    # ---------- 定义状态图节点 ----------
    def input_node(state: ChatState) -> dict:
        """获取用户输入，处理空输入、退出指令和键盘中断"""
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            # 标记为中断退出，不再重复打印退出语
            return {"user_input": "", "should_exit": True, "interrupted": True}

        if not user_input:
            # 空输入：不退出，回到输入节点重新获取
            return {"user_input": "", "should_exit": False, "interrupted": False}

        should_exit = user_input.lower() in ["exit", "退出"]
        return {
            "user_input": user_input,
            "should_exit": should_exit,
            "interrupted": False
        }

    def chat_node(state: ChatState) -> dict:
        """调用机器人获取回复（仅在非退出状态下执行）"""
        if state["should_exit"]:
            return {"bot_reply": ""}
        reply = bot.chat(state["user_input"])
        clean_reply = reply.strip().replace("\n\n", "\n")
        return {"bot_reply": clean_reply}

    def output_node(state: ChatState) -> dict:
        """打印机器人回复（非退出状态）"""
        if not state["should_exit"] and state["bot_reply"]:
            print(f"{bot.name}：{state['bot_reply']}\n")
        return {}

    def end_node(state: ChatState) -> dict:
        """结束对话，打印告别语（除非已经因中断打印过）"""
        if not state.get("interrupted", False):
            print(f"{bot.name}：さようなら、お兄ちゃん👋")
        return {}

    # ---------- 构建状态图 ----------
    builder = StateGraph(ChatState)

    # 添加节点
    builder.add_node("input", input_node)
    builder.add_node("chat", chat_node)
    builder.add_node("output", output_node)
    builder.add_node("end", end_node)

    builder.set_entry_point("input")

    # 从 input 出发的条件边
    def route_after_input(state: ChatState) -> str:
        if state["should_exit"]:
            return "end"
        if not state["user_input"]:
            return "input"   # 空输入循环
        return "chat"

    builder.add_conditional_edges(
        "input",
        route_after_input,
        {
            "end": "end",
            "input": "input",
            "chat": "chat"
        }
    )

    # 固定边：chat -> output -> input（循环），output 后回到 input 继续下一轮
    builder.add_edge("chat", "output")
    builder.add_edge("output", "input")

    # 编译并执行图（invoke 会一直运行，直到遇到 end 节点）
    app = builder.compile()
    app.invoke({})


if __name__ == "__main__":
    main()
