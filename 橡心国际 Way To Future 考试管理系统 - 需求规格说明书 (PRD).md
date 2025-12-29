# **橡心国际 Way To Future 考试管理系统 \- 需求规格说明书 (PRD)**

| 文档版本 | 日期 | 作者 | 状态 | 备注 |
| :---- | :---- | :---- | :---- | :---- |
| **v3.0** | 2025-12-28 | Gemini | **定稿** | 整合试卷CSV结构、报名签到、AI评语及系统/用户管理闭环 |

## **1\. 项目概述 (Project Overview)**

### **1.1 项目背景**

“橡心国际 Way To Future”是橡心国际教育体系下的核心学术测评活动，每年举办多次（如 2025-2026 学年 S1/S2 系列）。该活动涉及 G1-G6 多个年级、涵盖英语（朗文/牛津/先锋）、数学（中数/英数/竞赛）、语文等多个学科。

目前，考务工作主要依赖 Excel 手工流转，存在数据分散、登分效率低、报表制作繁琐（特别是雷达图和双面排版）等问题。

### **1.2 核心目标**

构建一套**内网私有化部署**的数字化管理系统，实现从“试卷规划”到“成绩单输出”的全链路闭环：

1. **规范化**：统一管理试卷结构（题号/模块/知识点/分值），支持 Excel/CSV 快速导入。  
2. **高效化**：通过 Web 端快速登分（按题录入）、自动计算总分与模块得分率。  
3. **智能化**：集成 AI 辅助生成个性化评语，自动生成含雷达图分析的 A4 双面 PDF 成绩单。  
4. **闭环管理**：严控用户权限，不支持自注册，确保数据安全。

### **1.3 技术架构 (Tech Stack)**

* **前端**：React 19 \+ Vite \+ TailwindCSS \+ Radix UI  
* **后端**：Node.js \+ tRPC (Type-safe API)  
* **数据库**：MySQL 8.0+ (Drizzle ORM)  
* **部署**：Docker 容器化部署于 Mac mini M4 (Intranet)  
* **AI服务**：OpenAI 兼容接口 (用于评语生成)

## **2\. 用户角色与权限 (Roles & Permissions)**

### **2.1 账户体系策略**

* **闭环管理**：系统**不支持**用户自行注册。所有账户仅能由【系统管理员】在后台手动创建与分发。  
* **默认账户**：系统初始化预置超级管理员账户。  
  * 用户名：admin  
  * 初始密码：admin123 (首次登录建议强制修改)

### **2.2 角色权限矩阵**

| 角色 | 标识 (Role ID) | 职能定义 | 核心权限范围 |
| :---- | :---- | :---- | :---- |
| **系统管理员** | admin | 全局控制 | 1\. **系统设置**：维护公司名称、上传 Logo。 2\. **用户管理**：创建/禁用账户、重置密码。 3\. **数据修正**：拥有对所有考务数据的最高修正权。 |
| **出卷老师** | creator | 试卷架构 | 1\. **试卷规划**：创建/编辑试卷模板，导入 CSV 结构。 2\. **考试发布**：定义考试系列与场次。 3\. **统计查看**：查看试卷维度的统计分析。 |
| **阅卷老师** | grader | 执行与交付 | 1\. **现场考务**：考场学生签到。 2\. **阅卷登分**：按题录入具体分数（仅限分配的任务）。 3\. **报告交付**：编辑/确认 AI 评语，下载成绩单。 |
| **学生/家长** | user | 终端查看 | *(未来规划)* 仅拥有查看个人历史成绩与报告的权限。 |

## **3\. 业务功能模块详解 (Functional Requirements)**

### **3.1 系统基础设置 (System Settings) \- *Admin Only***

* **公司信息配置**：  
  * **公司名称**：配置全局显示名称（如“橡心国际教育”）。  
  * **Logo 管理**：上传并存储公司 Logo（支持 PNG/JPG），此 Logo 将动态渲染于**系统登录页**及**成绩单 PDF 页眉**。  
* **用户管理**：  
  * **列表视图**：展示用户名、真实姓名、角色、状态（正常/禁用）、最后登录时间。  
  * **账户操作**：  
    * **新增用户**：输入用户名、密码、姓名、选择角色。  
    * **重置密码**：管理员可强制重置指定用户的密码。  
    * **禁用/启用**：可暂时封禁离职或异常账户。

### **3.2 考试规划与试卷管理 (Exam Planning)**

* **层级定义**：  
  * **Level 1 考试系列 (Series)**：定义大的学年活动，e.g., "2025-2026学年 第一学期 WTF测评"。  
  * **Level 2 试卷模板 (Paper Template)**：定义具体学科试卷，关联科目与年级。  
* **试卷结构导入 (CSV Import)**：  
  * **功能**：支持解析上传的 CSV 文件（参考 2025秋季...G1朗文英语.csv），自动建立试卷结构。  
  * **关键字段映射**：  
    * 题号 (Question No)：唯一标识。  
    * 模块 (Module)：e.g., "基础计算", "概念模块"。  
    * 知识点 (Knowledge Point)：e.g., "两位数加法", "一般过去时"。  
    * 题型 (Type)：e.g., "口算", "单项选择", "竖式计算"。  
    * 分值 (Score)：该题满分值。  
  * **校验**：导入时需校验总分是否匹配。

### **3.3 考务管理 (Session & Registration)**

* **场次管理 (Sessions)**：  
  * 在系列下创建具体场次。  
  * 属性：名称（e.g., "12月28日 上午场"）、时间、地点、监考老师。  
