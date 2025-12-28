#!/bin/bash

echo "🔐 私有仓库协同配置脚本"
echo "=================================="

# 检查当前目录
current_dir=$(pwd)
if [[ ! "$current_dir" == *"Student_grade_system"* ]]; then
    echo "❌ 请在Student_grade_system目录中运行此脚本"
    exit 1
fi

echo "✅ 当前目录: $(pwd)"

# 检查Git仓库
if [ ! -d ".git" ]; then
    echo "❌ Git仓库未初始化"
    exit 1
fi

echo "✅ Git仓库已初始化"

# 用户输入Token
echo ""
echo "🔑 配置GitHub Personal Access Token"
echo "================================="
echo "请按以下步骤获取Token:"
echo "1. 访问: https://github.com/shcming2023/settings/tokens"
echo "2. 点击 'Generate new token (classic)'"
echo "3. 选择权限: ✅ repo"
echo "4. 复制生成的Token"
echo ""

read -p "请输入您的Personal Access Token: " github_token

if [ -z "$github_token" ]; then
    echo "❌ Token不能为空"
    exit 1
fi

echo "✅ Token已输入"

# 配置远程仓库
repo_url="https://shcming2023:${github_token}@github.com/shcming2023/Student_grade_system.git"

echo ""
echo "🔧 配置远程仓库..."

# 检查是否已有远程仓库
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  检测到已有远程仓库，正在更新..."
    git remote set-url origin "$repo_url"
else
    echo "📡 添加远程仓库..."
    git remote add origin "$repo_url"
fi

echo "✅ 远程仓库配置完成"

# 测试连接
echo ""
echo "🔍 测试仓库连接..."

if git ls-remote origin >/dev/null 2>&1; then
    echo "✅ 仓库连接成功"
else
    echo "❌ 仓库连接失败"
    echo "🔧 可能的原因:"
    echo "  1. Token权限不足 (需要repo权限)"
    echo "  2. 仓库名称错误"
    echo "  3. 网络连接问题"
    exit 1
fi

# 检查当前分支
current_branch=$(git branch --show-current)
echo "📋 当前分支: $current_branch"

# 推送代码
echo ""
echo "🚀 推送代码到私有仓库..."

if git push -u origin "$current_branch"; then
    echo ""
    echo "🎉 推送成功！"
    echo ""
    echo "📊 仓库信息:"
    echo "🔗 仓库地址: https://github.com/shcming2023/Student_grade_system"
    echo "🔒 状态: 私有仓库"
    echo "📁 本地路径: $(pwd)"
    echo ""
    echo "🛠️  日常操作命令:"
    echo "  git pull origin $current_branch    # 拉取最新更改"
    echo "  git add .                        # 添加所有更改"
    echo "  git commit -m 'message'          # 提交更改"
    echo "  git push origin $current_branch    # 推送更改"
    echo ""
    echo "🔐 安全提醒:"
    echo "  ✅ Token已配置，不要泄露给他人"
    echo "  ✅ Token已保存到Git remote配置中"
    echo "  ⚠️  建议定期更换Token"
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "🔧 解决方案:"
    echo "1. 检查Token是否有效且具有repo权限"
    echo "2. 确认私有仓库已创建"
    echo "3. 检查网络连接"
    echo ""
    echo "📞 如需帮助，请提供错误信息"
fi

# 创建环境变量文件 (可选)
echo ""
read -p "是否创建.env文件保存Token配置? (y/n): " create_env

if [[ "$create_env" == "y" || "$create_env" == "Y" ]]; then
    cat > .env << EOF
# GitHub配置 - 私有仓库访问
GITHUB_TOKEN=${github_token}
GITHUB_USER=shcming2023
GITHUB_REPO=Student_grade_system
EOF
    
    chmod 600 .env
    echo "✅ .env文件已创建 (权限: 600)"
    echo "⚠️  .env文件已在.gitignore中，不会被提交"
fi

# 验证配置
echo ""
echo "🔍 验证配置..."
echo "远程仓库:"
git remote -v

echo ""
echo "📋 推送历史:"
git log --oneline -5

echo ""
echo "✅ 私有仓库协同配置完成！"