import { describe, it, expect } from "vitest";
import { appRouter } from "./routers";
import * as db from "./db";
import type { TrpcContext } from "./_core/context";
import bcrypt from "bcryptjs";

function createTestContext(): TrpcContext {
  return {
    user: null,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: () => {},
      cookie: () => {},
    } as TrpcContext["res"],
  };
}

describe("Teachers Management", () => {
  it("should have admin account initialized", async () => {
    const teachers = await db.getAllTeachers();
    const admin = teachers.find((t) => t.username === "admin");

    expect(admin).toBeDefined();
    expect(admin?.role).toBe("admin");
    expect(admin?.status).toBe("active");

    // 验证管理员密码
    const passwordMatch = await bcrypt.compare(
      "admin123",
      admin!.password
    );
    expect(passwordMatch).toBe(true);
  });

  it("should authenticate admin with correct credentials", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    const loginResult = await caller.teacherAuth.login({
      username: "admin",
      password: "admin123",
    });

    expect(loginResult.token).toBeDefined();
    expect(loginResult.teacher).toBeDefined();
    expect(loginResult.teacher?.username).toBe("admin");
    expect(loginResult.teacher?.role).toBe("admin");
    expect(loginResult.teacher).not.toHaveProperty("password");
  });

  it("should reject login with incorrect password", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.teacherAuth.login({
        username: "admin",
        password: "wrongpassword",
      })
    ).rejects.toThrow();
  });

  it("should reject login with non-existent username", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.teacherAuth.login({
        username: "nonexistent_user_12345",
        password: "anypassword",
      })
    ).rejects.toThrow();
  });

  it("should reject login for inactive account", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);
    
    // 创建一个停用的账户
    const timestamp = Date.now();
    const hashedPassword = await bcrypt.hash("test123", 10);
    await db.createTeacher({
      username: `inactive_${timestamp}`,
      password: hashedPassword,
      name: "停用账户",
      role: "teacher",
      status: "inactive",
    });

    // 尝试登录停用的账户
    await expect(
      caller.teacherAuth.login({
        username: `inactive_${timestamp}`,
        password: "test123",
      })
    ).rejects.toThrow("账户已被禁用");
  });
});
