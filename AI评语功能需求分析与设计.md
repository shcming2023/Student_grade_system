# AI评语功能需求分析与设计

## 1. 新增需求分析

### 1.1 核心需求变更

| 需求编号 | 需求描述 | 影响范围 |
| :--- | :--- | :--- |
| **R1** | 每个成绩单最多生成3次AI评语，超过提示限额用完 | 数据库、后端API、前端UI |
| **R2** | 3次生成的评语都保留，可查看历史版本 | 数据库结构重大变更 |
| **R3** | 生成前校验成绩是否填写完整，未完成需二次确认 | 后端API、前端交互 |
| **R4** | AI评语仅供教师参考，需修改确认后才能正式使用 | 数据库、业务流程 |
| **R5** | 系统设置中配置LLM API（DeepSeek） | 系统设置表、后端配置 |

### 1.2 业务流程设计

```
教师进入成绩录入页面
  ↓
填写学生成绩
  ↓
点击"生成AI评语"
  ↓
系统检查：是否已生成3次？
  ├─ 是 → 提示"已达生成上限(3/3)"，禁用按钮
  └─ 否 → 继续
       ↓
       系统检查：成绩是否填写完整？
       ├─ 否 → 弹窗确认："检测到部分题目未填写成绩，是否继续生成评语？"
       │        ├─ 取消 → 中止
       │        └─ 确认 → 继续
       └─ 是 → 继续
            ↓
            调用DeepSeek API生成评语
            ↓
            保存为新版本（版本号+1）
            ↓
            展示评语，状态为"草稿"
            ↓
            教师修改评语
            ↓
            点击"确认使用"
            ↓
            评语状态变为"已确认"，用于成绩单PDF生成
```

## 2. 数据库设计

### 2.1 新增表：AICommentHistory（AI评语历史）

用于存储每次生成的AI评语记录。

| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | 主键 | PRIMARY KEY |
| `registration_id` | INTEGER | 关联的报名记录ID | FOREIGN KEY → ExamRegistration |
| `version` | INTEGER | 版本号（1, 2, 3） | NOT NULL |
| `content` | TEXT | AI生成的评语内容 | NOT NULL |
| `is_ai_generated` | BOOLEAN | 是否由AI生成（true）还是规则生成（false） | DEFAULT true |
| `status` | VARCHAR(20) | 状态：draft（草稿）/ confirmed（已确认） | DEFAULT 'draft' |
| `generated_at` | DATETIME | 生成时间 | DEFAULT CURRENT_TIMESTAMP |
| `confirmed_at` | DATETIME | 确认时间 | NULL |
| `confirmed_by` | INTEGER | 确认人（教师ID） | FOREIGN KEY → User |

**索引**:
- `(registration_id, version)` - 唯一索引，确保同一报名记录的版本号不重复

### 2.2 修改表：ReportCard

原有的 `ReportCard` 表保留，但 `ai_comment` 和 `teacher_comment` 字段的语义调整：
- `ai_comment`: **弃用**（保留字段以兼容旧数据）
- `teacher_comment`: 改为存储**最终确认的评语**（来自AICommentHistory中状态为confirmed的最新记录）

或者，更简洁的方案是：
- 在 `ReportCard` 表中新增 `confirmed_comment_id` 字段，关联到 `AICommentHistory.id`
- PDF生成时，查询该ID对应的评语内容

**推荐方案**：新增字段 `confirmed_comment_id`

| 字段名 | 类型 | 说明 | 约束 |
| :--- | :--- | :--- | :--- |
| `confirmed_comment_id` | INTEGER | 已确认的评语ID | FOREIGN KEY → AICommentHistory |

### 2.3 修改表：SystemSetting

在现有的 `SystemSetting` 表中新增字段：

| 字段名 | 类型 | 说明 | 默认值 |
| :--- | :--- | :--- | :--- |
| `llm_api_provider` | VARCHAR(50) | LLM服务商（如：deepseek, openai） | 'deepseek' |
| `llm_api_key` | VARCHAR(255) | LLM API密钥 | NULL |
| `llm_api_base_url` | VARCHAR(255) | LLM API Base URL | 'https://api.deepseek.com' |
| `llm_model` | VARCHAR(100) | 使用的模型名称 | 'deepseek-chat' |

## 3. API设计

### 3.1 生成AI评语

**接口**: `POST /api/ai-comment/generate`

**请求参数**:
```json
{
  "student_id": 123,
  "template_name": "数学期中测评",
  "force": false  // 是否强制生成（成绩未填完时）
}
```

**响应**:
- **成功（200）**:
  ```json
  {
    "success": true,
    "comment": {
      "id": 456,
      "version": 2,
      "content": "张三同学在本次...",
      "is_ai_generated": true,
      "status": "draft",
      "generated_at": "2026-01-03T10:30:00Z"
    },
    "remaining_quota": 1  // 剩余可生成次数
  }
  ```

- **达到上限（400）**:
  ```json
  {
    "success": false,
    "error": "quota_exceeded",
    "message": "已达到生成上限（3/3），无法继续生成。"
  }
  ```

- **成绩未填完（400）**:
  ```json
  {
    "success": false,
    "error": "incomplete_scores",
    "message": "检测到部分题目未填写成绩，请确认后重试。",
    "missing_count": 5,  // 未填写的题目数量
    "total_count": 20    // 总题目数量
  }
  ```

