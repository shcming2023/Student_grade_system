import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

type AuthenticatedUser = NonNullable<TrpcContext["user"]>;

function createAuthContext(): { ctx: TrpcContext } {
  const user: AuthenticatedUser = {
    id: 1,
    openId: "test-user",
    email: "test@example.com",
    name: "Test User",
    loginMethod: "manus",
    role: "admin",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
  };

  const ctx: TrpcContext = {
    user,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: () => {},
    } as TrpcContext["res"],
  };

  return { ctx };
}

describe("reportCard", () => {
  it("should get report card data for a student", async () => {
    const { ctx } = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    // 首先创建必要的基础数据
    const grade = await caller.grades.create({
      name: "G1-RC1",
      displayName: "一年级-RC1",
      sortOrder: 101,
    });

    const subject = await caller.subjects.create({
      name: "数学-RC1",
      code: "math-rc1",
      category: "math",
    });

    const examTemplateResult = await caller.examTemplates.create({
      name: "期末考试-RC1",
      subjectId: subject.id,
      gradeId: grade.id,
      totalScore: 100,
    });
    const examTemplateId = examTemplateResult.id;

    // 创建题目
    await caller.questions.create({
      examTemplateId: examTemplateId,
      questionNumber: 1,
      module: "基础计算",
      knowledgePoint: "加法运算",
      questionType: "计算题",
      score: 10,
      sortOrder: 1,
    });

    await caller.questions.create({
      examTemplateId: examTemplateId,
      questionNumber: 2,
      module: "基础计算",
      knowledgePoint: "减法运算",
      questionType: "计算题",
      score: 10,
      sortOrder: 2,
    });

    await caller.questions.create({
      examTemplateId: examTemplateId,
      questionNumber: 3,
      module: "应用题",
      knowledgePoint: "实际问题",
      questionType: "应用题",
      score: 20,
      sortOrder: 3,
    });

    // 创建班级
    const classData = await caller.classes.create({
      gradeId: grade.id,
      name: "1班-RC1",
      fullName: "G1-1班-RC1",
    });

    // 创建学生
    const student = await caller.students.create({
      studentNumber: "20250001-RC1",
      name: "张三",
      classId: classData.id,
      status: "active",
    });

    // 创建考试
    const exam = await caller.exams.create({
      examTemplateId: examTemplateId,
      classId: classData.id,
      examDate: new Date(),
      name: "2025春季期末考试-RC1",
    });

    // 获取题目列表
    const questions = await caller.questions.byTemplate({ examTemplateId: examTemplateId });

    // 录入成绩
    await caller.scores.upsert({
      examId: exam.id,
      studentId: student.id,
      questionId: questions[0].id,
      score: 8,
    });

    await caller.scores.upsert({
      examId: exam.id,
      studentId: student.id,
      questionId: questions[1].id,
      score: 9,
    });

    await caller.scores.upsert({
      examId: exam.id,
      studentId: student.id,
      questionId: questions[2].id,
      score: 15,
    });

    // 获取成绩单
    const reportCard = await caller.reportCard.getReportCard({
      examId: exam.id,
      studentId: student.id,
    });

    // 验证成绩单数据
    expect(reportCard).toBeDefined();
    expect(reportCard.studentInfo.studentName).toBe("张三");
    expect(reportCard.examInfo.examName).toBe("2025春季期末考试-RC1");
    expect(reportCard.totalEarned).toBe(32);
    expect(reportCard.totalMax).toBe(40);
    expect(reportCard.percentage).toBe(80);

    // 验证题目得分清单
    expect(reportCard.questionScores).toHaveLength(3);
    expect(reportCard.questionScores[0].studentScore).toBe(8);
    expect(reportCard.questionScores[1].studentScore).toBe(9);
    expect(reportCard.questionScores[2].studentScore).toBe(15);

    // 验证模块分析
    expect(reportCard.moduleAnalysis).toBeDefined();
    const basicModule = reportCard.moduleAnalysis.find((m: any) => m.module === "基础计算");
    expect(basicModule).toBeDefined();
    expect(basicModule.earned).toBe(17);
    expect(basicModule.max).toBe(20);
    expect(basicModule.percentage).toBe(85);

    const appModule = reportCard.moduleAnalysis.find((m: any) => m.module === "应用题");
    expect(appModule).toBeDefined();
    expect(appModule.earned).toBe(15);
    expect(appModule.max).toBe(20);
    expect(appModule.percentage).toBe(75);

    // 验证知识点分析
    expect(reportCard.knowledgeAnalysis).toBeDefined();
    expect(reportCard.knowledgeAnalysis.length).toBeGreaterThan(0);
  });

  it("should get all report cards for an exam", async () => {
    const { ctx } = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    // 创建基础数据
    const grade = await caller.grades.create({
      name: "G2-RC2",
      displayName: "二年级-RC2",
      sortOrder: 202,
    });

    const subject = await caller.subjects.create({
      name: "英语-RC2",
      code: "english-rc2",
      category: "english",
    });

    const examTemplateResult = await caller.examTemplates.create({
      name: "月考-RC2",
      subjectId: subject.id,
      gradeId: grade.id,
      totalScore: 50,
    });
    const examTemplateId = examTemplateResult.id;

    await caller.questions.create({
      examTemplateId: examTemplateId,
      questionNumber: 1,
      module: "听力",
      knowledgePoint: "听力理解",
      questionType: "听力题",
      score: 25,
      sortOrder: 1,
    });

    await caller.questions.create({
      examTemplateId: examTemplateId,
      questionNumber: 2,
      module: "阅读",
      knowledgePoint: "阅读理解",
      questionType: "阅读题",
      score: 25,
      sortOrder: 2,
    });

    const classData = await caller.classes.create({
      gradeId: grade.id,
      name: "2班-RC2",
      fullName: "G2-2班-RC2",
    });

    // 创建两个学生
    const student1 = await caller.students.create({
      studentNumber: "20250002-RC2",
      name: "李四",
      classId: classData.id,
      status: "active",
    });

    const student2 = await caller.students.create({
      studentNumber: "20250003-RC2",
      name: "王五",
      classId: classData.id,
      status: "active",
    });

    const exam = await caller.exams.create({
      examTemplateId: examTemplateId,
      classId: classData.id,
      examDate: new Date(),
      name: "2025春季月考-RC2",
    });

    const questions = await caller.questions.byTemplate({ examTemplateId: examTemplateId });

    // 为两个学生录入成绩
    await caller.scores.upsert({
      examId: exam.id,
      studentId: student1.id,
      questionId: questions[0].id,
      score: 20,
    });

    await caller.scores.upsert({
      examId: exam.id,
      studentId: student1.id,
      questionId: questions[1].id,
      score: 22,
    });

    await caller.scores.upsert({
      examId: exam.id,
      studentId: student2.id,
      questionId: questions[0].id,
      score: 23,
    });

    await caller.scores.upsert({
      examId: exam.id,
      studentId: student2.id,
      questionId: questions[1].id,
      score: 24,
    });

    // 获取所有学生的成绩单
    const reportCards = await caller.reportCard.getExamReportCards({
      examId: exam.id,
    });

    // 验证
    expect(reportCards).toBeDefined();
    expect(reportCards.length).toBe(2);
    
    const student1Report = reportCards.find((r: any) => r.studentInfo.studentName === "李四");
    const student2Report = reportCards.find((r: any) => r.studentInfo.studentName === "王五");
    
    expect(student1Report).toBeDefined();
    expect(student1Report.totalEarned).toBe(42);
    
    expect(student2Report).toBeDefined();
    expect(student2Report.totalEarned).toBe(47);
  });
});
