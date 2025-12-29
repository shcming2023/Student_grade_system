#!/bin/bash

# 腾讯云CVM部署脚本
# 适用于 TencentOS Server 3.1

set -e

echo "开始部署 Way To Future 考试管理系统..."

# 1. 检查环境
echo "检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "Docker 未安装，正在安装..."
    yum install -y docker
    systemctl start docker
    systemctl enable docker
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose 未安装，正在安装..."
    # 安装 docker-compose (简化版，假设 docker plugin available or install standalone)
    # 对于 TencentOS，尝试 pip 或直接下载 binary
    curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 2. 准备目录
APP_DIR="/opt/Way To Future考试管理系统/Student_grade_system"
cd "$APP_DIR"

# 3. 构建与启动
echo "构建并启动服务..."
docker-compose down
docker-compose up -d --build

# 4. 检查状态
echo "等待服务启动..."
sleep 10
if curl -s http://localhost:8888 > /dev/null; then
    echo "服务启动成功！"
    echo "访问地址: http://$(curl -s ifconfig.me):8888"
else
    echo "服务启动可能失败，请检查 docker logs"
    docker-compose logs --tail=20
fi

# 5. 防火墙配置 (如果需要)
# TencentOS 可能使用 iptables 或 firewalld
if systemctl is-active firewalld &> /dev/null; then
    echo "配置防火墙开放 8888 端口..."
    firewall-cmd --zone=public --add-port=8888/tcp --permanent
    firewall-cmd --reload
fi

echo "部署完成！"
