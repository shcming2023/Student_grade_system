# **橡心国际 Way To Future 考试管理系统 - 需求规格说明书 (PRD)**

| 文档版本 | 日期 | 作者 | 状态 | 备注 |
| :---- | :---- | :---- | :---- | :---- |
| **v4.0** | 2026-01-02 | Trae AI | **基线重置** | 根据现有 Python/Flask 架构及已实现功能进行全量修订，作为当前开发基线 |
| **v3.0** | 2025-12-28 | Gemini | 存档 | 原始规划版本（Node.js/React 架构） |

## **1. 项目概述 (Project Overview)**

### **1.1 项目背景**
“橡心国际 Way To Future”是橡心国际教育体系下的核心学术测评活动。本项目旨在构建一套**内网私有化部署**的数字化管理系统，解决传统 Excel 手工流转带来的数据分散、登分效率低、报表制作繁琐等问题。

### **1.2 核心目标**
构建一套轻量级、高可用的 **Web 端学生成绩管理系统**，实现：
1.  **数据集中化**：统一管理学生、试卷、成绩数据，支持一键备份与恢复。
2.  **流程规范化**：标准化“考试场次-试卷模板-考生报名-成绩录入”的业务流。
3.  **输出自动化**：自动计算模块得分率，生成含雷达图分析的 A4 双面 PDF 成绩单。
4.  **操作便捷化**：支持 Excel 批量导入导出，适配 iPad/PC 端高效登分。

### **1.3 技术架构 (Current Tech Stack)**
*   **后端框架**：Python 3.9+ / Flask 2.0+
*   **数据库**：SQLite (开发/测试) / MySQL 8.0+ (生产), SQLAlchemy ORM
*   **前端技术**：Bootstrap 5 + Jinja2 Templates + jQuery
*   **报表引擎**：ReportLab (PDF生成), Matplotlib/ReportLab Charts (图表)
*   **数据处理**：Pandas, OpenPyXL (Excel 处理)
*   **部署环境**：Docker / Shell Script (适配 Mac mini M4)

## **2. 用户角色与权限 (Roles & Permissions)**

系统采用 **RBAC (Role-Based Access Control)** 简化模型，仅支持内部员工登录，不对学生/家长开放登录。

### **2.1 角色定义**

| 角色 | 标识 | 权限范围 |
| :---- | :---- | :---- |
| **系统管理员** | `admin` | **全权掌控**：<br>1. 用户管理（创建教师、重置密码）。<br>2. 系统设置（公司信息、Logo）。<br>3. 数据管理（一键备份、全量导入导出）。<br>4. 所有业务功能（考试、试卷、成绩、报表）。 |
| **教师** | `teacher` | **业务执行**：<br>1. **考务**：查看考试场次、试卷模板。<br>2. **录入**：仅能对自己负责的试卷进行登分（需分配权限）。<br>3. **报表**：生成并下载成绩单。<br>4. **限制**：不可管理用户，不可修改系统设置。 |

### **2.2 账户体系**
*   **预置账户**：`admin` (初始密码 `admin123`)。
*   **注册机制**：仅支持管理员在后台创建账户，不支持公网自助注册。

## **3. 业务功能模块 (Functional Modules)**

### **3.1 基础数据管理**
*   **学校管理**：管理学校基础信息（名称、代码）。
*   **学生管理**：
    *   维护学生档案（学号、姓名、年级、性别、所属学校、班级）。
    *   支持 Excel 批量导入学生数据。
*   **教师管理**：管理员可增删改查教师账户，分配初始密码。

### **3.2 考试规划 (Exam Management)**
*   **考试场次 (Exam Session)**：
    *   定义考试活动（如“2025秋季期末考试”）。
    *   属性：名称、日期、类型（上午/下午）、时间段、状态。
*   **试卷模板 (Exam Template)**：
    *   定义试卷结构（关联科目、年级）。
    *   **题目管理**：细化到每道题的题号、模块、知识点、题型、分值。
    *   **教师分配**：指定出卷人（Creator）和阅卷人（Grader）。
    *   支持 Excel 模板导入试卷结构。

### **3.3 报名与考务 (Registration)**
*   **报名管理**：
    *   建立关联：学生 -> 考试场次 -> 试卷模板。
    *   支持 Excel 批量导入报名名单（含自动匹配逻辑）。
    *   **报考详情**：在学生列表页直观展示已报名的所有考试及试卷。
*   **考务排表**：支持导出考场签到表。

### **3.4 成绩录入 (Scoring)**
*   **Web 登分界面**：
    *   按“场次+试卷”筛选进入录入任务。
    *   **矩阵式录入**：横向展示题目，纵向展示学生。
    *   **实时校验**：输入分数超过满分值自动报错提示。
    *   **便捷操作**：支持 Tab 键快速切换，优化 iPad 触控体验。
*   **自动计算**：前端实时计算卷面总分，后端异步计算模块得分率。

### **3.5 报表与输出 (Reporting)**
*   **智能成绩单 (PDF)**：
    *   **规格**：A4 标准纸，双面排版。
    *   **内容**：
        *   **正面**：学生信息、考试信息、题目得分明细表。
        *   **反面**：六维能力雷达图（基于模块得分率）、AI/教师评语、校长签名。
    *   **技术实现**：基于 ReportLab 精确绘制，支持批量打包下载。
*   **统计分析**：
    *   提供考试维度的总分分布、平均分、及格率统计。

### **3.6 数据治理 (Data Governance)**
*   **一键全量备份**：
    *   将所有核心数据（场次、模板、学生、成绩、题目明细、报考详情）导出为多 Sheet Excel 文件。
*   **Excel 交互**：
    *   支持试卷结构导入。
    *   支持学生名单导入。
    *   支持 OCR 识别后的报名数据导入。

## **4. 数据模型 (Data Schema)**

基于 `SQLAlchemy` ORM 定义的核心实体：

### **4.1 用户与配置**
*   **User**: `id`, `username`, `password_hash`, `role`, `real_name`.
*   **SystemSetting**: `company_name`, `logo_path`.

### **4.2 基础档案**
*   **School**: `id`, `name`, `code`.
*   **Student**: `id`, `student_id`, `name`, `gender`, `grade_level`, `school_id`, `class_name`.
*   **Subject**: `id`, `name`, `code`, `type` (如 Oxford, Langford).

### **4.3 考务核心**
*   **ExamSession**: `id`, `name`, `exam_date`, `session_type`, `status`.
*   **ExamTemplate**: `id`, `name`, `subject_id`, `grade_level`, `total_questions`, `creator_id`, `grader_id`.
*   **Question**: `id`, `template_id`, `question_number`, `module`, `knowledge_point`, `score`.
*   **ExamRegistration**: `id`, `student_id`, `session_id`, `template_id`, `status` (registered/absent).
*   **Score**: `id`, `registration_id`, `question_id`, `score`, `is_correct`.

## **5. 非功能性需求 (NFR)**

1.  **部署便捷性**：必须提供 `start_student_system.sh` 一键启动脚本，自动处理 Python 虚拟环境与依赖。
2.  **数据安全性**：
    *   生产环境数据库 (`MySQL`) 与开发环境 (`SQLite`) 分离。
    *   敏感配置（密钥、数据库URL）通过环境变量注入。
3.  **性能要求**：
    *   PDF 批量生成速度需满足 100 份/分钟。
    *   登分界面支持 50+ 并发访问不卡顿。
4.  **兼容性**：
    *   服务端：适配 Linux (Ubuntu/Debian) 及 macOS (Apple Silicon)。
    *   客户端：适配 Chrome/Safari (Desktop) 及 Safari (iPad OS)。
