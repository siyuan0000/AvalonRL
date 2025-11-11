# Avalon AI Game - Web UI

Web 界面用于运行和查看 Avalon AI 游戏。

## 快速启动

```bash
./start_web.sh
```

然后访问 `http://localhost:5000`

## 功能

### 控制面板
- AI 后端选择（Ollama/DeepSeek API/Local Transformers）
- 实时游戏状态监控
- 最近游戏列表

### 日志查看器
- 完整游戏回放
- 玩家角色和 AI 配置
- 任务详情（提议、讨论、投票、执行）
- 暗杀阶段
- JSON 日志下载

## 使用

1. 启动服务：`./start_web.sh`
2. 浏览器访问：`http://localhost:5000`
3. 选择 AI 后端和模型
4. 点击 "Start Game"
5. 游戏完成后查看日志

## AI 后端配置

**Ollama（本地）**
- 选择模型（deepseek-r1/qwen2.5/llama3.1 等）
- 确保 Ollama 服务运行中

**DeepSeek API**
- 选择模型（deepseek-chat/deepseek-reasoner）
- API Key 可选（为空则使用 `.env.local`）

**Local Transformers**
- 输入 HuggingFace 模型 ID 或本地路径

## API 端点

**游戏控制**
- `POST /api/start_game` - 启动游戏
- `GET /api/game_status` - 获取状态

**日志管理**
- `GET /api/logs` - 游戏列表
- `GET /api/log/<game_id>` - 获取日志
- `GET /api/log/<game_id>/download` - 下载日志

**系统**
- `GET /api/check_ollama` - 检查 Ollama

## 文件结构

```
AvalonRL/
├── web_ui.py              # Flask 应用
├── start_web.sh           # 启动脚本
├── templates/
│   ├── index.html         # 控制面板
│   └── viewer.html        # 日志查看器
├── static/
│   ├── style.css
│   ├── script.js
│   └── viewer.js
└── logs/                  # 游戏日志
```

## 注意

- 游戏运行时间：几分钟到十几分钟（取决于 AI 模型）
- 一次只能运行一个游戏
- API Key 建议存储在 `.env.local`
- 自定义玩家配置请使用 `start.py`
