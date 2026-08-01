"""
主程序入口
启动聊天机器人，循环接收用户输入并输出回复。
"""

from bot import Robot
from config import BOT_TONE, BOT_NAME


def main():
    # 初始化机器人，所有参数均可在此修改
    bot = Robot(
        name=BOT_NAME,          # 机器人名字
        tone=BOT_TONE,    # 语气风格
        memory_path="memory.json"
    )

    print(f"{bot.name} 已上线！输入 'exit' 或 '退出' 结束对话。\n")


    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "退出"]:
            print(f"{bot.name}：さようなら、お兄ちゃん👋")
            break

        reply = bot.chat(user_input)
        clean_reply = reply.strip().replace("\n\n", "\n")
        print(f"{bot.name}：{clean_reply}\n")

if __name__ == "__main__":
    main()
