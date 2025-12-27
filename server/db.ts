import { eq, and, desc, asc, sql, inArray } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { 
  InsertUser, users, 
  teachers, InsertTeacher,
  grades, InsertGrade,
  classes, InsertClass,
  subjects, InsertSubject,
  students, InsertStudent,
  examTemplates, InsertExamTemplate,
  questions, InsertQuestion,
  exams, InsertExam,
  scores, InsertScore,
  reportCards, InsertReportCard,
  examSessions, InsertExamSession,
  examStudents, InsertExamStudent
} from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

// ============= User Management =============

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

export async function getAllUsers() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(users).orderBy(desc(users.createdAt));
}

// ============= Grade Management =============

export async function createGrade(grade: InsertGrade) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(grades).values(grade);
  return result;
}

export async function getAllGrades() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(grades).orderBy(asc(grades.sortOrder));
}

export async function getGradeById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(grades).where(eq(grades.id, id)).limit(1);
  return result[0];
}

export async function updateGrade(id: number, data: Partial<InsertGrade>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.update(grades).set(data).where(eq(grades.id, id));
}

export async function deleteGrade(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(grades).where(eq(grades.id, id));
}

// ============= Class Management =============

export async function createClass(classData: InsertClass) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(classes).values(classData);
  return result;
}

export async function getAllClasses() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(classes).orderBy(asc(classes.gradeId), asc(classes.name));
}

export async function getClassById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(classes).where(eq(classes.id, id)).limit(1);
  return result[0];
}

export async function getClassesByGrade(gradeId: number) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(classes).where(eq(classes.gradeId, gradeId)).orderBy(asc(classes.name));
}

export async function updateClass(id: number, data: Partial<InsertClass>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.update(classes).set(data).where(eq(classes.id, id));
}

export async function deleteClass(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(classes).where(eq(classes.id, id));
}

// ============= Subject Management =============

export async function createSubject(subject: InsertSubject) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(subjects).values(subject);
  return result;
}

export async function getAllSubjects() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(subjects).orderBy(asc(subjects.category), asc(subjects.name));
}

export async function getSubjectById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(subjects).where(eq(subjects.id, id)).limit(1);
  return result[0];
}

export async function updateSubject(id: number, data: Partial<InsertSubject>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.update(subjects).set(data).where(eq(subjects.id, id));
}

export async function deleteSubject(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(subjects).where(eq(subjects.id, id));
}

// ============= Student Management =============

export async function createStudent(student: InsertStudent) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(students).values(student);
  return result;
}

export async function getAllStudents() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(students).orderBy(asc(students.classId), asc(students.name));
}

export async function getStudentById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(students).where(eq(students.id, id)).limit(1);
  return result[0];
}

export async function getStudentsByClass(classId: number) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(students).where(eq(students.classId, classId)).orderBy(asc(students.name));
}

export async function updateStudent(id: number, data: Partial<InsertStudent>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.update(students).set(data).where(eq(students.id, id));
}

export async function deleteStudent(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(students).where(eq(students.id, id));
}

// ============= Exam Template Management =============

export async function createExamTemplate(template: InsertExamTemplate) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(examTemplates).values(template);
  return result;
}

export async function getAllExamTemplates() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(examTemplates).orderBy(desc(examTemplates.createdAt));
}

export async function getExamTemplateById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(examTemplates).where(eq(examTemplates.id, id)).limit(1);
  return result[0];
}

export async function getExamTemplatesBySubjectAndGrade(subjectId: number, gradeId: number) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(examTemplates)
    .where(and(eq(examTemplates.subjectId, subjectId), eq(examTemplates.gradeId, gradeId)))
    .orderBy(desc(examTemplates.createdAt));
}

export async function updateExamTemplate(id: number, data: Partial<InsertExamTemplate>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.update(examTemplates).set(data).where(eq(examTemplates.id, id));
}

export async function deleteExamTemplate(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(examTemplates).where(eq(examTemplates.id, id));
}

// ============= Question Management =============

export async function createQuestion(question: InsertQuestion) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(questions).values(question);
  return result;
}

export async function createQuestions(questionList: InsertQuestion[]) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(questions).values(questionList);
  return result;
}

