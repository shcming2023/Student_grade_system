# GitHub配置和仓库创建指南

## 🎯 目标
将本地学生成绩管理系统同步到GitHub

## 📋 前置检查
- ✅ Git已安装: `/usr/bin/git`
- ✅ GitHub用户: shcming2023
- ✅ 本地项目已创建

## 🔧 步骤1: 配置Git用户信息
```bash
# 设置Git用户名和邮箱
git config --global user.name "shcming2023"
git config --global user.email "your-email@example.com"

# 验证配置
git config --list
```

## 🔧 步骤2: 在GitHub创建仓库
1. 访问 https://github.com/shcming2023
2. 点击 "New repository" 或 "+" 按钮
3. 填写仓库信息:
   - Repository name: `Student_grade_system`
   - Description: `学生成绩管理系统`
   - 选择 Public 或 Private
   - 勾选 "Add a README file" (可选)
   - 勾选 "Add .gitignore" (可选)
4. 点击 "Create repository"

## 🔧 步骤3: 初始化本地Git仓库
```bash
cd "/opt/Way To Future考试管理系统/Student_grade_system"

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "Initial commit: 学生成绩管理系统初始化"
```

## 🔧 步骤4: 连接远程仓库
```bash
# 添加远程仓库 (替换为实际的仓库URL)
git remote add origin https://github.com/shcming2023/Student_grade_system.git

# 推送到远程仓库
git push -u origin main
```

## 🔧 步骤5: 配置SSH密钥 (推荐)
```bash
# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# 启动SSH代理
eval "$(ssh-agent -s)"

# 添加密钥到代理
ssh-add ~/.ssh/id_rsa

# 复制公钥到GitHub
cat ~/.ssh/id_rsa.pub
# 然后在GitHub Settings > SSH and GPG keys 中添加

# 使用SSH URL
git remote set-url origin git@github.com:shcming2023/Student_grade_system.git
```

## 🔧 步骤6: 验证连接
```bash
# 测试SSH连接
ssh -T git@github.com

# 查看远程仓库
git remote -v

# 查看状态
git status
```

## 🔄 日常使用命令
```bash
# 拉取最新代码
git pull origin main

# 添加新更改
git add .
git commit -m "更新内容"
git push origin main

# 查看提交历史
git log --oneline
```

## 📁 项目结构
```
Student_grade_system/
├── README.md                 # 项目说明
├── requirements.txt          # Python依赖
├── app.py                   # Flask主应用
├── config.py               # 配置文件
├── templates/              # HTML模板
├── static/                # 静态资源
├── utils/                 # 工具函数
├── models/                # 数据模型
└── database/              # 数据库文件
```

## 🚀 快速部署
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

访问: http://localhost:5000

## 📞 常见问题解决

### 问题1: 权限被拒绝
```bash
# 解决方案: 使用SSH或配置token
git remote set-url origin https://your-token@github.com/shcming2023/Student_grade_system.git
```

### 问题2: 推送失败
```bash
# 解决方案: 强制推送 (谨慎使用)
git push -f origin main
```

### 问题3: 忽略文件配置
创建 `.gitignore` 文件:
```
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv
venv/
instance/
*.db
*.sqlite
.DS_Store
```

## 📝 提交规范
```bash
git commit -m "feat: 添加学生管理功能"
git commit -m "fix: 修复成绩计算bug"
git commit -m "docs: 更新README文档"
```