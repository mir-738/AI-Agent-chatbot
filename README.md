# AI-Agent-chatbot
下面是为你项目量身定制的 README.md 文件。请将其复制到项目根目录（覆盖现有 README.md），或直接新建。


# AI 聊天助手

> 一个基于 DeepSeek 大语言模型的智能聊天机器人，拥有长期记忆和实用工具，以 **“谷风天音”** 式傲娇妹妹人设与你互动。

---


特色


- **角色扮演**：内置“天音”人格提示词——表面毒舌嘲讽，内心温柔傲娇。根据你的情绪切换语气。  
- **长期记忆**：自动记录对话，并能识别你的喜好（如食物、音乐、习惯等），存储为长期记忆，让每次聊天都更懂你。  
- **实用工具箱**：  
  - **天气查询**：接入心知天气 API，实时获取城市天气。  
  - **计算器**：进行数学运算（支持复杂表达式）。  
  - **时间查询**：获取当前时间、日期或时区信息。  

---


技术栈


- **语言**：Python 3.10+  
- **LLM**：DeepSeek API（`deepseek-v4-flash` 模型）  
- **记忆存储**：JSON 文件（轻量，无需数据库）  
- **工具实现**：纯 Python 函数调用  
- **界面**：Web UI（基于 Streamlit 或 Flask，根据你的实现调整）  


---


安装与配置


1. 克隆仓库  
bash  
git clone https://github.com/mir-738/AI-Agent-chatbot.git  
cd AI-Agent-chatbot  
2. 创建虚拟环境（推荐）  
bash  
python -m venv .venv  
source .venv/bin/activate   # Linux/Mac  
.venv\Scripts\activate      # Windows  
3. 安装依赖  
bash  
pip install -r requirements.txt  
4. 配置环境变量  
在项目根目录创建 .env 文件（已加入 .gitignore），填入以下内容：  
```
env
DEEPSEEK_API_KEY=你的DeepSeek API密钥
SENIVERSE_API_KEY=你的心知天气API密钥
```
获取密钥：


DeepSeek: platform.deepseek.com  
心知天气: seniverse.com  


启动  
运行 Web UI  
bash  
python web_ui.py  
（如果使用 Streamlit，则执行 streamlit run web_ui.py）


命令行交互（若有）  
bash  
python main.py  
记忆机制  
短期记忆：保存最近 N 轮对话（由 MAX_HISTORY 控制），保持上下文连贯。  

长期记忆：当检测到用户反复提及的偏好（如“我喜欢吃辣”、“我讨厌下雨”）时，自动提取并存入 memory.json，日后对话会主动调用。  

记忆文件默认保留 7 天（由 MEMORY_DAY 控制），过时记忆自动清理。  

工具函数说明  
工具名称	触发方式	依赖  
天气查询	用户提问“今天天气怎么样？”或“北京天气”	心知天气 API（需 Seniverse 密钥）  
计算器	输入数学表达式如 (3+5)*2	无（使用 Python eval 安全沙箱）  
时间查询	“现在几点了？”、“今天星期几？”	无  
工具调用由 DeepSeek 根据上下文自动决策，无需手动指定。  



项目结构
```
text
.
├── .env                   # 环境变量（不提交）
├── .gitignore
├── README.md
├── requirements.txt
├── config.py              # 配置（API 密钥、模型参数等）
├── bot.py                 # 核心对话逻辑
├── memory.py              # 记忆管理（读写、过期清理）
├── tools.py               # 工具函数（天气、计算、时间）
├── web_ui.py              # Web 界面入口
├── main.py                # 命令行启动（可选）
├── tianyin.spec           # PyInstaller 打包配置
└── memory.json            # 记忆存储文件（首次运行自动生成）

```
```
测试工具
你可以单独测试工具函数：
```
```
python
from tools import get_weather, calculate, get_current_time
print(get_weather("北京"))
print(calculate("10+20*3"))
print(get_current_time())
```



贡献  
欢迎提交 Issue 或 Pull Request。若你想添加新工具或优化记忆策略，请参考现有代码风格。  

许可  
本项目仅供学习与娱乐用途，请勿用于商业或非法场景。使用 DeepSeek 与心知天气 API 时请遵守其服务条款。  

致谢  
DeepSeek 提供强大且性价比极高的语言模型  
  
心知天气提供稳定易用的天气 API  

角色设定灵感来自“谷风天音”（柚子社傲娇妹妹形象）
