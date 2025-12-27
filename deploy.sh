#!/bin/bash

# ============================================
# 学生成绩管理系统 - Mac mini M4 部署脚本
# ============================================
# 此脚本用于在Mac mini M4服务器上部署应用
# 使用方法：chmod +x deploy.sh && ./deploy.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "学生成绩管理系统 - 部署脚本"
echo "=========================================="
echo ""

# 检查Node.js版本
echo "检查Node.js版本..."
if ! command -v node &> /dev/null; then
    echo "错误：未找到Node.js，请先安装Node.js 18或更高版本"
    echo "访问 https://nodejs.org/ 下载安装"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "错误：Node.js版本过低（当前：$(node -v)），需要18或更高版本"
    exit 1
fi
echo "✓ Node.js版本：$(node -v)"
echo ""

# 检查pnpm
echo "检查pnpm..."
if ! command -v pnpm &> /dev/null; then
    echo "未找到pnpm，正在安装..."
    npm install -g pnpm
fi
echo "✓ pnpm版本：$(pnpm -v)"
echo ""

# 检查MySQL
echo "检查MySQL连接..."
if ! command -v mysql &> /dev/null; then
    echo "警告：未找到mysql命令行工具"
    echo "请确保MySQL已安装并运行"
    echo "macOS安装方法：brew install mysql"
fi
echo ""

# 检查环境配置文件
echo "检查环境配置..."
if [ ! -f ".env.production" ]; then
    echo "错误：未找到.env.production文件"
    echo "请复制.env.production.template为.env.production并填写配置"
    exit 1
fi
echo "✓ 环境配置文件存在"
echo ""

# 安装依赖
echo "安装依赖包..."
pnpm install --frozen-lockfile
echo "✓ 依赖安装完成"
echo ""

# 运行数据库迁移
echo "运行数据库迁移..."
pnpm db:push
echo "✓ 数据库迁移完成"
echo ""

# 构建生产版本
echo "构建生产版本..."
pnpm build
echo "✓ 构建完成"
echo ""

echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 如需导入24套试卷数据，运行："
echo "   node import-exam-templates.mjs"
echo ""
echo "2. 启动应用："
echo "   ./start.sh"
echo ""
echo "3. 访问应用："
echo "   http://localhost:3000"
echo "   或"
echo "   http://$(ipconfig getifaddr en0):3000  (局域网访问)"
echo ""
echo "4. 停止应用："
echo "   ./stop.sh"
echo ""