* **报名管理 (Registration)**：  
  * **关联关系**：建立 Student \-\> Session \-\> PaperTemplate 的多对多关系。  
  * **导入源**：支持 Excel 批量导入报名名单（包含学生信息及报考科目）。  
* **现场签到 (Check-in)**：  
  * **界面**：阅卷老师/考务人员可按场次查看学生名单。  
  * **操作**：标记学生状态为“已实到”或“缺考”。  
  * **逻辑约束**：未签到（缺考）的学生，其成绩录入入口应被锁定或标记。

### **3.4 阅卷与成绩录入 (Scoring)**

* **录入界面**：  
  * **筛选**：按“场次 \+ 试卷 \+ 班级”进入录入视图。  
  * **按题登分 (Question-Level Entry)**：  
    * 界面横向展示题目（Q1, Q2...），纵向展示学生。  
    * **高效操作**：支持 Tab 键快速切换下一个输入框，适配小键盘连续录入。  
  * **校验逻辑**：输入分数不得超过该题设定的满分值，否则前端报错提示。  
* **自动计算**：  
  * 前端实时计算卷面总分，给予即时反馈。  
  * 后台自动聚合“模块”得分，用于生成雷达图。

### **3.5 智能成绩单 (Smart Report Card)**

* **版式标准**：A4 纵向，双面布局 PDF。  
* **页面结构**：  
  * **正面 (Front Page)**：  
    * **页眉**：动态调用系统配置的 **Logo** 与 **公司名称**。  
    * **基本信息**：学生姓名、年级、科目、考试日期、总分。  
    * **成绩明细表**：详细列出每道题的题号、知识点、满分、实得分。  
  * **反面 (Back Page)**：  
    * **能力雷达图**：基于“模块”得分率自动生成（e.g., 计算力, 概念理解, 应用能力）。  
    * **简要分析**：系统基于得分率预置规则生成的简短客观描述（如“计算能力优秀，但在概念理解方面有待加强”）。  
    * **教师评语**：  
      * **AI 生成**：点击“AI 生成”按钮，调用 LLM 接口，根据学生薄弱点和亮点生成约 100 字评语。  
      * **人工修订**：老师可直接编辑 AI 生成的文本并保存最终版本。  
    * **页脚**：校长/教师电子签名区。

## **4\. 数据模型设计 (Data Schema)**

*(基于 drizzle/schema.ts 的核心实体定义)*

1. **SystemSettings**  
   * key (PK): varchar (e.g., 'company\_name', 'company\_logo\_url')  
   * value: text  
   * updatedAt: timestamp  
2. **Users**  
   * id: int (PK)  
   * username: varchar (unique)  
   * passwordHash: varchar  
   * fullName: varchar  
   * role: enum('admin', 'creator', 'grader')  
   * status: enum('active', 'inactive')  
3. **ExamSeries** (考试系列)  
   * id: int (PK)  
   * name: varchar (e.g., "2025秋季S1")  
   * academicYear: varchar  
   * semester: varchar  
4. **PaperTemplates** (试卷模板)  
   * id: int (PK)  
   * seriesId: int (FK \-\> ExamSeries)  
   * name: varchar (e.g., "G1朗文英语")  
   * subject: varchar  
   * grade: varchar  
   * totalScore: decimal  
5. **Questions** (题目)  
   * id: int (PK)  
   * templateId: int (FK \-\> PaperTemplates)  
   * number: int (题号)  
   * module: varchar (模块)  
   * knowledgePoint: text (知识点)  
   * type: varchar (题型)  
   * maxScore: decimal (满分)  
6. **ExamSessions** (场次)  
   * id: int (PK)  
   * seriesId: int (FK \-\> ExamSeries)  
   * name: varchar  
   * startTime: datetime  
   * location: varchar  
7. **Registrations** (报名记录)  
   * id: int (PK)  
   * studentId: int (FK)  
   * sessionId: int (FK \-\> ExamSessions)  
   * paperTemplateId: int (FK \-\> PaperTemplates)  
   * status: enum('registered', 'checked\_in', 'absent') (报名/实到/缺考)  
8. **Scores** (分数)  
   * id: int (PK)  
   * registrationId: int (FK \-\> Registrations)  
   * questionId: int (FK \-\> Questions)  
   * earnedScore: decimal  
9. **ReportCards** (成绩单)  
   * id: int (PK)  
   * registrationId: int (FK)  
   * aiComment: text (AI生成评语)  
   * teacherComment: text (最终评语)  
   * pdfUrl: varchar  
   * generatedAt: timestamp

## **5\. 开发里程碑 (Milestones)**

### **Phase 1: 核心基础 (P0) \- *预计周期：3天***

* **环境初始化**：配置 Docker、MySQL，初始化 Admin 账户。  
* **系统管理**：完成“公司设置”与“用户管理”功能，确保权限闭环。  
* **试卷工程**：实现 CSV 解析器，完美适配上传的 24 类试卷结构。

### **Phase 2: 业务流程 (P1) \- *预计周期：5天***

* **考务流**：考试系列 \-\> 场次 \-\> 报名 \-\> 签到 流程打通。  
* **登分系统**：开发高效率的 Web 登分界面（Grid 布局 \+ 键盘导航）。  
* **数据层**：实现分数校验与自动汇总逻辑。

### **Phase 3: 报表与AI (P1) \- *预计周期：4天***

* **PDF 引擎**：集成 PDF 生成库，实现 A4 双面精准排版（含页眉 Logo）。  
* **AI 集成**：对接 LLM 接口，调试 Prompt 以生成高质量评语。  
* **交付验收**：批量导出功能测试及部署。