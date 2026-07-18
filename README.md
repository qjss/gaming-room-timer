# 🎮 电玩店包间计时管理系统

一个简单易用的主机电玩店包间计时管理系统，支持多包间管理、实时计时、结账等功能。

## ✨ 功能特点

- 📺 **多包间管理**：支持 PS5、Xbox、Switch 等多种游戏机
- ⏱️ **实时计时**：精确到分钟的计时功能
- 💰 **自动计费**：按小时计费，自动计算费用
- 📊 **数据统计**：今日收入、订单数等统计
- 📋 **历史记录**：完整的消费记录查询
- 🌐 **云端部署**：一键 Blueprint 部署到 Render 免费空间

## 🚀 一键部署到 Render（Blueprint）

### 1. Fork 本仓库
点击右上角的 **Fork**，把仓库复制到你自己的 GitHub 账号下。

### 2. 在 Render 创建 Blueprint
1. 打开 [Render Dashboard](https://dashboard.render.com/)
2. 点击 **New** → **Blueprint**
3. 选择 **Connect a repository**，授权并选中你的 `gaming-room-timer` 仓库
4. 蓝图名字输入 `xydw`（随便填），点击 **Apply**
5. Render 会自动识别 `render.yaml`，同时创建：
   - 🖥️ Web Service：`gaming-room-timer`（Python + Flask）
   - 🗄️ PostgreSQL：`gaming-room-db`（免费版）
6. **DATABASE_URL 会自动注入**（render.yaml 已配置 `fromDatabase`），无需手动设置

> 等待约 2-5 分钟，看到 Web Service 显示 `Live` 就表示部署完成了 ✅

### 3. 初始化包间
第一次打开网站时，点击页面右上角的 **🔧 初始化包间** 按钮，
系统会自动创建 4 个默认包间（PS5×2、Xbox×1、Switch×1）。

### 4. 后续修改
- 直接在 GitHub 仓库里改代码，Render 会自动重新部署（已开启 autoDeploy）
- 如果想停服，到 Render Dashboard 对应服务上点 **Suspend**

## 💻 本地运行

### 前置要求
- Python 3.9+

### 安装与启动

```bash
# 克隆仓库
git clone https://github.com/qjss/gaming-room-timer.git
cd gaming-room-timer

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

打开浏览器访问 http://localhost:5000

本地默认使用 SQLite，无需任何配置。

## 📱 使用说明

### 开始计时
1. 点击空闲包间卡片上的 **▶ 开始计时** 按钮
2. 输入顾客名称（可选，默认"散客"）
3. 点击 **开始计时**，包间变成"使用中"

### 结账
1. 点击使用中包间的 **💰 结账** 按钮
2. 系统会自动计算时长与费用
3. 确认后点击 **确认结账**

### 新增 / 修改包间
- 通过页面上的 **➕ 新增包间** 可以添加新房间
- 输入主机类型（PS5 / Xbox / Switch）和时薪即可

## 🔌 API 接口速查

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET  | `/api/rooms` | 获取所有包间 |
| POST | `/api/rooms` | 创建新包间 |
| POST | `/api/rooms/init` | 创建默认包间 |
| POST | `/api/rooms/<id>/start` | 开始计时 |
| POST | `/api/sessions/<id>/end` | 结束计时 |
| GET  | `/api/sessions?active=true` | 当前进行中的会话 |
| GET  | `/api/statistics` | 今日收入/订单 |
| GET  | `/rooms/status/all` | 所有包间状态概览 |

## 📂 项目结构

```
game-room-timer/
├── app/
│   ├── __init__.py       # 应用工厂（自动处理 postgres:// → postgresql://）
│   ├── models.py         # 数据库模型（Room / Session / Setting）
│   └── routes/
│       ├── home.py       # 首页
│       ├── rooms.py      # 包间管理 API
│       └── timer.py      # 计时 API
├── app/
│   └── templates/
│       └── index.html    # 前端页面（响应式 UI）
├── config.py             # 配置文件
├── app.py                # 应用入口（gunicorn 启动点）
├── requirements.txt      # 依赖（flask / sqlalchemy / psycopg2-binary）
├── render.yaml           # Render Blueprint（Web + PostgreSQL）
└── README.md             # 说明文档
```

## 🛠️ 技术栈

- **后端**：Flask 3 · SQLAlchemy · Flask-Migrate
- **数据库**：PostgreSQL（生产）/ SQLite（本地开发）
- **前端**：原生 HTML5 + CSS3 + JavaScript（无框架依赖）
- **部署**：Render（Web Service + Managed PostgreSQL · 免费）

## ⚠️ 注意事项

1. **Render 免费版限制**
   - Web 服务 15 分钟无活动后休眠，下次访问需要 30 秒左右唤醒
   - 免费 PostgreSQL 90 天后会休眠（但不会被删除，数据保留）
   - 适合小型店铺 demo / 自用

2. **时区说明**
   - 数据库使用 UTC 时间存储
   - 前端按本地时间显示（中国显示 UTC+8）

3. **数据安全**
   - `SECRET_KEY` 已用 `generateValue: true` 自动随机生成
   - 建议每隔一段时间到 Render 控制台备份 PostgreSQL 数据

## 📝 License

MIT License
