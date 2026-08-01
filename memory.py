import json
import os
from datetime import datetime

class Memory:
    def __init__(self, filepath="memory.json", max_short_term=20):
        """
        filepath:         记忆存储文件
        max_short_term:   短期记忆最大条数（FIFO，最新100条）
        """
        self.filepath = filepath
        self.max_short_term = max_short_term
        self.memories = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def add_short_term(self, content, keywords=None):
        """添加短期记忆，自动保留最新 max_short_term 条"""
        memory = {
            "type": "short",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "keywords": keywords or []
        }
        self.memories.append(memory)
        self._trim_short_term()
        self._save()

    def add_long_term(self, content, keywords=None):
        """添加长期记忆（永久保存）"""
        memory = {
            "type": "long",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "keywords": keywords or []
        }
        self.memories.append(memory)
        self._save()

    def _trim_short_term(self):
        """短期记忆只保留最新 max_short_term 条（按时间戳排序）"""
        long_mems = [m for m in self.memories if m.get("type") == "long"]
        short_mems = [m for m in self.memories if m.get("type") == "short"]
        # 按时间戳倒序排列，保留前 max_short_term 条，再转回正序存储
        short_mems.sort(key=lambda x: x["timestamp"], reverse=True)
        short_mems = short_mems[:self.max_short_term]
        self.memories = long_mems + short_mems

    def get_short_term(self, max_count=None):
        """获取短期记忆，最新在前"""
        short = [m for m in self.memories if m.get("type") == "short"]
        short.sort(key=lambda x: x["timestamp"], reverse=True)
        if max_count:
            short = short[:max_count]
        return short

    def get_long_term(self):
        """获取所有长期记忆，最新在前"""
        long = [m for m in self.memories if m.get("type") == "long"]
        long.sort(key=lambda x: x["timestamp"], reverse=True)
        return long

    def format_for_prompt(self, short_max=5):
        """将记忆格式化为提示文本（长期全部显示，短期只取最近 short_max 条）"""
        long_mems = self.get_long_term()
        short_mems = self.get_short_term(max_count=short_max)

        lines = []
        if long_mems:
            lines.append("【长期记忆（永久保留）】")
            for i, mem in enumerate(long_mems, 1):
                time_str = datetime.fromisoformat(mem["timestamp"]).strftime("%m-%d %H:%M")
                lines.append(f"{i}. [{time_str}] {mem['content']}")

        if short_mems:
            lines.append("【近期对话记忆（最近 {short_max} 条）】")
            for i, mem in enumerate(short_mems, 1):
                time_str = datetime.fromisoformat(mem["timestamp"]).strftime("%m-%d %H:%M")
                lines.append(f"{i}. [{time_str}] {mem['content']}")

        return "\n".join(lines) if lines else "暂无记忆。"



