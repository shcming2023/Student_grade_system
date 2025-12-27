#!/bin/bash

# ============================================
# 学生成绩管理系统 - 停止脚本
# ============================================
# 使用方法：chmod +x stop.sh && ./stop.sh

echo "=========================================="
echo "停止学生成绩管理系统"
echo "=========================================="
echo ""

# 检查PID文件
if [ ! -f ".app.pid" ]; then
    echo "未找到运行中的应用进程"
    exit 0
fi

# 读取PID
APP_PID=$(cat .app.pid)

# 检查进程是否存在
if ! ps -p $APP_PID > /dev/null 2>&1; then
    echo "进程 $APP_PID 不存在，可能已经停止"
    rm -f .app.pid
    exit 0
fi

# 停止进程
echo "正在停止进程 $APP_PID..."
kill $APP_PID

# 等待进程结束
sleep 2

# 检查是否成功停止
if ps -p $APP_PID > /dev/null 2>&1; then
    echo "进程未响应，强制停止..."
    kill -9 $APP_PID
    sleep 1
fi

# 清理PID文件
rm -f .app.pid

echo "✓ 应用已停止"
