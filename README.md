# 🎮 电玩店包间计时管理系统

一个简单易用的主机电玩店包间计时管理系统，支持多包间管理、实时计时、结账等功能。

## ✨ 功能特点

- 📺 **多包间管理**: 支持 PS5、Xbox、Switch 等多种游戏机
- ⏱️ **实时计时**: 精确到分钟的计时功能
- 💰 **自动计费**: 按小时计费，自动计算费用
- 📊 **数据统计**: 今日收入、订单数等统计
- 📋 **历史记录**: 完整的消费记录查询
- 🌐 **云端部署**: 支持 Render 免费部署

## 🚀 快速部署到 Render

### 方法一：使用 Blueprint（推荐）

1. **Fork 本仓库**
   - 点击本仓库右上角的 ""Fork""
   - 选择你的 GitHub 账号

2. **登录 Render**
   - 访问 [Render](https://render.com)
   - 使用 GitHub 账号登录

3. **创建 Blueprint**
   - 点击 ""New"" → ""Blueprint""
   - 连接你的 GitHub 仓库
   - Render 会自动读取 ender.yaml 并创建服务

4. **配置数据库**
   - 在 Render 后台，进入 PostgreSQL 数据库
   - 复制 Internal Database URL
   - 在 Web 服务的环境变量中设置 DATABASE_URL

### 方法二：手动部署

1. **创建 Web 服务**
   - ""New"" → ""Web Service""
   - 连接 GitHub 仓库
   - 设置构建命令: pip install -r requirements.txt
   - 设置启动命令: gunicorn app:app

2. **创建 PostgreSQL 数据库**
   - ""New"" → ""PostgreSQL""
   - 记住数据库连接信息

3. **设置环境变量**
   - DATABASE_URL: 数据库连接地址
   - SECRET_KEY: 随机密钥（可自动生成）

## 💻 本地运行

### 前置要求
- Python 3.9+
- SQLite（可选，用于本地开发）

### 安装步骤

`ash
# 克隆仓库
git clone <你的仓库地址>
cd game-room-timer

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
`

打开浏览器访问 http://localhost:5000

## 📱 使用说明

### 初始化包间
1. 首次使用时，点击右上角的 ""初始化包间"" 按钮
2. 系统会自动创建 4 个默认包间

### 开始计时
1. 点击空闲包间的 ""开始计时"" 按钮
2. 输入顾客名称（可选，默认为 ""散客""）
3. 点击 ""开始计时""

### 结账
1. 点击使用中包间的 ""结账"" 按钮
2. 确认时长和费用
3. 点击 ""确认结账""

## 📂 项目结构

`
game-room-timer/
├── app/
│   ├── __init__.py       # 应用工厂
│   ├── models.py         # 数据库模型
│   ├── routes/           # 路由
│   │   ├── home.py       # 首页
│   │   ├── rooms.py      # 包间管理 API
│   │   └── timer.py      # 计时 API
│   └── templates/
│       └── index.html    # 前端页面
├── config.py             # 配置文件
├── app.py                # 应用入口
├── requirements.txt      # 依赖列表
├── render.yaml           # Render Blueprint
└── README.md             # 说明文档
`

## 🛠️ 技术栈

- **后端**: Flask, SQLAlchemy, Flask-Migrate
- **数据库**: PostgreSQL (Render) / SQLite (本地)
- **前端**: HTML5, CSS3, JavaScript
- **部署**: Render (Web + PostgreSQL)

## ⚠️ 注意事项

1. **Render 免费版限制**
   - Web 服务在 15 分钟无活动后会休眠
   - 数据库免费版有存储限制
   - 适合小规模使用

2. **时区说明**
   - 系统使用 UTC 时间存储
   - 前端会自动转换为本地时间显示

3. **数据安全**
   - 建议定期备份数据库
   - 不要在生产环境使用默认密钥

## 📝 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请通过 GitHub Issues 反馈。
