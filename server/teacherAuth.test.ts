import { describe, expect, it, beforeAll } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";
import { initializeAdmin } from "./teacherAuth";

// 创建测试用的context
function createTestContext(): TrpcContext {
  return {
    user: null,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: () => {},
    } as TrpcContext["res"],
  };
}

describe("Teacher Authentication", () => {
  beforeAll(async () => {
    // 确保管理员账户已初始化
    await initializeAdmin();
  });

  it("should login with correct admin credentials", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.teacherAuth.login({
      username: "admin",
      password: "admin123",
    });

    expect(result.success).toBe(true);
    expect(result.token).toBeDefined();
    expect(result.teacher).toBeDefined();
    expect(result.teacher?.username).toBe("admin");
    expect(result.teacher?.role).toBe("admin");
  });

  it("should fail login with incorrect password", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.teacherAuth.login({
        username: "admin",
        password: "wrongpassword",
      })
    ).rejects.toThrow();
  });

  it("should fail login with non-existent username", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.teacherAuth.login({
        username: "nonexistent",
        password: "password",
      })
    ).rejects.toThrow();
  });

  it("should create a new teacher (admin only)", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    // 先登录获取管理员token
    const loginResult = await caller.teacherAuth.login({
      username: "admin",
      password: "admin123",
    });

    // 创建新教师
    const newTeacher = await caller.teachers.create({
      username: `teacher_${Date.now()}`,
      password: "teacher123",
      name: "测试教师",
      email: "test@example.com",
      role: "teacher",
    });

    expect(newTeacher).toBeDefined();
    expect(newTeacher.username).toContain("teacher_");
    expect(newTeacher.role).toBe("teacher");
  });

  it("should list all teachers", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const teachers = await caller.teachers.list();

    expect(Array.isArray(teachers)).toBe(true);
    expect(teachers.length).toBeGreaterThan(0);
    // 应该至少有管理员账户
    const admin = teachers.find(t => t.username === "admin");
    expect(admin).toBeDefined();
    expect(admin?.role).toBe("admin");
  });
});
