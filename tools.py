import json
import re
import requests
from datetime import datetime
from config import SENIVERSE_API_KEY

# ========================= 工具函数定义 =========================
def get_weather(city: str) -> str:
    """通过心知天气API查询实时天气（需配置 SENIVERSE_API_KEY）"""
    if SENIVERSE_API_KEY == "你的心知天气API_KEY":
        return "天气服务未配置API Key，请在config.py中填入心知天气的key"

    url = "https://api.seniverse.com/v3/weather/now.json"
    params = {
        "key": SENIVERSE_API_KEY,
        "location": city,
        "language": "zh-Hans",
        "unit": "c"
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            now = result["now"]
            city_name = result["location"]["name"]
            temp = now.get("temperature", "未知")
            text = now.get("text", "未知")
            feels_like = now.get("feels_like")  # 如果不存在就返回 None

            if feels_like:
                return f"{city_name}天气：{text}，温度 {temp}℃，体感 {feels_like}℃"
            else:
                return f"{city_name}天气：{text}，温度 {temp}℃"
        else:
            return f"未找到城市 {city} 的天气信息"
    except Exception as e:
        return f"天气查询失败：{str(e)}"

def calculate(expression: str) -> str:
    """安全计算数学表达式（仅允许数字、运算符和括号）"""
    # 安全检查，只允许数字、空格、+-*/()、.、%
    allowed_chars = set("0123456789+-*/().%^ ")
    if not all(ch in allowed_chars for ch in expression):
        return "表达式含有不允许的字符，只能包含数字、运算符和括号"
    # 替换 ^ 为 ** 以支持幂运算
    expression = expression.replace("^", "**")
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算出错：{str(e)}"

def get_current_time() -> str:
    """获取当前日期和时间"""
    now = datetime.now()
    return f"现在是 {now.year}年{now.month}月{now.day}日 {now.hour}:{now.minute:02d}，星期{['一','二','三','四','五','六','日'][now.weekday()]}"

# ========================= 工具注册表 =========================
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time,
    # 以后在这里添加新函数即可
}

# ========================= 工具描述（给模型看的） =========================
TOOLS_DESCRIPTION = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气（使用心知天气数据）",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海、New York"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算一个数学表达式，例如：1+2*3、sqrt(4)可以写成4**0.5",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式字符串，如 '(2+3)*4'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的准确日期和时间",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    # 以后添加新工具在这里追加描述即可
]