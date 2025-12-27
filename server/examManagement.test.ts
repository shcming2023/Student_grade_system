import { describe, it, expect, beforeAll } from 'vitest';
import { appRouter } from './routers';
import * as teacherAuth from './teacherAuth';

describe('Exam Management', () => {
  let adminToken: string;
  let teacherId: number;

  beforeAll(async () => {
    // 使用管理员账户登录
    const loginResult = await teacherAuth.loginTeacher('admin', 'admin123');
    if (!loginResult) {
      throw new Error('Failed to login as admin');
    }
    adminToken = loginResult.token;
    teacherId = loginResult.teacher.id;
  });

  describe('Exam Sessions', () => {
    it('should create an exam session', async () => {
      const caller = appRouter.createCaller({
        req: {} as any,
        res: {} as any,
        user: { id: teacherId } as any,
      });

      const timestamp = Date.now();
      const result = await caller.examSessions.create({
        name: `2025-2026学年测试考试 S1 ${timestamp}`,
        schoolYear: '2025-2026',
        semester: 'S1',
        startDate: '2025-09-01',
        endDate: '2025-09-30',
        description: '测试考试描述',
        status: 'draft',
      });

      expect(result.success).toBe(true);
    });

    it('should list all exam sessions', async () => {
      const caller = appRouter.createCaller({
        req: {} as any,
        res: {} as any,
        user: { id: teacherId } as any,
      });

      const sessions = await caller.examSessions.list();
      expect(Array.isArray(sessions)).toBe(true);
      expect(sessions.length).toBeGreaterThan(0);
    });
  });

  describe('Exam Templates', () => {
    let examSessionId: number;
    let subjectId: number;
    let gradeId: number;

    beforeAll(async () => {
      const caller = appRouter.createCaller({
        req: {} as any,
        res: {} as any,
        user: { id: teacherId } as any,
      });

      // 获取第一个考试
      const sessions = await caller.examSessions.list();
      if (sessions.length > 0) {
        examSessionId = sessions[0].id;
      }

      // 获取第一个科目
      const subjects = await caller.subjects.list();
      if (subjects.length > 0) {
        subjectId = subjects[0].id;
      }

      // 获取第一个年级
      const grades = await caller.grades.list();
      if (grades.length > 0) {
        gradeId = grades[0].id;
      }
    });

    it('should create an exam template with teacher assignment', async () => {
      if (!examSessionId || !subjectId || !gradeId) {
        console.log('Skipping test: missing required data');
        return;
      }

      const caller = appRouter.createCaller({
        req: {} as any,
        res: {} as any,
        user: { id: teacherId } as any,
      });

      const result = await caller.examTemplates.create({
        examSessionId,
        name: '测试试卷',
        subjectId,
        gradeId,
        totalScore: 100,
        description: '测试试卷描述',
        creatorId: teacherId,
        graderId: teacherId,
      });

      expect(result.success).toBe(true);
      expect(result.id).toBeDefined();
    });

    it('should list exam templates by exam session', async () => {
      if (!examSessionId) {
        console.log('Skipping test: missing exam session');
        return;
      }

      const caller = appRouter.createCaller({
        req: {} as any,
        res: {} as any,
        user: { id: teacherId } as any,
      });

      const templates = await caller.examTemplates.byExamSession({ examSessionId });
      expect(Array.isArray(templates)).toBe(true);
    });
  });
});
