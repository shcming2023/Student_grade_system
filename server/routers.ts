import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import { z } from "zod";
import * as db from "./db";
import { TRPCError } from "@trpc/server";
import * as teacherAuth from "./teacherAuth";
import { examTemplates } from "../drizzle/schema";
import { eq } from "drizzle-orm";

// ============= Validation Schemas =============

const gradeSchema = z.object({
  name: z.string().min(1).max(50),
  displayName: z.string().min(1).max(100),
  sortOrder: z.number().int(),
});

const classSchema = z.object({
  gradeId: z.number().int(),
  name: z.string().min(1).max(100),
  fullName: z.string().min(1).max(200),
  teacherId: z.number().int().optional().nullable(),
});

const subjectSchema = z.object({
  name: z.string().min(1).max(100),
  code: z.string().min(1).max(50),
  category: z.string().min(1).max(50),
  description: z.string().optional().nullable(),
});

const studentSchema = z.object({
  studentNumber: z.string().min(1).max(50),
  name: z.string().min(1).max(100),
  classId: z.number().int(),
  gender: z.enum(["male", "female"]).optional().nullable(),
  dateOfBirth: z.date().optional().nullable(),
  parentContact: z.string().max(100).optional().nullable(),
  status: z.enum(["active", "inactive"]).default("active"),
});

const examTemplateSchema = z.object({
  examSessionId: z.number().int(),
  name: z.string().min(1).max(200),
  subjectId: z.number().int(),
  gradeId: z.number().int(),
  totalScore: z.number(),
  description: z.string().optional().nullable(),
  creatorId: z.number().int().optional().nullable(),
  graderId: z.number().int().optional().nullable(),
});

const questionSchema = z.object({
  examTemplateId: z.number().int(),
  questionNumber: z.number().int(),
  module: z.string().max(100).optional().nullable(),
  knowledgePoint: z.string().optional().nullable(),
  questionType: z.string().max(100).optional().nullable(),
  score: z.number(),
  sortOrder: z.number().int(),
});

const examSchema = z.object({
  examSessionId: z.number().int().optional(), // 关联考试管理（可选，渐进式迁移）
  examTemplateId: z.number().int(),
  classId: z.number().int(),
  examDate: z.date(),
  name: z.string().min(1).max(200),
  creatorTeacherId: z.number().int().optional(), // 出卷老师ID（可选，渐进式迁移）
  graderTeacherId: z.number().int().optional(), // 阅卷老师ID
  status: z.enum(["draft", "published", "completed"]).default("draft"),
});

const scoreSchema = z.object({
  examId: z.number().int(),
  studentId: z.number().int(),
  questionId: z.number().int(),
  score: z.number(),
});

// ============= Router Definition =============

// 成绩单生成相关的API
import { generateReportCardPDF, type ReportCardData } from './reportCard';

const reportCardRouter = router({
  // 获取学生某次考试的完整成绩单数据
  getReportCard: protectedProcedure
    .input(z.object({
      examId: z.number().int(),
      studentId: z.number().int(),
    }))
    .query(async ({ input }) => {
      const reportCard = await db.getReportCardData(input.examId, input.studentId);
      if (!reportCard) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: '成绩单数据不存在',
        });
      }
      return reportCard;
    }),

  // 获取某次考试的所有学生成绩单列表（用于批量生成）
  getExamReportCards: protectedProcedure
    .input(z.object({
      examId: z.number().int(),
    }))
    .query(async ({ input }) => {
      const reportCards = await db.getExamReportCards(input.examId);
      return reportCards;
    }),
  
  // 生成成绩单PDF
  generatePDF: protectedProcedure
    .input(z.object({
      examId: z.number().int(),
      studentId: z.number().int(),
      schoolName: z.string().optional().default('Way To Future'),
    }))
    .mutation(async ({ input }) => {
      // 获取成绩单数据
      const reportCardData = await db.getReportCardData(input.examId, input.studentId);
      if (!reportCardData) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: '成绩单数据不存在',
        });
      }
      
      // 转换数据格式
      const pdfData: ReportCardData = {
        studentName: reportCardData.studentInfo.studentName,
        studentNumber: reportCardData.studentInfo.studentNumber,
        schoolName: input.schoolName,
        grade: reportCardData.examInfo.gradeName,
        className: reportCardData.studentInfo.className,
        examName: reportCardData.examInfo.examName,
        schoolYear: '2025-2026', // TODO: 从考试信息中获取
        semester: 'S2', // TODO: 从考试信息中获取
        examDate: new Date(reportCardData.examInfo.examDate).toLocaleDateString('zh-CN'),
        subjects: reportCardData.moduleAnalysis.map(m => ({
          name: m.module,
          score: m.earned,
          totalScore: m.max,
        })),
        totalScore: reportCardData.totalEarned,
        totalPossibleScore: reportCardData.totalMax,
        averageScore: reportCardData.totalEarned / reportCardData.moduleAnalysis.length,
        teacherComment: undefined,
      };
      
      // 生成PDF
      const pdfBuffer = await generateReportCardPDF(pdfData);
      
      // 返回base64编码的PDF
      return {
        success: true,
        pdf: pdfBuffer.toString('base64'),
        filename: `成绩单_${reportCardData.studentInfo.studentName}_${reportCardData.examInfo.examName}.pdf`,
      };
    }),
});