export async function getQuestionsByExamTemplate(examTemplateId: number) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(questions)
    .where(eq(questions.examTemplateId, examTemplateId))
    .orderBy(asc(questions.sortOrder));
}

export async function updateQuestion(id: number, data: Partial<InsertQuestion>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.update(questions).set(data).where(eq(questions.id, id));
}

export async function deleteQuestion(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(questions).where(eq(questions.id, id));
}

export async function deleteQuestionsByExamTemplate(examTemplateId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(questions).where(eq(questions.examTemplateId, examTemplateId));
}

// ============= Exam Management =============

export async function createExam(exam: InsertExam) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(exams).values(exam);
  return result;
}

export async function getAllExams() {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(exams).orderBy(desc(exams.examDate));
}

export async function getExamById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(exams).where(eq(exams.id, id)).limit(1);
  return result[0];
}

export async function getExamsByClass(classId: number) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(exams).where(eq(exams.classId, classId)).orderBy(desc(exams.examDate));
}

export async function updateExam(id: number, data: Partial<InsertExam>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.update(exams).set(data).where(eq(exams.id, id));
}

export async function deleteExam(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(exams).where(eq(exams.id, id));
}

// ============= Score Management =============

export async function createScore(score: InsertScore) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(scores).values(score);
  return result;
}

export async function createScores(scoreList: InsertScore[]) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  if (scoreList.length === 0) return;
  const result = await db.insert(scores).values(scoreList);
  return result;
}

export async function getScoresByExam(examId: number) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(scores).where(eq(scores.examId, examId));
}

export async function getScoresWithDetailsByExam(examId: number) {
  const db = await getDb();
  if (!db) return { students: [], questions: [], scores: [] };
  
  // 获取考试信息
  const exam = await db.select().from(exams).where(eq(exams.id, examId)).limit(1);
  if (exam.length === 0) return { students: [], questions: [], scores: [] };
  
  const examData = exam[0];
  
  // 获取该班级的所有学生
  const studentList = await db.select().from(students)
    .where(eq(students.classId, examData.classId))
    .orderBy(asc(students.studentNumber));
  
  // 获取试卷模板的所有题目
  const questionList = await db.select().from(questions)
    .where(eq(questions.examTemplateId, examData.examTemplateId))
    .orderBy(asc(questions.sortOrder));
  
  // 获取所有成绩
  const scoreList = await db.select().from(scores)
    .where(eq(scores.examId, examId));
  
  return {
    students: studentList,
    questions: questionList,
    scores: scoreList,
  };
}

export async function getScoresByStudent(examId: number, studentId: number) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(scores)
    .where(and(eq(scores.examId, examId), eq(scores.studentId, studentId)))
    .orderBy(asc(scores.questionId));
}

export async function updateScore(id: number, data: Partial<InsertScore>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.update(scores).set(data).where(eq(scores.id, id));
}

export async function upsertScore(score: InsertScore) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  // 查找是否已存在
  const existing = await db.select().from(scores)
    .where(and(
      eq(scores.examId, score.examId),
      eq(scores.studentId, score.studentId),
      eq(scores.questionId, score.questionId)
    ))
    .limit(1);
  
  if (existing.length > 0) {
    // 更新
    return await db.update(scores)
      .set({ score: score.score, updatedAt: new Date() })
      .where(eq(scores.id, existing[0].id));
  } else {
    // 创建
    return await db.insert(scores).values(score);
  }
}

export async function deleteScore(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(scores).where(eq(scores.id, id));
}

export async function deleteScoresByExam(examId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(scores).where(eq(scores.examId, examId));
}

// ============= Report Card Management =============

export async function createReportCard(reportCard: InsertReportCard) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.insert(reportCards).values(reportCard);
  return result;
}

export async function getReportCardsByExam(examId: number) {
  const db = await getDb();
  if (!db) return [];
  return await db.select().from(reportCards)
    .where(eq(reportCards.examId, examId))
    .orderBy(desc(reportCards.totalScore));
}

