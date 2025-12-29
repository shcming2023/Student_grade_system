# 开发部门 (Trae/Buddy) 项目行动准则 V1.0

本文档是 **Way To Future 考试管理系统** 项目执行团队的官方行动准则，基于 **6A工作法** 进行本地化适配。所有开发活动必须严格遵循本准则，确保项目从需求到交付的稳步、有序、高质量推进。

---

## 1. 核心原则：SSOT (唯一事实来源)

所有开发工作必须严格对齐并最终更新至项目的 SSOT (Single Source of Truth) 体系：

- **“宪法” (Constitution)**:
  - 在动手编码前，**必须** 再次阅读 `../橡心国际 Way To Future 考试管理系统 - 需求规格说明书 (PRD).md`。
  - 任何与 PRD 冲突的变更，必须先请求修改 PRD，严禁擅自偏离需求。
- **“总账” (Ledger)**:
  - 任务的进度状态以 `todo.md` 为准。
  - 每日进度和重大变更必须同步至 `说明文档.md` 的 [进度记录] 模块。
- **“行动准则” (Code of Conduct)**:
  - 本文档 (`PROJECT_RULES.md`) 是你的行为规范，任何操作不得违背。

---

## 2. 开发工作流 (6A工作流之执行阶段)

你的核心职责聚焦于 **阶段5: Automate (执行)**，具体步骤如下：

1.  **接收任务 (Accept)**:
    - 明确 `todo.md` 中的当前优先级任务 (High Priority)。
    - 确认输入数据源（如 `基础数据/` 目录下的 Excel 模板）和预期输出。
2.  **环境准备 (Access)**:
    - 确保 `requirements.txt` 依赖已安装且版本一致。
    - 确保数据库 (SQLite/MySQL) 结构与 `models/` 定义同步。
    - 运行 `start_student_system.sh` 确认开发环境基准正常。
3.  **编码实现 (Act)**:
    - **原子化提交**: 每个功能点（如“新增API接口”、“修复导入Bug”）完成后立即 commit，严禁堆积代码。
    - **代码规范**: Python 代码需遵循 PEP 8，前端代码需保持缩进整洁，关键逻辑必须添加注释。
4.  **质量自检 (Analyze)**:
    - **数据验证**: 使用 `基础数据/` 中的真实 Excel 文件进行导入测试，确保无解析错误。
    - **逻辑验证**: 对照 PRD 中的 [验收标准] 逐条核对（如：分数录入是否校验上限、成绩单是否双面排版）。
5.  **交付打包 (Arrange)**:
    - 清理临时文件 (`__pycache__`, `.DS_Store`, 临时上传文件)。
    - 确保 `deploy.sh` 或 `start_student_system.sh` 脚本可直接运行新功能。
6.  **提交交付 (Apply)**:
    - 更新 `todo.md` 状态为 `[x]`。
    - 在 `说明文档.md` 中记录完成时间与产出物。
    - 发起 Git Push 同步至远程仓库。

---

## 3. 协同四大铁律 (Four Iron Laws)

### 铁律一：文档驱动开发
- **你的责任**: 任何代码变更如果影响了业务逻辑或数据结构，**必须** 同步更新 `说明文档.md` 或相关技术文档。
- **禁止**: 严禁只改代码不改文档，导致文档与代码“两张皮”。

### 铁律二：数据安全红线
- **你的责任**:
  - **绝不允许** 将真实的生产数据库文件 (sqlite.db) 或含有敏感信息的配置 (config.py 中包含密码) 提交到 Git。
  - 敏感信息必须通过环境变量或被 `.gitignore` 忽略的配置文件 (`instance/config.py`) 读取。
- **测试数据**: 开发测试只能使用 `基础数据/students_sample.xlsx` 等脱敏样例数据。

### 铁律三：环境清洁与复原
- **你的责任**: 每次交付前，必须运行测试脚本验证系统启动无误。
- **标准**: “在我机器上能跑”不是交付标准，标准是“在全新拉取的环境中执行 `start_student_system.sh` 能跑”。

### 铁律四：闭环反馈
- **你的责任**: 遇到 PRD 逻辑漏洞或技术不可行性（如 PDF 排版限制），必须立即反馈并记录在 `说明文档.md` 的 [问题/风险] 区域，而不是自行“魔改”需求。

---

## 4. 技术执行规范

### 4.1 数据一致性
- **Excel 导入**: 必须使用 `pandas` 或 `openpyxl` 处理 Excel，且必须包含 **数据校验层** (Validation Layer)，对必填项缺失、数据类型错误进行拦截并返回友好报错。
- **数据库事务**: 涉及多表写入的操作（如：导入试卷同时写入 Template 和 Questions 表），必须使用 `db.session.begin_nested()` 或 `try...except...rollback` 确保原子性。

### 4.2 接口规范
- **RESTful**: API 设计需遵循 REST 原则。
  - GET `/api/students` (查询)
  - POST `/api/students` (新增)
  - PUT/PATCH `/api/students/<id>` (修改)
  - DELETE `/api/students/<id>` (删除)
- **响应格式**: 统一使用 JSON 格式：
  ```json
  {
    "success": true,
    "data": { ... },
    "message": "操作成功"
  }
  ```

### 4.3 目录结构规范
- 所有业务代码位于 `Student_grade_system/` 根目录。
- 静态资源存放在 `static/`，模板存放在 `templates/`。
- 上传文件临时存储在 `uploads/` (需在 `.gitignore` 中忽略)。

---

## 5. 交付物清单 (Deliverables Checklist)

每次功能发布 (Release) 需包含：

1.  **源代码**: 提交至 Git 仓库。
2.  **依赖变更**: 如有新增库，更新 `requirements.txt`。
3.  **数据库迁移**: 如有 Schema 变更，提供 SQL 脚本或 Drizzle 迁移文件。
4.  **更新日志**: 在 `说明文档.md` 中更新版本记录 (Changelog)。
