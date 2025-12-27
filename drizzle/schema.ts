import { int, mysqlEnum, mysqlTable, text, timestamp, varchar, decimal, boolean, index } from "drizzle-orm/mysql-core";

/**
 * 用户表 - 教师账户
 * 包含基础认证信息和角色权限
 */
export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * 教师表
 * 存储教师账户信息、密码和权限
 */
export const teachers = mysqlTable("teachers", {
  id: int("id").autoincrement().primaryKey(),
  username: varchar("username", { length: 50 }).notNull().unique(), // 登录用户名
  password: varchar("password", { length: 255 }).notNull(), // 加密后的密码
  name: varchar("name", { length: 100 }).notNull(), // 教师姓名
  email: varchar("email", { length: 320 }), // 邮箱
  phone: varchar("phone", { length: 20 }), // 电话
  role: mysqlEnum("role", ["admin", "teacher"]).default("teacher").notNull(), // 系统角色：管理员、普通教师
  status: mysqlEnum("status", ["active", "inactive"]).default("active").notNull(), // 状态
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastLoginAt: timestamp("lastLoginAt"), // 最后登录时间
});

export type Teacher = typeof teachers.$inferSelect;
export type InsertTeacher = typeof teachers.$inferInsert;

/**
 * 年级表
 * 存储年级信息（G1-G6）
 */
export const grades = mysqlTable("grades", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 50 }).notNull().unique(), // G1, G2, G3, G4, G5, G6
  displayName: varchar("displayName", { length: 100 }).notNull(), // 一年级, 二年级等
  sortOrder: int("sortOrder").notNull(), // 排序顺序
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Grade = typeof grades.$inferSelect;
export type InsertGrade = typeof grades.$inferInsert;

/**
 * 班级表
 * 存储班级信息，关联年级
 */
export const classes = mysqlTable("classes", {
  id: int("id").autoincrement().primaryKey(),
  gradeId: int("gradeId").notNull(), // 关联年级
  name: varchar("name", { length: 100 }).notNull(), // 班级名称，如"1班"
  fullName: varchar("fullName", { length: 200 }).notNull(), // 完整名称，如"G1-1班"
  teacherId: int("teacherId"), // 班主任ID
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  gradeIdx: index("grade_idx").on(table.gradeId),
}));

export type Class = typeof classes.$inferSelect;
export type InsertClass = typeof classes.$inferInsert;

/**
 * 科目表
 * 存储科目信息（朗文英语、牛津英语、先锋英语、中数、英数、语文）
 */
export const subjects = mysqlTable("subjects", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 100 }).notNull().unique(), // 科目名称
  code: varchar("code", { length: 50 }).notNull().unique(), // 科目代码，如"longman_english"
  category: varchar("category", { length: 50 }).notNull(), // 科目分类：english, math, chinese
  description: text("description"), // 科目描述
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Subject = typeof subjects.$inferSelect;
export type InsertSubject = typeof subjects.$inferInsert;

/**
 * 学生表
 * 存储学生基本信息
 */
export const students = mysqlTable("students", {
  id: int("id").autoincrement().primaryKey(),
  studentNumber: varchar("studentNumber", { length: 50 }).notNull().unique(), // 学号
  name: varchar("name", { length: 100 }).notNull(), // 姓名
  classId: int("classId").notNull(), // 所属班级
  gender: mysqlEnum("gender", ["male", "female"]), // 性别
  dateOfBirth: timestamp("dateOfBirth"), // 出生日期
  parentContact: varchar("parentContact", { length: 100 }), // 家长联系方式
  status: mysqlEnum("status", ["active", "inactive"]).default("active").notNull(), // 状态
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  classIdx: index("class_idx").on(table.classId),
}));

export type Student = typeof students.$inferSelect;
export type InsertStudent = typeof students.$inferInsert;

/**
 * 考试管理表（新增）
 * 存储考试的整体信息，如"2025-2026学年Way To Future考试 S2"
 */
export const examSessions = mysqlTable("exam_sessions", {
  id: int("id").autoincrement().primaryKey(),
  name: varchar("name", { length: 200 }).notNull().unique(), // 考试名称，不能重名
  schoolYear: varchar("schoolYear", { length: 50 }).notNull(), // 学年，如"2025-2026"
  semester: varchar("semester", { length: 20 }).notNull(), // 学期，如"S1", "S2"
  startDate: timestamp("startDate"), // 考试开始日期
  endDate: timestamp("endDate"), // 考试结束日期
  description: text("description"), // 考试描述
  status: mysqlEnum("status", ["draft", "active", "completed", "archived"]).default("draft").notNull(),
  createdBy: int("createdBy").notNull(), // 创建人（教师ID）
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type ExamSession = typeof examSessions.$inferSelect;
export type InsertExamSession = typeof examSessions.$inferInsert;

/**
 * 试卷模板表
 * 存储试卷的基本信息和结构
 */
export const examTemplates = mysqlTable("exam_templates", {
  id: int("id").autoincrement().primaryKey(),
  examSessionId: int("examSessionId").notNull(), // 关联考试
  name: varchar("name", { length: 200 }).notNull(), // 试卷名称，如"G1朗文英语"
  subjectId: int("subjectId").notNull(), // 关联科目
  gradeId: int("gradeId").notNull(), // 关联年级
  totalScore: decimal("totalScore", { precision: 5, scale: 1 }).notNull(), // 总分
  description: text("description"), // 试卷描述
  createdBy: int("createdBy").notNull(), // 创建人
  creatorId: int("creatorId"), // 出卷老师ID（可选）
  graderId: int("graderId"), // 阅卷老师ID（可选）
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  examSessionIdx: index("exam_session_idx").on(table.examSessionId),
  subjectGradeIdx: index("subject_grade_idx").on(table.subjectId, table.gradeId),
}));

export type ExamTemplate = typeof examTemplates.$inferSelect;
export type InsertExamTemplate = typeof examTemplates.$inferInsert;

/**
 * 题目表
 * 存储试卷中的每道题目信息
 */
export const questions = mysqlTable("questions", {
  id: int("id").autoincrement().primaryKey(),
  examTemplateId: int("examTemplateId").notNull(), // 关联试卷模板
  questionNumber: int("questionNumber").notNull(), // 题号
  module: varchar("module", { length: 100 }), // 模块
  knowledgePoint: text("knowledgePoint"), // 核心知识点/技能
  questionType: varchar("questionType", { length: 100 }), // 题型
  score: decimal("score", { precision: 5, scale: 1 }).notNull(), // 分值
  sortOrder: int("sortOrder").notNull(), // 排序顺序
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  examTemplateIdx: index("exam_template_idx").on(table.examTemplateId),
}));

