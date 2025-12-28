# 私有仓库协同开发配置指南

## 🎯 目标
保持GitHub仓库私有，在当前CodeBuddy环境中协同开发

## 🔐 方案1: 使用Personal Access Token (推荐)

### 步骤1: 创建GitHub Personal Access Token

1. **登录GitHub**
   - 访问 https://github.com/shcming2023
   - 点击右上角头像 → Settings

2. **进入开发者设置**
   - 左侧菜单 → Developer settings
   - Personal access tokens → Tokens (classic)

3. **生成新Token**
   - 点击 "Generate new token (classic)"
   - 填写信息:
     ```
     Note: CodeBuddy Development Token
     Expiration: 90 days (或选择No expiration)
     ```

4. **选择权限**
   ```
   ✅ repo (完整仓库访问权限)
   ✅ write:org (写入组织权限，如果需要)
   ✅ workflow (GitHub Actions权限)
   ```

5. **生成并复制Token**
   - 点击 "Generate token"
   - ⚠️ **立即复制并保存**，离开页面后无法再次查看

### 步骤2: 配置本地Git使用Token

```bash
cd "/opt/Way To Future考试管理系统/Student_grade_system"

# 方法1: 使用Token作为密码 (推荐)
git remote set-url origin https://shcming2023:YOUR_TOKEN@github.com/shcming2023/Student_grade_system.git

# 方法2: 使用git credential helper
git config --global credential.helper store
git push origin master  # 会提示输入用户名和Token
```

## 🔐 方案2: 使用SSH密钥 (更安全)

### 步骤1: 生成SSH密钥

```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "codebuddy@shcming2023"

# 或使用RSA算法
ssh-keygen -t rsa -b 4096 -C "codebuddy@shcming2023"
```

### 步骤2: 添加SSH密钥到GitHub

1. **复制公钥**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # 或
   cat ~/.ssh/id_rsa.pub
   ```

2. **添加到GitHub**
   - GitHub → Settings → SSH and GPG keys
   - "New SSH key"
   - Title: CodeBuddy SSH Key
   - 粘贴公钥内容
   - "Add SSH key"

### 步骤3: 配置SSH远程地址

```bash
# 使用SSH URL
git remote set-url origin git@github.com:shcming2023/Student_grade_system.git

# 测试连接
ssh -T git@github.com
```

## 🔄 方案3: 环境变量配置 (自动化)

### 创建环境配置文件

```bash
# 创建环境文件
cat > .env << EOF
GITHUB_TOKEN=your_personal_access_token_here
GITHUB_REPO=shcming2023/Student_grade_system
EOF

# 设置文件权限
chmod 600 .env
```

### 创建自动化同步脚本

```bash
#!/bin/bash
# auto_sync.sh - 自动同步脚本

source .env

# 添加远程仓库 (使用Token)
git remote add origin https://shcming2023:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git

# 推送代码
git push -u origin master
```

## 🛠️ 实际配置步骤

### 立即可用的配置命令

```bash
cd "/opt/Way To Future考试管理系统/Student_grade_system"

# 1. 获取您的Personal Access Token后，替换YOUR_TOKEN
TOKEN="YOUR_PERSONAL_ACCESS_TOKEN_HERE"

# 2. 配置远程仓库
git remote set-url origin https://shcming2023:${TOKEN}@github.com/shcming2023/Student_grade_system.git

# 3. 测试推送
git push -u origin master
```

## 🔒 安全最佳实践

### 1. Token安全
- ⚠️ 永远不要将Token提交到代码仓库
- ✅ 使用环境变量或配置文件
- ✅ 定期更换Token
- ✅ 设置Token过期时间

### 2. 文件权限
```bash
# 确保敏感文件权限正确
chmod 600 .env
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### 3. .gitignore配置
确保敏感文件不被提交:
```gitignore
.env
.github_token
*.token
config_local.py
```

## 🚀 快速开始脚本

我已为您创建自动化配置脚本:

```bash
# 运行私有仓库配置
./setup_private_repo.sh
```

## 📋 验证配置

```bash
# 检查远程仓库配置
git remote -v

# 测试连接
git ls-remote origin

# 查看仓库状态
git status
```

## 🔄 日常工作流程

```bash
# 1. 拉取最新更改
git pull origin master

# 2. 添加新更改
git add .

# 3. 提交更改
git commit -m "your commit message"

# 4. 推送到私有仓库
git push origin master
```

## 🆘 常见问题解决

### 问题1: Token权限不足
**解决:** 重新生成Token，确保勾选repo权限

### 问题2: SSH连接失败
**解决:** 检查SSH密钥是否正确添加到GitHub

### 问题3: 推送被拒绝
**解决:** 检查仓库地址和Token是否正确

---

## 📞 需要帮助？

如果配置过程中遇到问题，请提供:
1. 错误信息
2. 当前配置状态
3. 使用的方法 (Token/SSH)

我将帮您实时解决！