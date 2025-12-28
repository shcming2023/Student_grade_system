#!/bin/bash

echo "🚀 GitHub仓库设置和推送脚本"
echo "================================"

# 检查当前目录
current_dir=$(pwd)
if [[ ! "$current_dir" == *"Student_grade_system"* ]]; then
    echo "❌ 请在Student_grade_system目录中运行此脚本"
    exit 1
fi

echo "✅ 当前目录: $(pwd)"

# 检查Git仓库状态
if [ ! -d ".git" ]; then
    echo "❌ Git仓库未初始化"
    exit 1
fi

echo "✅ Git仓库已初始化"

# 获取GitHub用户名
echo ""
echo "📋 请确认GitHub信息:"
echo "用户名: shcming2023"
echo "仓库名: Student_grade_system"
echo ""

# 询问仓库URL
echo "请选择仓库类型:"
echo "1. HTTPS (https://github.com/shcming2023/Student_grade_system.git)"
echo "2. SSH (git@github.com:shcming2023/Student_grade_system.git)"
read -p "请输入选择 (1 或 2): " choice

case $choice in
    1)
        repo_url="https://github.com/shcming2023/Student_grade_system.git"
        echo "✅ 选择HTTPS方式"
        ;;
    2)
        repo_url="git@github.com:shcming2023/Student_grade_system.git"
        echo "✅ 选择SSH方式"
        ;;
    *)
        echo "❌ 无效选择，使用HTTPS"
        repo_url="https://github.com/shcming2023/Student_grade_system.git"
        ;;
esac

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
echo "📡 仓库URL: $repo_url"

echo ""
echo "🔍 检查连接..."

# 测试连接
if [[ "$repo_url" == git@* ]]; then
    echo "测试SSH连接..."
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ SSH连接成功"
    else
        echo "❌ SSH连接失败，请检查SSH密钥配置"
        echo "💡 建议使用HTTPS方式或配置SSH密钥"
        exit 1
    fi
else
    echo "✅ HTTPS方式无需额外配置"
fi

echo ""
echo "🚀 准备推送代码..."

# 检查当前分支
current_branch=$(git branch --show-current)
echo "当前分支: $current_branch"

# 推送代码
echo "正在推送到GitHub..."
git push -u origin $current_branch

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 推送成功！"
    echo ""
    echo "📊 仓库信息:"
    echo "🔗 仓库地址: https://github.com/shcming2023/Student_grade_system"
    echo "📁 本地路径: $(pwd)"
    echo ""
    echo "🛠️  后续操作:"
    echo "  git status                    # 查看状态"
    echo "  git add .                    # 添加更改"
    echo "  git commit -m 'message'      # 提交更改"
    echo "  git push origin $current_branch # 推送更改"
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "🔧 可能的解决方案:"
    echo "1. 确认仓库已在GitHub创建并设置为Public"
    echo "2. 检查网络连接"
    echo "3. 如果使用HTTPS，确认GitHub访问权限"
    echo "4. 如果使用SSH，确认SSH密钥已配置"
fi

echo ""
echo "📝 提交规范建议:"
echo "  feat: 新功能"
echo "  fix: 修复bug"
echo "  docs: 文档更新"
echo "  style: 代码格式调整"
echo "  refactor: 代码重构"
echo "  test: 测试相关"