export type Question = typeof questions.$inferSelect;
export type InsertQuestion = typeof questions.$inferInsert;

/**
 * 考试试卷表（重构）
 * 记录某次考试中的具体试卷，关联考试管理、试卷模板、教师和学生
 */
export const exams = mysqlTable("exams", {
  id: int("id").autoincrement().primaryKey(),
  examSessionId: int("examSessionId"), // 关联考试管理（可选，渐进式迁移）
  examTemplateId: int("examTemplateId").notNull(), // 关联试卷模板
  classId: int("classId").notNull(), // 关联班级
  examDate: timestamp("examDate").notNull(), // 考试日期
  name: varchar("name", { length: 200 }).notNull(), // 试卷名称
  creatorTeacherId: int("creatorTeacherId"), // 出卷老师ID（可选，渐进式迁移）
  graderTeacherId: int("graderTeacherId"), // 阅卷老师ID
  status: mysqlEnum("status", ["draft", "published", "completed"]).default("draft").notNull(),
  createdBy: int("createdBy").notNull(), // 创建人
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  examSessionIdx: index("exam_session_idx").on(table.examSessionId),
  classIdx: index("class_idx").on(table.classId),
  examTemplateIdx: index("exam_template_idx").on(table.examTemplateId),
  creatorTeacherIdx: index("creator_teacher_idx").on(table.creatorTeacherId),
  graderTeacherIdx: index("grader_teacher_idx").on(table.graderTeacherId),
}));

export type Exam = typeof exams.$inferSelect;
export type InsertExam = typeof exams.$inferInsert;

/**
 * 试卷-学生关联表（新增）
 * 记录哪些学生参加哪个试卷
 */
export const examStudents = mysqlTable("exam_students", {
  id: int("id").autoincrement().primaryKey(),
  examId: int("examId").notNull(), // 关联试卷
  studentId: int("studentId").notNull(), // 关联学生
  createdAt: timestamp("createdAt").defaultNow().notNull(),
}, (table) => ({
  examStudentIdx: index("exam_student_idx").on(table.examId, table.studentId),
}));

export type ExamStudent = typeof examStudents.$inferSelect;
export type InsertExamStudent = typeof examStudents.$inferInsert;

/**
 * 成绩记录表
 * 存储学生每道题的得分
 */
export const scores = mysqlTable("scores", {
  id: int("id").autoincrement().primaryKey(),
  examId: int("examId").notNull(), // 关联考试
  studentId: int("studentId").notNull(), // 关联学生
  questionId: int("questionId").notNull(), // 关联题目
  score: decimal("score", { precision: 5, scale: 1 }).notNull(), // 得分
  createdBy: int("createdBy").notNull(), // 录入人
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  examStudentIdx: index("exam_student_idx").on(table.examId, table.studentId),
  questionIdx: index("question_idx").on(table.questionId),
}));

export type Score = typeof scores.$inferSelect;
export type InsertScore = typeof scores.$inferInsert;

/**
 * 成绩单表
 * 存储学生的考试总成绩和统计信息
 */
export const reportCards = mysqlTable("report_cards", {
  id: int("id").autoincrement().primaryKey(),
  examId: int("examId").notNull(), // 关联考试
  studentId: int("studentId").notNull(), // 关联学生
  totalScore: decimal("totalScore", { precision: 6, scale: 2 }).notNull(), // 总分
  percentage: decimal("percentage", { precision: 5, scale: 2 }), // 得分率
  classRank: int("classRank"), // 班级排名
  gradeRank: int("gradeRank"), // 年级排名
  analysis: text("analysis"), // LLM生成的分析报告
  suggestions: text("suggestions"), // LLM生成的学习建议
  weakPoints: text("weakPoints"), // 薄弱知识点（JSON格式）
  teacherComment: text("teacherComment"), // 教师评语
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => ({
  examStudentIdx: index("exam_student_idx").on(table.examId, table.studentId),
}));

export type ReportCard = typeof reportCards.$inferSelect;
export type InsertReportCard = typeof reportCards.$inferInsert;