export async function getReportCard(examId: number, studentId: number) {
  const db = await getDb();
  if (!db) return undefined;
  const result = await db.select().from(reportCards)
    .where(and(eq(reportCards.examId, examId), eq(reportCards.studentId, studentId)))
    .limit(1);
  return result[0];
}

export async function updateReportCard(id: number, data: Partial<InsertReportCard>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.update(reportCards).set(data).where(eq(reportCards.id, id));
}

export async function deleteReportCard(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return await db.delete(reportCards).where(eq(reportCards.id, id));
}

// ============= Statistics and Analytics =============

/**
 * 计算考试的统计信息
 */
export async function calculateExamStatistics(examId: number) {
  const db = await getDb();
  if (!db) return null;

  // 获取所有成绩记录
  const allScores = await getScoresByExam(examId);
  
  // 按学生分组计算总分
  const studentScores = new Map<number, number>();
  allScores.forEach(score => {
    const current = studentScores.get(score.studentId) || 0;
    studentScores.set(score.studentId, current + parseFloat(score.score as any));
  });

  // 计算统计数据
  const scores = Array.from(studentScores.values());
  const totalStudents = scores.length;
  const totalScore = scores.reduce((sum, s) => sum + s, 0);
  const averageScore = totalStudents > 0 ? totalScore / totalStudents : 0;
  const maxScore = totalStudents > 0 ? Math.max(...scores) : 0;
  const minScore = totalStudents > 0 ? Math.min(...scores) : 0;

  return {
    totalStudents,
    averageScore,
    maxScore,
    minScore,
    studentScores: Array.from(studentScores.entries()).map(([studentId, score]) => ({
      studentId,
      totalScore: score
    }))
  };
}

/**
 * 生成或更新成绩单
 */
export async function generateReportCards(examId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const stats = await calculateExamStatistics(examId);
  if (!stats) return;

  // 获取考试信息
  const exam = await getExamById(examId);
  if (!exam) throw new Error("Exam not found");

  const template = await getExamTemplateById(exam.examTemplateId);
  if (!template) throw new Error("Exam template not found");

  // 按总分排序，计算排名
  const sortedScores = stats.studentScores.sort((a, b) => b.totalScore - a.totalScore);

  // 为每个学生创建或更新成绩单
  for (let i = 0; i < sortedScores.length; i++) {
    const { studentId, totalScore } = sortedScores[i]!;
    const rank = i + 1;
    const percentage = (totalScore / parseFloat(template.totalScore as any)) * 100;

    // 检查是否已存在成绩单
    const existing = await getReportCard(examId, studentId);

    if (existing) {
      // 更新现有成绩单
      await updateReportCard(existing.id, {
        totalScore: totalScore.toString() as any,
        percentage: percentage.toFixed(2) as any,
        classRank: rank,
      });
    } else {
      // 创建新成绩单
      await createReportCard({
        examId,
        studentId,
        totalScore: totalScore.toString() as any,
        percentage: percentage.toFixed(2) as any,
        classRank: rank,
        gradeRank: null,
      });
    }
  }

  return sortedScores.length;
}

// ============= Report Card Functions =============

/**
 * 获取学生某次考试的完整成绩单数据
 * 包含：基本信息、每题得分、按模块统计、按知识点统计
 */
