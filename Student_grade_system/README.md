# 学生成绩管理系统 (Student Grade Management System)

## 项目简介
这是一个基于Web的学生成绩管理系统，提供学生信息管理、成绩录入、查询统计等功能。

## 功能特性
- 学生信息管理 (增删改查)
- 成绩录入与管理
- 成绩统计分析
- 班级管理
- 教师管理
- 数据导入导出

## 技术栈
- **前端**: HTML5, CSS3, JavaScript
- **后端**: Python Flask
- **数据库**: SQLite (开发环境) / MySQL (生产环境)
- **UI框架**: Bootstrap 5
- **图表库**: Chart.js

## 项目结构
```
Student_grade_system/
├── wtf_app_simple.py       # Flask应用主文件 (单文件架构)
├── requirements.txt        # Python依赖
├── static/                 # 静态资源 (CSS/JS/Images)
├── templates/              # HTML模板
├── start_student_system.sh # 启动脚本 (端口 8083)
├── Dockerfile              # Docker构建文件
├── docker-compose.yml      # Docker编排文件
├── DEPLOYMENT.md           # 部署文档
├── PROJECT_RULES.md        # 项目行动准则 (SSOT)
├── 说明文档.md              # 项目进度与说明
├── todo.md                 # 任务清单
└── 基础数据/               # Excel导入模板与示例数据
```

## 安装运行

### 1. 环境要求
- Python 3.9+
- pip

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
# 开发模式
python wtf_app_simple.py

# 生产模式 (推荐)
./start_student_system.sh
```

### 4. 访问应用
打开浏览器访问: 
- 本地: http://localhost:8083
- 公网: http://101.35.149.123:8083

## API接口
（参考 wtf_app_simple.py 中的路由定义）

## 开发说明
本项目采用单文件架构 (`wtf_app_simple.py`) 以简化维护。
所有新功能开发需遵循 `PROJECT_RULES.md`。

## 许可证
Private
# 使用Flask内置服务器
python app.py

# 使用Gunicorn (推荐)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker部署
```bash
# 构建镜像
docker build -t student-grade-system .

# 运行容器
docker run -p 5000:5000 student-grade-system
```

## 更新日志
- v1.0.0 - 初始版本发布
- v1.1.0 - 添加成绩统计功能
- v1.2.0 - 优化用户界面

## 贡献指南
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request