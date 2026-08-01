import customtkinter as ctk
from threading import Thread
from bot import Robot  # 请确保 bot.py 中定义了 Robot 类
import tkinter as tk

# 设置外观
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.bot = Robot()

        self.title("天音 Chat")
        self.geometry("500x650")
        self.minsize(400, 500)

        # 布局权重
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # ---------- 聊天显示区域（可滚动） ----------
        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            scrollbar_button_color=("gray70", "gray30"),  # 让滚动条更明显
            scrollbar_button_hover_color=("gray50", "gray50")
        )
        self.chat_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")

        # 内部容器列权重，使消息容器可以靠左或靠右
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # 绑定鼠标滚轮事件（增强兼容性）
        self.chat_frame.bind("<MouseWheel>", self._on_mousewheel)

        # ---------- 输入区域 ----------
        self.input_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray85", "gray20"))
        self.input_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="输入消息...",
            corner_radius=20,
            height=40,
            border_width=0,
            fg_color=("gray95", "gray30")
        )
        self.entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.entry.bind("<Return>", self.send_message)

        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="发送",
            width=60,
            height=40,
            corner_radius=20,
            command=self.send_message
        )
        self.send_btn.grid(row=0, column=1, padx=(0, 10), pady=10)

        # 存储所有气泡控件（用于调整宽度）
        self.bubbles = []

        # 右键菜单（复制功能）
        self.copy_menu = tk.Menu(self, tearoff=0)
        self.copy_menu.add_command(label="复制", command=self.copy_bubble_text)
        self.current_bubble = None

        # 窗口尺寸变化时更新气泡宽度
        self.bind("<Configure>", self.on_window_resize)

        # 欢迎消息
        self.add_message("天音", "你好！我是天音，你的智能助手。", is_user=False)
        self.entry.focus()

        # 初始调整气泡宽度
        self.after(100, lambda: self.on_window_resize(type('Event', (), {'widget': self})()))

    def _on_mousewheel(self, event):
        """处理鼠标滚轮滚动"""
        self.chat_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_wraplength(self):
        """计算气泡的最大宽度（窗口宽度的60%，并限制最小/最大值）"""
        window_width = self.winfo_width()
        target = int(window_width * 0.6)
        return max(200, min(target, 500))

    def on_window_resize(self, event):
        """窗口大小变化时更新所有气泡的折行宽度，并重新调整滚动区域"""
        if event.widget == self:
            new_width = self.get_wraplength()
            for bubble in self.bubbles:
                bubble.configure(wraplength=new_width)
            # 刷新滚动区域
            self.chat_frame._parent_canvas.configure(scrollregion=self.chat_frame._parent_canvas.bbox("all"))
            self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """可靠地将滚动条移动到底部"""
        self.chat_frame.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)
        # 延迟再执行一次，确保新内容加载后仍处于底部
        self.after(50, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))

    def add_message(self, sender, text, is_user=True):
        """
        添加一条消息到聊天区域
        is_user: True 表示用户消息（右侧绿色气泡），False 表示机器人消息（左侧灰色气泡）
        """
        # 消息容器（透明，用于控制整体对齐）
        msg_container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        row_index = len(self.chat_frame.winfo_children())
        msg_container.grid(
            row=row_index, column=0,
            sticky="e" if is_user else "w",
            padx=10, pady=(4, 4)
        )
        # 容器内部列权重，使气泡可以靠左或靠右
        msg_container.grid_columnconfigure(0, weight=1)

        # 发送者名称（小字显示）
        sender_label = ctk.CTkLabel(
            msg_container,
            text=sender,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("gray50", "gray70")
        )
        sender_label.grid(
            row=0, column=0,
            sticky="e" if is_user else "w",
            padx=(0, 5) if is_user else (5, 0),
            pady=(0, 2)
        )

        # 气泡颜色
        if is_user:
            bubble_color = "#95EC69"  # 微信绿
            text_color = "#000000"
        else:
            bubble_color = ("#E0E0E0", "#4A4A4A")
            text_color = ("#000000", "#FFFFFF")

        bubble = ctk.CTkLabel(
            msg_container,
            text=text,
            corner_radius=12,
            fg_color=bubble_color,
            text_color=text_color,
            padx=14,
            pady=10,
            wraplength=self.get_wraplength(),
            justify="left",
            font=ctk.CTkFont(size=13)
        )
        bubble.grid(row=1, column=0, sticky="e" if is_user else "w")

        self.bubbles.append(bubble)

        # 绑定右键菜单
        bubble.bind("<Button-3>", self.show_copy_menu)
        bubble.bind("<Button-1>", lambda e: self.copy_menu.unpost())

        # 强制更新滚动区域（让滚动条识别新内容）
        self.chat_frame._parent_canvas.configure(scrollregion=self.chat_frame._parent_canvas.bbox("all"))
        # 滚动到底部
        self.scroll_to_bottom()

    def show_copy_menu(self, event):
        self.current_bubble = event.widget
        try:
            self.copy_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.copy_menu.grab_release()

    def copy_bubble_text(self):
        if self.current_bubble:
            text = self.current_bubble.cget("text")
            self.clipboard_clear()
            self.clipboard_append(text)
            self.current_bubble = None

    def send_message(self, event=None):
        user_input = self.entry.get().strip()
        if not user_input:
            return
        self.add_message("你", user_input, is_user=True)
        self.entry.delete(0, "end")
        self.send_btn.configure(state="disabled")
        Thread(target=self.get_bot_reply, args=(user_input,), daemon=True).start()

    def get_bot_reply(self, user_input):
        try:
            reply = self.bot.chat(user_input)
            self.after(0, self.show_reply, reply)
        except Exception as e:
            self.after(0, self.show_reply, f"❌ 出错：{str(e)}")

    def show_reply(self, reply):
        self.add_message("天音", reply, is_user=False)
        self.send_btn.configure(state="normal")


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()