export async function getReportCardData(examId: number, studentId: number) {
  const db = await getDb();
  if (!db) return null;

  // 1. 获取考试基本信息
  const examResult = await db
    .select({
      examId: exams.id,
      examName: exams.name,
      examDate: exams.examDate,
      templateId: exams.examTemplateId,
      templateName: examTemplates.name,
      subjectId: examTemplates.subjectId,
      subjectName: subjects.name,
      gradeId: examTemplates.gradeId,
      gradeName: grades.displayName,
      totalScore: examTemplates.totalScore,
    })
    .from(exams)
    .innerJoin(examTemplates, eq(exams.examTemplateId, examTemplates.id))
    .innerJoin(subjects, eq(examTemplates.subjectId, subjects.id))
    .innerJoin(grades, eq(examTemplates.gradeId, grades.id))
    .where(eq(exams.id, examId))
    .limit(1);

  if (examResult.length === 0) return null;
  const examInfo = examResult[0];

  // 2. 获取学生基本信息
  const studentResult = await db
    .select({
      studentId: students.id,
      studentNumber: students.studentNumber,
      studentName: students.name,
      classId: students.classId,
      className: classes.name,
    })
    .from(students)
    .innerJoin(classes, eq(students.classId, classes.id))
    .where(eq(students.id, studentId))
    .limit(1);

  if (studentResult.length === 0) return null;
  const studentInfo = studentResult[0];

  // 3. 获取所有题目和学生的得分
  const questionScores = await db
    .select({
      questionId: questions.id,
      questionNumber: questions.questionNumber,
      module: questions.module,
      knowledgePoint: questions.knowledgePoint,
      questionType: questions.questionType,
      maxScore: questions.score,
      studentScore: scores.score,
      sortOrder: questions.sortOrder,
    })
    .from(questions)
    .leftJoin(
      scores,
      and(
        eq(scores.questionId, questions.id),
        eq(scores.examId, examId),
        eq(scores.studentId, studentId)
      )
    )
    .where(eq(questions.examTemplateId, examInfo.templateId))
    .orderBy(questions.sortOrder);

  // 4. 计算总分
  const totalEarned = questionScores.reduce(
    (sum, q) => sum + (parseFloat(q.studentScore?.toString() || '0')),
    0
  );

  // 5. 按模块统计
  const moduleStats: Record<string, { earned: number; max: number; count: number }> = {};
  questionScores.forEach(q => {
    const module = q.module || '未分类';
    if (!moduleStats[module]) {
      moduleStats[module] = { earned: 0, max: 0, count: 0 };
    }
    moduleStats[module].earned += parseFloat(q.studentScore?.toString() || '0');
    moduleStats[module].max += parseFloat(q.maxScore.toString());
    moduleStats[module].count += 1;
  });

  const moduleAnalysis = Object.entries(moduleStats).map(([module, stats]) => ({
    module,
    earned: stats.earned,
    max: stats.max,
    count: stats.count,
    percentage: stats.max > 0 ? (stats.earned / stats.max) * 100 : 0,
  }));

  // 6. 按知识点统计
  const knowledgeStats: Record<string, { earned: number; max: number; count: number }> = {};
  questionScores.forEach(q => {
    const kp = q.knowledgePoint || '未分类';
    if (!knowledgeStats[kp]) {
      knowledgeStats[kp] = { earned: 0, max: 0, count: 0 };
    }
    knowledgeStats[kp].earned += parseFloat(q.studentScore?.toString() || '0');
    knowledgeStats[kp].max += parseFloat(q.maxScore.toString());
    knowledgeStats[kp].count += 1;
  });

  const knowledgeAnalysis = Object.entries(knowledgeStats).map(([knowledgePoint, stats]) => ({
    knowledgePoint,
    earned: stats.earned,
    max: stats.max,
    count: stats.count,
    percentage: stats.max > 0 ? (stats.earned / stats.max) * 100 : 0,
  }));

  return {
    // 基本信息
    examInfo,
    studentInfo,
    // 成绩得分清单
    questionScores: questionScores.map(q => ({
      questionNumber: q.questionNumber,
      module: q.module,
      knowledgePoint: q.knowledgePoint,
      questionType: q.questionType,
      maxScore: parseFloat(q.maxScore.toString()),
      studentScore: parseFloat(q.studentScore?.toString() || '0'),
    })),
    // 总分
    totalEarned: parseFloat(totalEarned.toFixed(2)),
    totalMax: parseFloat(examInfo.totalScore!.toString()),
    percentage: parseFloat(((totalEarned / parseFloat(examInfo.totalScore!.toString())) * 100).toFixed(2)),
    // 成绩分析
    moduleAnalysis: moduleAnalysis.map(m => ({
      ...m,
      earned: parseFloat(m.earned.toFixed(2)),
      max: parseFloat(m.max.toFixed(2)),
      percentage: parseFloat(m.percentage.toFixed(2)),
    })),
    knowledgeAnalysis: knowledgeAnalysis.map(k => ({
      ...k,
      earned: parseFloat(k.earned.toFixed(2)),
      max: parseFloat(k.max.toFixed(2)),
      percentage: parseFloat(k.percentage.toFixed(2)),
    })),
  };
}