### 3.2 获取评语历史

**接口**: `GET /api/ai-comment/history?student_id=123&template_name=数学期中测评`

**响应**:
```json
{
  "success": true,
  "history": [
    {
      "id": 454,
      "version": 1,
      "content": "...",
      "status": "draft",
      "generated_at": "2026-01-03T10:00:00Z"
    },
    {
      "id": 456,
      "version": 2,
      "content": "...",
      "status": "confirmed",
      "generated_at": "2026-01-03T10:30:00Z",
      "confirmed_at": "2026-01-03T10:35:00Z"
    }
  ],
  "quota": {
    "used": 2,
    "total": 3,
    "remaining": 1
  }
}
```

### 3.3 确认使用评语

**接口**: `POST /api/ai-comment/confirm`

**请求参数**:
```json
{
  "comment_id": 456,
  "content": "张三同学在本次...(教师修改后的内容)"
}
```

**响应**:
```json
{
  "success": true,
  "message": "评语已确认"
}
```

**副作用**:
- 更新 `AICommentHistory` 表中该记录的 `status` 为 `confirmed`
- 更新 `content` 为教师修改后的内容
- 更新 `ReportCard` 表中的 `confirmed_comment_id` 为该评语ID

### 3.4 系统设置API

**接口**: `POST /api/settings/llm`

**请求参数**:
```json
{
  "provider": "deepseek",
  "api_key": "sk-xxxxx",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}
```

**响应**:
```json
{
  "success": true,
  "message": "LLM配置已更新"
}
```

## 4. 前端交互设计

### 4.1 成绩录入页面

**新增元素**:
1. **生成次数提示**: "AI评语生成次数：2/3"
2. **生成按钮状态**:
   - 未达上限：`<button>生成AI评语</button>`
   - 已达上限：`<button disabled>已达生成上限(3/3)</button>`
3. **查看历史按钮**: `<button>查看历史评语</button>`

**交互流程**:
1. 点击"生成AI评语"
2. 如果成绩未填完，弹窗确认：
   ```
   检测到20道题目中有5道未填写成绩，是否继续生成评语？
   [取消] [继续生成]
   ```
3. 生成中显示加载动画
4. 生成后，评语文本框变为可编辑状态，底部显示：
   ```
   [确认使用此评语] [重新生成(1/3剩余)]
   ```

### 4.2 历史评语弹窗

**布局**:
```
┌─────────────────────────────────────┐
│ 历史评语 (2/3)                      │
├─────────────────────────────────────┤
│ 版本1 - 2026-01-03 10:00 (草稿)    │
│ 张三同学在本次...                   │
│ [查看详情]                          │
├─────────────────────────────────────┤
│ 版本2 - 2026-01-03 10:30 ✓已确认   │
│ 张三同学在本次...(修改后)           │
│ [查看详情] [使用此版本]             │
└─────────────────────────────────────┘
```

### 4.3 系统设置页面

**新增LLM配置区块**:
```
┌─────────────────────────────────────┐
│ LLM API 配置                        │
├─────────────────────────────────────┤
│ 服务商: [DeepSeek ▼]                │
│ API Key: [********************]     │
│ Base URL: [https://api.deepseek.com]│
│ 模型: [deepseek-chat]               │
│ [测试连接] [保存配置]               │
└─────────────────────────────────────┘
```

## 5. 技术实现要点

### 5.1 成绩完整性检查

```python
def check_scores_completeness(student_id, template_id):
    """
    检查学生在某试卷下的成绩是否填写完整
    返回: (is_complete, missing_count, total_count)
    """
    questions = Question.query.filter_by(exam_template_id=template_id).all()
    total_count = len(questions)
    
    scores = Score.query.filter(
        Score.student_id == student_id,
        Score.question_id.in_([q.id for q in questions])
    ).all()
    
    filled_count = len(scores)
    missing_count = total_count - filled_count
    
    return (missing_count == 0, missing_count, total_count)
```

### 5.2 生成次数限制检查

```python
def check_generation_quota(registration_id):
    """
    检查AI评语生成次数配额
    返回: (can_generate, used_count, remaining_count)
    """
    MAX_GENERATIONS = 3
    
    used_count = AICommentHistory.query.filter_by(
        registration_id=registration_id
    ).count()
    
    remaining_count = MAX_GENERATIONS - used_count
    can_generate = remaining_count > 0
    
    return (can_generate, used_count, remaining_count)
```

### 5.3 DeepSeek API调用

```python
from openai import OpenAI

def get_llm_client():
    """根据系统设置获取LLM客户端"""
    setting = SystemSetting.query.first()
    
    return OpenAI(
        api_key=setting.llm_api_key,
        base_url=setting.llm_api_base_url
    )

def generate_with_deepseek(data):
    """使用DeepSeek生成评语"""
    client = get_llm_client()
    setting = SystemSetting.query.first()
    
    response = client.chat.completions.create(
        model=setting.llm_model or "deepseek-chat",
        messages=[...],
        temperature=0.7
    )
    
    return response.choices[0].message.content
```

## 6. 迁移方案

对于已有的旧数据（ReportCard表中的ai_comment字段）：

1. 创建数据迁移脚本
2. 将现有的 `ai_comment` 迁移到 `AICommentHistory` 表，版本号为1，状态为confirmed
3. 更新 `ReportCard.confirmed_comment_id` 指向迁移后的记录
