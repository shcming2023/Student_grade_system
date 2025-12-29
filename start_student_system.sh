#!/bin/bash
# 进入项目目录
cd "$(dirname "$0")/Student_grade_system"

# 停止旧进程
echo "Stopping existing server..."
pkill -f "wtf_app_simple" || true

# 等待进程结束
sleep 2

# 启动新进程
echo "Starting server..."
nohup python3 -c "from wtf_app_simple import app; app.run(host='0.0.0.0', port=8083, debug=False)" > app.log 2>&1 &

echo "Server started on port 8083"
