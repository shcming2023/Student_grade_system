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

describe("Students API", () => {
  let testGradeId: number;
  let testClassId: number;

  beforeAll(async () => {
    // 确保测试数据存在
    const grades = await db.getAllGrades();
    if (grades.length === 0) {
      await db.createGrade({ name: "G1", displayName: "一年级", sortOrder: 1 });
    }
    const allGrades = await db.getAllGrades();
    testGradeId = allGrades[0]!.id;

    // 创建测试班级
    const classes = await db.getAllClasses();
    if (classes.length === 0) {
      await db.createClass({
        gradeId: testGradeId,
        name: "1班",
        fullName: "G1-1班",
        teacherId: null,
      });
    }
    const allClasses = await db.getAllClasses();
    testClassId = allClasses[0]!.id;
  });

  it("should list all students", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const students = await caller.students.list();
    expect(Array.isArray(students)).toBe(true);
  });

  it("should create a new student", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const timestamp = Date.now();
    const result = await caller.students.create({
      studentNumber: `TEST${timestamp}`,
      name: "测试学生",
      classId: testClassId,
      gender: "male",
      parentContact: "13800138000",
      status: "active",
    });

    expect(result.success).toBe(true);
  });

  it("should get students by class", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const students = await caller.students.byClass({ classId: testClassId });
    expect(Array.isArray(students)).toBe(true);
  });
});

describe("Grades API", () => {
  it("should list all grades", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const grades = await caller.grades.list();
    expect(Array.isArray(grades)).toBe(true);
    expect(grades.length).toBeGreaterThan(0);
  });
});

describe("Subjects API", () => {
  it("should list all subjects", async () => {
    const ctx = createAuthContext();
    const caller = appRouter.createCaller(ctx);

    const subjects = await caller.subjects.list();
    expect(Array.isArray(subjects)).toBe(true);
  });
});
