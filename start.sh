#!/bin/bash

# ============================================
# 学生成绩管理系统 - 启动脚本
# ============================================
# 使用方法：chmod +x start.sh && ./start.sh

set -e

echo "=========================================="
echo "启动学生成绩管理系统"
echo "=========================================="
echo ""

# 检查是否已构建
if [ ! -d "dist" ]; then
    echo "错误：未找到构建文件"
    echo "请先运行部署脚本：./deploy.sh"
    exit 1
fi

# 检查环境配置
if [ ! -f ".env.production" ]; then
    echo "错误：未找到.env.production文件"
    exit 1
fi

# 加载环境变量
export $(cat .env.production | grep -v '^#' | xargs)

# 获取端口（默认3000）
PORT=${PORT:-3000}

# 检查端口是否被占用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "警告：端口 $PORT 已被占用"
    echo "请先停止占用该端口的进程，或修改.env.production中的PORT配置"
    exit 1
fi

# 启动应用（后台运行）
echo "正在启动应用..."
echo "端口：$PORT"
echo ""

nohup pnpm start > logs/app.log 2>&1 &
APP_PID=$!

# 保存PID
echo $APP_PID > .app.pid

# 等待启动
sleep 3

# 检查是否成功启动
if ps -p $APP_PID > /dev/null 2>&1; then
    echo "✓ 应用启动成功！"
    echo ""
    echo "访问地址："
    echo "  本机：http://localhost:$PORT"
    
    # 获取局域网IP
    LAN_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "未获取到")
    if [ "$LAN_IP" != "未获取到" ]; then
        echo "  局域网：http://$LAN_IP:$PORT"
    fi
    
    echo ""
    echo "进程ID：$APP_PID"
    echo "日志文件：logs/app.log"
    echo ""
    echo "查看日志："
    echo "  tail -f logs/app.log"
    echo ""
    echo "停止应用："
    echo "  ./stop.sh"
else
    echo "✗ 应用启动失败"
    echo "请查看日志文件：logs/app.log"
    exit 1
fi
