#!/bin/bash

echo "🚀 启动学生成绩管理系统"
echo "================================"

# 进入项目目录
cd "/opt/Way To Future考试管理系统/Student_grade_system"

# 检查依赖
echo "📦 检查Python依赖..."
python3 -c "import flask, flask_sqlalchemy, reportlab" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少依赖，正在安装..."
    pip3 install -r requirements.txt
fi

# 停止现有进程
echo "🛑 停止现有进程..."
pkill -f "wtf_app_simple" 2>/dev/null
pkill -f "port=8083" 2>/dev/null

# 等待进程完全停止
sleep 2

# 在8083端口启动应用
echo "🌐 启动应用在8083端口..."
nohup python3 -c "
from wtf_app_simple import app
# 生产环境运行，关闭debug
app.run(host='0.0.0.0', port=8083, debug=False)
" > student_system.log 2>&1 &

# 等待应用启动
sleep 3

# 检查应用状态
echo "🔍 检查应用状态..."
if netstat -tlnp | grep :8083 >/dev/null; then
    echo "✅ 应用启动成功！"
    echo "📡 本地访问: http://localhost:8083"
    echo "🌐 公网访问: http://101.35.149.123:8083"
    echo "📋 进程信息:"
    ps aux | grep "python3.*8083" | grep -v grep
else
    echo "❌ 应用启动失败"
    echo "📄 查看日志:"
    tail -20 student_system.log
    exit 1
fi

# 测试HTTP响应
echo "🧪 测试HTTP响应..."
if curl -s http://localhost:8083 | head -5 >/dev/null; then
    echo "✅ HTTP响应正常"
else
    echo "❌ HTTP响应异常"
fi

echo ""
echo "🎉 学生成绩管理系统部署完成！"
echo ""
echo "📊 访问地址:"
echo "   本地: http://localhost:8083"
echo "   公网: http://101.35.149.123:8083"
echo ""
echo "🛠️ 管理命令:"
echo "   查看日志: tail -f student_system.log"
echo "   停止服务: pkill -f 'python3.*8083'"
echo "   重启服务: ./start_student_system.sh"
echo ""
echo "📱 主要功能:"
echo "   • 学生信息管理"
echo "   • 课程管理"
echo "   • 成绩录入"
echo "   • 数据统计"