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

describe("Exam Templates API", () => {
  let testSubjectId: number;
  let testGradeId: number;
  let testTemplateId: number;

  beforeAll(async () => {
    // 确保测试数据存在
    const subjects = await db.getAllSubjects();
    if (subjects.length === 0) {
      await db.createSubject({
        name: "测试科目",
        code: "test_subject",
        category: "other",
        description: null,
      });
    }
    const allSubjects = await db.getAllSubjects();
    testSubjectId = allSubjects[0]!.id;

    const grades = await db.getAllGrades();
    if (grades.length === 0) {
      await db.createGrade({ name: "G1", displayName: "一年级", sortOrder: 1 });
    }
    const allGrades = await db.getAllGrades();
    testGradeId = allGrades[0]!.id;
  });

  it("should create a new exam template", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.examTemplates.create({
      name: "测试试卷模板",
      subjectId: testSubjectId,
      gradeId: testGradeId,
      totalScore: 100,
      description: "这是一个测试模板",
    });

    expect(result.success).toBe(true);
    expect(result.id).toBeDefined();
    testTemplateId = result.id!;
  });

  it("should list all exam templates", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const templates = await caller.examTemplates.list();
    expect(Array.isArray(templates)).toBe(true);
    expect(templates.length).toBeGreaterThan(0);
  });

  it("should get exam templates by subject and grade", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const templates = await caller.examTemplates.bySubjectAndGrade({
      subjectId: testSubjectId,
      gradeId: testGradeId,
    });

    expect(Array.isArray(templates)).toBe(true);
  });
});

describe("Questions API", () => {
  let testTemplateId: number;

  beforeAll(async () => {
    const templates = await db.getAllExamTemplates();
    if (templates.length > 0) {
      testTemplateId = templates[0]!.id;
    }
  });

  it("should create questions for a template", async () => {
    if (!testTemplateId) {
      console.log("Skipping test: no template available");
      return;
    }

    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.questions.create({
      examTemplateId: testTemplateId,
      questionNumber: 1,
      module: "模块A",
      knowledgePoint: "知识点1",
      questionType: "选择题",
      score: 5,
      sortOrder: 1,
    });

    expect(result.success).toBe(true);
  });

  it("should get questions by exam template", async () => {
    if (!testTemplateId) {
      console.log("Skipping test: no template available");
      return;
    }

    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const questions = await caller.questions.byExamTemplate({
      examTemplateId: testTemplateId,
    });

    expect(Array.isArray(questions)).toBe(true);
  });

  it("should create batch questions", async () => {
    if (!testTemplateId) {
      console.log("Skipping test: no template available");
      return;
    }

    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.questions.createBatch({
      questions: [
        {
          examTemplateId: testTemplateId,
          questionNumber: 2,
          module: "模块B",
          knowledgePoint: "知识点2",
          questionType: "填空题",
          score: 10,
          sortOrder: 2,
        },
        {
          examTemplateId: testTemplateId,
          questionNumber: 3,
          module: "模块C",
          knowledgePoint: "知识点3",
          questionType: "简答题",
          score: 15,
          sortOrder: 3,
        },
      ],
    });

    expect(result.success).toBe(true);
  });
});

describe("Classes and Subjects API", () => {
  it("should list all classes", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const classes = await caller.classes.list();
    expect(Array.isArray(classes)).toBe(true);
  });

  it("should list all subjects", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const subjects = await caller.subjects.list();
    expect(Array.isArray(subjects)).toBe(true);
    expect(subjects.length).toBeGreaterThan(0);
  });
});
