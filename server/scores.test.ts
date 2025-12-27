import { describe, expect, it, beforeAll } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";
import * as db from "./db";

type AuthenticatedUser = NonNullable<TrpcContext["user"]>;

function createAuthContext(): TrpcContext {
  const user: AuthenticatedUser = {
    id: 1,
    openId: "test-user",
    email: "test@example.com",
    name: "Test Teacher",
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

  return ctx;
}

describe.sequential("Scores API", () => {
  let testClassId: number;
  let testTemplateId: number;
  let testStudentId: number;
  let testExamId: number | undefined;
  let testQuestionId: number;

  beforeAll(async () => {
    // 获取测试数据
    const classes = await db.getAllClasses();
    if (classes.length === 0) {
      throw new Error("需要至少一个班级进行测试");
    }
    testClassId = classes[0]!.id;

    const templates = await db.getAllExamTemplates();
    if (templates.length === 0) {
      throw new Error("需要至少一个试卷模板进行测试");
    }
    testTemplateId = templates[0]!.id;

    const students = await db.getStudentsByClass(testClassId);
    if (students.length === 0) {
      // 创建测试学生
      const timestamp = Date.now();
      await db.createStudent({
        studentNumber: `TEST${timestamp}`,
        name: "测试学生",
        classId: testClassId,
        gender: "male",
        status: "active",
      });
      const newStudents = await db.getStudentsByClass(testClassId);
      testStudentId = newStudents[0]!.id;
    } else {
      testStudentId = students[0]!.id;
    }

    const questions = await db.getQuestionsByExamTemplate(testTemplateId);
    if (questions.length === 0) {
      throw new Error("需要至少一个题目进行测试");
    }
    testQuestionId = questions[0]!.id;
  });

  it("should create an exam", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.exams.create({
      examTemplateId: testTemplateId,
      classId: testClassId,
      examDate: new Date(),
      name: "测试考试",
      status: "draft",
    });

    expect(result.success).toBe(true);
    expect(result.id).toBeDefined();
    testExamId = result.id!;
  });

  it("should upsert a score (create)", async () => {
    if (!testExamId) throw new Error("testExamId is not set");
    
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.scores.upsert({
      examId: testExamId,
      studentId: testStudentId,
      questionId: testQuestionId,
      score: 8.5,
    });

    expect(result.success).toBe(true);
  });

  it("should upsert a score (update)", async () => {
    if (!testExamId) throw new Error("testExamId is not set");
    
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.scores.upsert({
      examId: testExamId,
      studentId: testStudentId,
      questionId: testQuestionId,
      score: 9.0,
    });

    expect(result.success).toBe(true);
  });

  it("should get scores with details by exam", async () => {
    if (!testExamId) throw new Error("testExamId is not set");
    
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.scores.byExamWithDetails({ examId: testExamId });

    expect(result).toBeDefined();
    expect(Array.isArray(result.students)).toBe(true);
    expect(Array.isArray(result.questions)).toBe(true);
    expect(Array.isArray(result.scores)).toBe(true);
    expect(result.students.length).toBeGreaterThan(0);
    expect(result.questions.length).toBeGreaterThan(0);
    expect(result.scores.length).toBeGreaterThan(0);
  });

  it("should get scores by student", async () => {
    if (!testExamId) throw new Error("testExamId is not set");
    
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const scores = await caller.scores.byStudent({
      examId: testExamId,
      studentId: testStudentId,
    });

    expect(Array.isArray(scores)).toBe(true);
    expect(scores.length).toBeGreaterThan(0);
  });
});
