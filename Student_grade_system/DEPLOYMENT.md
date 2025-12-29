# 学生成绩管理系统 - Mac mini M4 内网部署指南

本文档详细说明如何在Mac mini M4服务器上部署学生成绩管理系统，供学校内网使用。

---

## 📋 目录

1. [系统要求](#系统要求)
2. [准备工作](#准备工作)
3. [部署步骤](#部署步骤)
4. [配置说明](#配置说明)
5. [启动和停止](#启动和停止)
6. [访问系统](#访问系统)
7. [数据导入](#数据导入)
8. [常见问题](#常见问题)
9. [维护和备份](#维护和备份)

---

## 系统要求

### 硬件要求
- **Mac mini M4**（或其他Mac设备）
- **内存**：建议8GB以上
- **存储**：至少10GB可用空间

### 软件要求
- **macOS**：Ventura 13.0或更高版本
- **Python**：3.9或更高版本
- **pip**：Python包管理工具

---

## 准备工作

### 1. 安装Python 3.9+
推荐使用 Homebrew 或 官网安装包。

### 2. 数据库
本系统默认使用 SQLite，无需额外安装数据库服务。如需使用 MySQL，请在环境变量中配置 `DATABASE_URL`。

---

## 部署步骤

### 1. 上传项目文件
将整个项目文件夹上传到Mac mini服务器。

### 2. 执行启动脚本
```bash
cd Student_grade_system
chmod +x start_student_system.sh
./start_student_system.sh
```
该脚本会自动检查依赖、安装依赖并在后台启动服务（默认端口 8083）。

### 3. 验证部署
访问 http://localhost:8083 或 http://<服务器IP>:8083

---

## 常用命令

### 停止服务
```bash
pkill -f "python3.*wtf_app_simple.py"
```

### 查看日志
```bash
tail -f student_system.log
```
cd /Users/your_username/student_grade_system
cp .env.production.template .env.production
nano .env.production  # 或使用其他编辑器
```

**必须修改的配置项：**
```env
# 数据库连接（根据实际情况修改）
DATABASE_URL=mysql://gradeuser:your_password@localhost:3306/student_grade_system

# JWT密钥（生成随机密钥）
JWT_SECRET=your_random_secret_key_here
```

**生成随机JWT密钥：**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 3. 运行部署脚本

```bash
./deploy.sh
```

部署脚本会自动执行以下操作：
1. 检查Node.js和pnpm版本
2. 安装项目依赖
3. 运行数据库迁移
4. 构建生产版本

---

## 配置说明

### 环境变量详解

| 变量名 | 说明 | 示例 | 必填 |
|--------|------|------|------|
| `DATABASE_URL` | MySQL数据库连接字符串 | `mysql://user:pass@localhost:3306/dbname` | ✓ |
| `JWT_SECRET` | JWT令牌加密密钥 | 随机生成的长字符串 | ✓ |
| `PORT` | 应用运行端口 | `3000` | ✗ |
| `VITE_APP_TITLE` | 系统标题 | `学生成绩管理系统` | ✗ |
| `OWNER_OPEN_ID` | 管理员账户ID | `admin` | ✗ |
| `OWNER_NAME` | 管理员姓名 | `管理员` | ✗ |

---

## 启动和停止

### 启动应用

```bash
./start.sh
```

启动成功后会显示访问地址：
```
✓ 应用启动成功！

访问地址：
  本机：http://localhost:3000
  局域网：http://192.168.1.100:3000

进程ID：12345
日志文件：logs/app.log
```

### 停止应用

```bash
./stop.sh
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/app.log

# 查看最近100行日志
tail -n 100 logs/app.log
```

### 开机自动启动（可选）

创建启动服务（使用launchd）：

1. 创建plist文件：
```bash
nano ~/Library/LaunchAgents/com.school.gradeystem.plist
```

2. 添加以下内容（修改路径）：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.school.gradesystem</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/your_username/student_grade_system/start.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/Users/your_username/student_grade_system</string>
</dict>
</plist>
```

3. 加载服务：
```bash
launchctl load ~/Library/LaunchAgents/com.school.gradesystem.plist
```

---

## 访问系统

### 本机访问
在Mac mini上打开浏览器，访问：
```
http://localhost:3000
```

### 局域网访问

#### 1. 获取Mac mini的IP地址
```bash
ipconfig getifaddr en0  # 有线网络
# 或
ipconfig getifaddr en1  # 无线网络
```

例如输出：`192.168.1.100`

#### 2. 在其他设备上访问
在同一局域网内的任何设备（电脑、平板、手机）上打开浏览器，访问：
```
http://192.168.1.100:3000
```

#### 3. 配置防火墙（如果无法访问）
```bash
# 允许端口3000的入站连接
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/node
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/local/bin/node
```

---

## 数据导入

### 导入24套试卷数据

部署完成后，运行以下命令导入预置的24套试卷模板和题目：

```bash
node import-exam-templates.mjs
```

这将导入：
- 6个科目（朗文英语、牛津英语、先锋英语、中数、英数、语文）
- 24个试卷模板
- 1200+道题目（包含模块、知识点、题型、分值）

### 导入学生数据（可选）

如果有现有的学生数据，可以通过系统界面手动添加，或联系技术支持进行批量导入。

---

## 常见问题

### 1. 端口被占用

**问题**：启动时提示"端口3000已被占用"

**解决方法**：
```bash
# 查找占用端口的进程
lsof -i :3000

# 停止该进程
kill -9 <PID>

# 或修改.env.production中的PORT配置
```

### 2. 数据库连接失败

**问题**：启动时提示数据库连接错误

**解决方法**：
1. 检查MySQL服务是否运行：
   ```bash
   brew services list
   ```
2. 验证数据库连接信息：
   ```bash
   mysql -u gradeuser -p student_grade_system
   ```
3. 检查`.env.production`中的`DATABASE_URL`配置

### 3. 权限问题

**问题**：脚本无法执行

**解决方法**：
```bash
chmod +x deploy.sh start.sh stop.sh
```

### 4. Node.js版本过低

**问题**：部署时提示Node.js版本不兼容

**解决方法**：
```bash
# 使用nvm安装新版本Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

---

## 维护和备份

### 数据库备份

#### 手动备份
```bash
# 备份数据库
mysqldump -u gradeuser -p student_grade_system > backup_$(date +%Y%m%d).sql

# 恢复数据库
mysql -u gradeuser -p student_grade_system < backup_20250101.sql
```

#### 自动备份（推荐）

创建备份脚本：
```bash
nano backup.sh
```

添加内容：
```bash
#!/bin/bash
BACKUP_DIR="/Users/your_username/backups"
mkdir -p $BACKUP_DIR
mysqldump -u gradeuser -p'your_password' student_grade_system > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql

# 保留最近7天的备份
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

设置定时任务（每天凌晨2点备份）：
```bash
crontab -e
```

添加：
```
0 2 * * * /Users/your_username/student_grade_system/backup.sh
```

### 日志管理

定期清理日志文件：
```bash
# 清空日志
> logs/app.log

# 或归档日志
mv logs/app.log logs/app_$(date +%Y%m%d).log
```

### 系统更新

当有新版本时：
1. 停止应用：`./stop.sh`
2. 备份数据库
3. 替换项目文件
4. 运行部署脚本：`./deploy.sh`
5. 启动应用：`./start.sh`

---

## 技术支持

如遇到问题，请联系系统管理员或技术支持团队。

**系统信息：**
- 项目名称：学生成绩管理系统
- 版本：1.0.0
- 技术栈：React + Node.js + MySQL
- 部署环境：Mac mini M4 内网

---

## 附录

### 目录结构
```
student_grade_system/
├── client/                 # 前端代码
├── server/                 # 后端代码
├── drizzle/               # 数据库schema
├── dist/                  # 构建输出（部署后生成）
├── logs/                  # 日志文件
├── .env.production        # 生产环境配置（需手动创建）
├── .env.production.template  # 配置模板
├── deploy.sh              # 部署脚本
├── start.sh               # 启动脚本
├── stop.sh                # 停止脚本
├── import-exam-templates.mjs  # 数据导入脚本
├── package.json           # 项目依赖
└── DEPLOYMENT.md          # 本文档
```

### 系统架构
```
[客户端浏览器] <--HTTP--> [Node.js服务器] <---> [MySQL数据库]
     ↓                         ↓
  React前端              Express + tRPC后端
```

### 端口说明
- **3000**：Web应用服务端口（可在.env.production中修改）
- **3306**：MySQL数据库端口（默认）

---

**祝您使用愉快！**