export const appRouter = router({
  system: systemRouter,
  
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),

  // ============= Teacher Auth Routes =============
  teacherAuth: router({
    // 教师登录
    login: publicProcedure
      .input(z.object({
        username: z.string().min(1),
        password: z.string().min(1),
      }))
      .mutation(async ({ input }) => {
        const result = await teacherAuth.loginTeacher(input.username, input.password);
        if (!result) {
          throw new TRPCError({
            code: 'UNAUTHORIZED',
            message: '用户名或密码错误',
          });
        }
        return result;
      }),

    // 验证token
    verifyToken: publicProcedure
      .input(z.object({ token: z.string() }))
      .query(async ({ input }) => {
        const payload = await teacherAuth.verifyTeacherToken(input.token);
        if (!payload) {
          throw new TRPCError({
            code: 'UNAUTHORIZED',
            message: 'Token无效或已过期',
          });
        }
        // 获取教师完整信息
        const teacher = await db.getTeacherById(payload.teacherId);
        if (!teacher) {
          throw new TRPCError({
            code: 'NOT_FOUND',
            message: '教师不存在',
          });
        }
        const { password: _, ...teacherWithoutPassword } = teacher;
        return teacherWithoutPassword;
      }),
  }),

  // ============= Teacher Management Routes =============
  teachers: router({
    // 获取所有教师列表
    list: protectedProcedure.query(async () => {
      const teachers = await db.getAllTeachers();
      return teachers.map(({ password, ...teacher }) => teacher);
    }),

    // 创建教师账户（仅管理员）
    create: protectedProcedure
      .input(z.object({
        username: z.string().min(1).max(50),
        password: z.string().min(6),
        name: z.string().min(1).max(100),
        email: z.string().email().optional().nullable(),
        phone: z.string().max(20).optional().nullable(),
        role: z.enum(['admin', 'teacher']),
      }))
      .mutation(async ({ input, ctx }) => {
        // TODO: 检查当前用户是否为管理员
        const hashedPassword = await teacherAuth.hashPassword(input.password);
        const result = await db.createTeacher({
          ...input,
          password: hashedPassword,
          status: 'active',
        });
        const insertId = (result as any).insertId || (result as any)[0]?.insertId;
        return { success: true, id: insertId };
      }),

    // 更新教师信息
    update: protectedProcedure
      .input(z.object({
        id: z.number().int(),
        data: z.object({
          name: z.string().min(1).max(100).optional(),
          email: z.string().email().optional().nullable(),
          phone: z.string().max(20).optional().nullable(),
          role: z.enum(['admin', 'teacher']).optional(),
          status: z.enum(['active', 'inactive']).optional(),
        }),
      }))
      .mutation(async ({ input }) => {
        await db.updateTeacher(input.id, input.data);
        return { success: true };
      }),

    // 修改密码
    changePassword: protectedProcedure
      .input(z.object({
        id: z.number().int(),
        newPassword: z.string().min(6),
      }))
      .mutation(async ({ input }) => {
        const hashedPassword = await teacherAuth.hashPassword(input.newPassword);
        await db.updateTeacher(input.id, { password: hashedPassword });
        return { success: true };
      }),

    // 删除教师
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        await db.deleteTeacher(input.id);
        return { success: true };
      }),
  }),

  // ============= Grade Routes =============
  grades: router({
    list: protectedProcedure.query(async () => {
      return await db.getAllGrades();
    }),
    
    create: protectedProcedure
      .input(gradeSchema)
      .mutation(async ({ input, ctx }) => {
        const result = await db.createGrade(input);
        const insertId = (result as any).insertId || (result as any)[0]?.insertId;
        return { success: true, id: insertId };
      }),
    
    update: protectedProcedure
      .input(z.object({ id: z.number().int(), data: gradeSchema.partial() }))
      .mutation(async ({ input }) => {
        await db.updateGrade(input.id, input.data);
        return { success: true };
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        await db.deleteGrade(input.id);
        return { success: true };
      }),
  }),

  // ============= Class Routes =============
  classes: router({
    list: protectedProcedure.query(async () => {
      return await db.getAllClasses();
    }),
    
    byGrade: protectedProcedure
      .input(z.object({ gradeId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getClassesByGrade(input.gradeId);
      }),
    
    create: protectedProcedure
      .input(classSchema)
      .mutation(async ({ input }) => {
        await db.createClass(input);
        return { success: true };
      }),
    
    update: protectedProcedure
      .input(z.object({ id: z.number().int(), data: classSchema.partial() }))
      .mutation(async ({ input }) => {
        await db.updateClass(input.id, input.data);
        return { success: true };
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        await db.deleteClass(input.id);
        return { success: true };
      }),
  }),

  // ============= Subject Routes =============
  subjects: router({
    list: protectedProcedure.query(async () => {
      return await db.getAllSubjects();
    }),
    
    create: protectedProcedure
      .input(subjectSchema)
      .mutation(async ({ input }) => {
        const result = await db.createSubject(input);
        const insertId = (result as any).insertId || (result as any)[0]?.insertId;
        return { success: true, id: insertId };
      }),
    
    update: protectedProcedure
      .input(z.object({ id: z.number().int(), data: subjectSchema.partial() }))
      .mutation(async ({ input }) => {
        await db.updateSubject(input.id, input.data);
        return { success: true };
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        await db.deleteSubject(input.id);
        return { success: true };
      }),
  }),

  // ============= Student Routes =============
  students: router({
    list: protectedProcedure.query(async () => {
      return await db.getAllStudents();
    }),
    
    byClass: protectedProcedure
      .input(z.object({ classId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getStudentsByClass(input.classId);
      }),
    
    getById: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getStudentById(input.id);
      }),
    
    create: protectedProcedure
      .input(studentSchema)
      .mutation(async ({ input }) => {
        await db.createStudent(input);
        return { success: true };
      }),
    
    update: protectedProcedure
      .input(z.object({ id: z.number().int(), data: studentSchema.partial() }))
      .mutation(async ({ input }) => {
        await db.updateStudent(input.id, input.data);
        return { success: true };
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        await db.deleteStudent(input.id);
        return { success: true };
      }),
  }),



  // ============= Question Routes =============
  questions: router({
    byExamTemplate: protectedProcedure
      .input(z.object({ examTemplateId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getQuestionsByExamTemplate(input.examTemplateId);
      }),
    
    create: protectedProcedure
      .input(questionSchema)
      .mutation(async ({ input }) => {
        await db.createQuestion({
          ...input,
          score: input.score.toString() as any,
        });
        return { success: true };
      }),
    
    createBatch: protectedProcedure
      .input(z.object({ questions: z.array(questionSchema) }))
      .mutation(async ({ input }) => {
        const questionsWithScore = input.questions.map(q => ({
          ...q,
          score: q.score.toString() as any,
        }));
        await db.createQuestions(questionsWithScore);
        return { success: true };
      }),
    
    update: protectedProcedure
      .input(z.object({ id: z.number().int(), data: questionSchema.partial() }))
      .mutation(async ({ input }) => {
        const updateData = input.data.score !== undefined
          ? { ...input.data, score: input.data.score.toString() as any }
          : input.data;
        await db.updateQuestion(input.id, updateData as any);
        return { success: true };
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        await db.deleteQuestion(input.id);
        return { success: true };
      }),
  }),

  // ============= Exam Routes =============
  exams: router({
    list: protectedProcedure.query(async () => {
      return await db.getAllExams();
    }),
    
    getById: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getExamById(input.id);
      }),
    
    byClass: protectedProcedure
      .input(z.object({ classId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getExamsByClass(input.classId);
      }),
    
    create: protectedProcedure
      .input(examSchema)
      .mutation(async ({ input, ctx }) => {
        const result = await db.createExam({
          ...input,
          createdBy: ctx.user.id,
        });
        const insertId = (result as any)[0]?.insertId || (result as any).insertId;
        return { success: true, id: insertId };
      }),
    
    update: protectedProcedure
      .input(z.object({ id: z.number().int(), data: examSchema.partial() }))
      .mutation(async ({ input }) => {
        await db.updateExam(input.id, input.data);
        return { success: true };
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        // 同时删除关联的成绩和成绩单
        await db.deleteScoresByExam(input.id);
        await db.deleteExam(input.id);
        return { success: true };
      }),
  }),

  // ============= Score Routes =============
  scores: router({
    // 获取考试的所有成绩（按学生和题目组织）
    byExamWithDetails: protectedProcedure
      .input(z.object({ examId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getScoresWithDetailsByExam(input.examId);
      }),
    
    byExam: protectedProcedure
      .input(z.object({ examId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getScoresByExam(input.examId);
      }),
    
    byStudent: protectedProcedure
      .input(z.object({ examId: z.number().int(), studentId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getScoresByStudent(input.examId, input.studentId);
      }),
    
    create: protectedProcedure
      .input(scoreSchema)
      .mutation(async ({ input, ctx }) => {
        await db.createScore({
          ...input,
          score: input.score.toString() as any,
          createdBy: ctx.user.id,
        });
        return { success: true };
      }),
    
    createBatch: protectedProcedure
      .input(z.object({ scores: z.array(scoreSchema) }))
      .mutation(async ({ input, ctx }) => {
        const scoresWithCreator = input.scores.map(score => ({
          ...score,
          score: score.score.toString() as any,
          createdBy: ctx.user.id,
        }));
        await db.createScores(scoresWithCreator);
        return { success: true };
      }),
    
    // 自动保存（创建或更新）
    upsert: protectedProcedure
      .input(scoreSchema)
      .mutation(async ({ input, ctx }) => {
        await db.upsertScore({
          ...input,
          score: input.score.toString() as any,
          createdBy: ctx.user.id,
        });
        return { success: true };
      }),
    
    update: protectedProcedure
      .input(z.object({ id: z.number().int(), data: scoreSchema.partial() }))
      .mutation(async ({ input }) => {
        const updateData = input.data.score !== undefined 
          ? { ...input.data, score: input.data.score.toString() as any }
          : input.data;
        await db.updateScore(input.id, updateData as any);
        return { success: true };
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        await db.deleteScore(input.id);
        return { success: true };
      }),
  }),

  // ============= Report Card Routes =============
  reportCards: router({
    byExam: protectedProcedure
      .input(z.object({ examId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getReportCardsByExam(input.examId);
      }),
    
    getByStudent: protectedProcedure
      .input(z.object({ examId: z.number().int(), studentId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getReportCard(input.examId, input.studentId);
      }),
    
    generate: protectedProcedure
      .input(z.object({ examId: z.number().int() }))
      .mutation(async ({ input }) => {
        const count = await db.generateReportCards(input.examId);
        return { success: true, count };
      }),
  }),

  // ============= Exam Sessions Routes =============
  examSessions: router({
    list: protectedProcedure
      .query(async () => {
        return await db.getAllExamSessions();
      }),
    
    getById: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getExamSessionById(input.id);
      }),
    
    create: protectedProcedure
      .input(z.object({
        name: z.string().min(1).max(200),
        schoolYear: z.string().min(1).max(50),
        semester: z.string().min(1).max(20),
        startDate: z.string().optional(),
        endDate: z.string().optional(),
        description: z.string().optional(),
        status: z.enum(['draft', 'active', 'completed', 'archived']).default('draft'),
      }))
      .mutation(async ({ input, ctx }) => {
        const teacherId = ctx.user?.id;
        if (!teacherId) throw new TRPCError({ code: 'UNAUTHORIZED', message: '请先登录' });
        
        const sessionData = {
          ...input,
          startDate: input.startDate ? new Date(input.startDate) : null,
          endDate: input.endDate ? new Date(input.endDate) : null,
          createdBy: teacherId,
        };
        
        await db.createExamSession(sessionData as any);
        return { success: true };
      }),
    
    update: protectedProcedure
      .input(z.object({
        id: z.number().int(),
        data: z.object({
          name: z.string().min(1).max(200).optional(),
          schoolYear: z.string().min(1).max(50).optional(),
          semester: z.string().min(1).max(20).optional(),
          startDate: z.string().optional().nullable(),
          endDate: z.string().optional().nullable(),
          description: z.string().optional().nullable(),
          status: z.enum(['draft', 'active', 'completed', 'archived']).optional(),
        }),
      }))
      .mutation(async ({ input }) => {
        const updateData = {
          ...input.data,
          startDate: input.data.startDate ? new Date(input.data.startDate) : undefined,
          endDate: input.data.endDate ? new Date(input.data.endDate) : undefined,
        };
        await db.updateExamSession(input.id, updateData as any);
        return { success: true };
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        await db.deleteExamSession(input.id);
        return { success: true };
      }),
  }),

  // ============= Exam Templates Routes =============
  examTemplates: router({
    list: protectedProcedure
      .query(async () => {
        return await db.getAllExamTemplates();
      }),
    
    byExamSession: protectedProcedure
      .input(z.object({ examSessionId: z.number().int() }))
      .query(async ({ input }) => {
        const db_instance = await db.getDb();
        if (!db_instance) return [];
        return await db_instance.select().from(examTemplates).where(eq(examTemplates.examSessionId, input.examSessionId));
      }),
    
    // 获取未关联到任何考试的试卷（试卷库）
    unassigned: protectedProcedure
      .query(async () => {
        const db_instance = await db.getDb();
        if (!db_instance) return [];
        return await db_instance.select().from(examTemplates).where(eq(examTemplates.examSessionId, 0));
      }),
    
    // 关联试卷到考试
    assignToExam: protectedProcedure
      .input(z.object({ 
        templateId: z.number().int(), 
        examSessionId: z.number().int() 
      }))
      .mutation(async ({ input }) => {
        await db.updateExamTemplate(input.templateId, { examSessionId: input.examSessionId } as any);
        return { success: true };
      }),
    
    bySubjectAndGrade: protectedProcedure
      .input(z.object({ subjectId: z.number().int(), gradeId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getExamTemplatesBySubjectAndGrade(input.subjectId, input.gradeId);
      }),
    
    getById: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .query(async ({ input }) => {
        return await db.getExamTemplateById(input.id);
      }),
    
    create: protectedProcedure
      .input(examTemplateSchema)
      .mutation(async ({ input, ctx }) => {
        const teacherId = ctx.user?.id;
        if (!teacherId) throw new TRPCError({ code: 'UNAUTHORIZED', message: '请先登录' });
        
        const result = await db.createExamTemplate({
          ...input,
          totalScore: input.totalScore.toString() as any,
          createdBy: teacherId,
        });
        const insertId = (result as any).insertId || (result as any)[0]?.insertId;
        return { success: true, id: insertId };
      }),
    
    update: protectedProcedure
      .input(z.object({ id: z.number().int(), data: examTemplateSchema.partial() }))
      .mutation(async ({ input }) => {
        const updateData = input.data.totalScore !== undefined
          ? { ...input.data, totalScore: input.data.totalScore.toString() as any }
          : input.data;
        await db.updateExamTemplate(input.id, updateData as any);
        return { success: true };
      }),
    
    delete: protectedProcedure
      .input(z.object({ id: z.number().int() }))
      .mutation(async ({ input }) => {
        // 同时删除关联的题目
        await db.deleteQuestionsByExamTemplate(input.id);
        await db.deleteExamTemplate(input.id);
        return { success: true };
      }),
  }),

  // ============= Statistics Routes =============
  statistics: router({
    examStats: protectedProcedure
      .input(z.object({ examId: z.number().int() }))
      .query(async ({ input }) => {
        return await db.calculateExamStatistics(input.examId);
      }),
  }),

  // ============= Report Card Generation Routes =============
  reportCard: reportCardRouter,
});

export type AppRouter = typeof appRouter;
