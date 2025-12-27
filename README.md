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
├── app.py                 # Flask应用主文件
├── requirements.txt        # Python依赖
├── config.py             # 配置文件
├── static/               # 静态资源
│   ├── css/
│   ├── js/
│   └── images/
├── templates/            # HTML模板
├── models/              # 数据模型
├── utils/               # 工具函数
└── database/            # 数据库文件
```

## 安装运行

### 1. 环境要求
- Python 3.6+
- pip

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
python app.py
```

### 4. 访问应用
打开浏览器访问: http://localhost:5000

## API接口

### 学生管理
- `GET /api/students` - 获取学生列表
- `POST /api/students` - 添加学生
- `PUT /api/students/<id>` - 更新学生信息
- `DELETE /api/students/<id>` - 删除学生

### 成绩管理
- `GET /api/grades` - 获取成绩列表
- `POST /api/grades` - 录入成绩
- `PUT /api/grades/<id>` - 更新成绩
- `GET /api/grades/statistics` - 成绩统计

## 开发说明
- 数据库初始化: `python utils/init_db.py`
- 测试数据: `python utils/generate_test_data.py`

## 许可证
MIT License

## 作者
开发团队
```

## 快速开始

```bash
# 克隆项目
git clone https://github.com/shcming2023/Student_grade_system.git

# 进入项目目录
cd Student_grade_system

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

## 部署说明

### 本地部署
```bash
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