/**
 * 获取某次考试的所有学生成绩单列表（用于批量生成）
 */
export async function getExamReportCards(examId: number) {
  const db = await getDb();
  if (!db) return [];

  // 获取该考试的所有学生
  const studentsInExam = await db
    .select({
      studentId: scores.studentId,
    })
    .from(scores)
    .where(eq(scores.examId, examId))
    .groupBy(scores.studentId);

  // 为每个学生生成成绩单数据
  const reportCards = await Promise.all(
    studentsInExam.map(s => getReportCardData(examId, s.studentId))
  );

  return reportCards.filter(rc => rc !== null);
}

// ============= Teacher Management =============

/**
 * 创建教师账户
 */
export async function createTeacher(teacher: InsertTeacher) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.insert(teachers).values(teacher);
}

/**
 * 根据用户名查找教师
 */
export async function getTeacherByUsername(username: string) {
  const db = await getDb();
  if (!db) return undefined;
  
  const result = await db.select().from(teachers).where(eq(teachers.username, username)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

/**
 * 根据ID查找教师
 */
export async function getTeacherById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  
  const result = await db.select().from(teachers).where(eq(teachers.id, id)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

/**
 * 获取所有教师列表
 */
export async function getAllTeachers() {
  const db = await getDb();
  if (!db) return [];
  
  return await db.select().from(teachers).orderBy(asc(teachers.name));
}

/**
 * 更新教师信息
 */
export async function updateTeacher(id: number, data: Partial<InsertTeacher>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.update(teachers).set(data).where(eq(teachers.id, id));
}

/**
 * 删除教师
 */
export async function deleteTeacher(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.delete(teachers).where(eq(teachers.id, id));
}

/**
 * 更新教师最后登录时间
 */
export async function updateTeacherLastLogin(id: number) {
  const db = await getDb();
  if (!db) return;
  
  await db.update(teachers).set({ lastLoginAt: new Date() }).where(eq(teachers.id, id));
}

// ============= Exam Session Management =============

/**
 * 创建考试管理
 */
export async function createExamSession(session: InsertExamSession) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.insert(examSessions).values(session);
}

/**
 * 获取所有考试管理列表
 */
export async function getAllExamSessions() {
  const db = await getDb();
  if (!db) return [];
  
  return await db.select().from(examSessions).orderBy(desc(examSessions.createdAt));
}

/**
 * 根据ID获取考试管理
 */
export async function getExamSessionById(id: number) {
  const db = await getDb();
  if (!db) return undefined;
  
  const result = await db.select().from(examSessions).where(eq(examSessions.id, id)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

/**
 * 更新考试管理
 */
export async function updateExamSession(id: number, data: Partial<InsertExamSession>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.update(examSessions).set(data).where(eq(examSessions.id, id));
}

/**
 * 删除考试管理
 */
export async function deleteExamSession(id: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.delete(examSessions).where(eq(examSessions.id, id));
}

// ============= Exam Student Management =============

/**
 * 添加试卷-学生关联
 */
export async function addExamStudent(examId: number, studentId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.insert(examStudents).values({ examId, studentId });
}

/**
 * 批量添加试卷-学生关联
 */
export async function addExamStudents(examId: number, studentIds: number[]) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  const values = studentIds.map(studentId => ({ examId, studentId }));
  return await db.insert(examStudents).values(values);
}

/**
 * 获取试卷的所有学生
 */
export async function getExamStudents(examId: number) {
  const db = await getDb();
  if (!db) return [];
  
  return await db
    .select({
      id: examStudents.id,
      studentId: examStudents.studentId,
      studentNumber: students.studentNumber,
      studentName: students.name,
      classId: students.classId,
    })
    .from(examStudents)
    .innerJoin(students, eq(examStudents.studentId, students.id))
    .where(eq(examStudents.examId, examId));
}

/**
 * 删除试卷-学生关联
 */
export async function removeExamStudent(examId: number, studentId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  
  return await db.delete(examStudents).where(
    and(
      eq(examStudents.examId, examId),
      eq(examStudents.studentId, studentId)
    )
  );
}
