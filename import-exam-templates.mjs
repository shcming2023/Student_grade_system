#!/usr/bin/env node
/**
 * 导入Excel解析的试卷模板数据到数据库
 */
import { readFileSync } from 'fs';
import { drizzle } from 'drizzle-orm/mysql2';
import { eq } from 'drizzle-orm';
import { mysqlTable, int, varchar, text, decimal, timestamp } from 'drizzle-orm/mysql-core';

// 读取环境变量
import dotenv from 'dotenv';
dotenv.config();

// 定义表结构
const subjects = mysqlTable('subjects', {
  id: int('id').autoincrement().primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
});

const grades = mysqlTable('grades', {
  id: int('id').autoincrement().primaryKey(),
  name: varchar('name', { length: 50 }).notNull(),
});

const examTemplates = mysqlTable('exam_templates', {
  id: int('id').autoincrement().primaryKey(),
  name: varchar('name', { length: 200 }).notNull(),
  subjectId: int('subjectId').notNull(),
  gradeId: int('gradeId').notNull(),
  totalScore: decimal('totalScore', { precision: 10, scale: 2 }).notNull(),
  description: text('description'),
  createdBy: int('createdBy').notNull(),
});

const questions = mysqlTable('questions', {
  id: int('id').autoincrement().primaryKey(),
  examTemplateId: int('examTemplateId').notNull(),
  questionNumber: int('questionNumber').notNull(),
  module: varchar('module', { length: 100 }),
  knowledgePoint: text('knowledgePoint'),
  questionType: varchar('questionType', { length: 100 }),
  score: decimal('score', { precision: 10, scale: 2 }).notNull(),
  sortOrder: int('sortOrder').notNull(),
});

const DATABASE_URL = process.env.DATABASE_URL;
if (!DATABASE_URL) {
  console.error('错误: 未找到 DATABASE_URL 环境变量');
  process.exit(1);
}

const db = drizzle(DATABASE_URL);

async function importTemplates() {
  try {
    // 读取解析后的JSON数据
    const jsonData = readFileSync('/home/ubuntu/exam_templates_clean.json', 'utf-8');
    const templates = JSON.parse(jsonData);
    
    console.log(`准备导入 ${templates.length} 个试卷模板...`);
    
    // 获取所有科目和年级
    const allSubjects = await db.select().from(subjects);
    const allGrades = await db.select().from(grades);
    
    const subjectMap = new Map(allSubjects.map(s => [s.name, s.id]));
    const gradeMap = new Map(allGrades.map(g => [g.name, g.id]));
    
    let successCount = 0;
    let errorCount = 0;
    
    for (const template of templates) {
      try {
        const subjectId = subjectMap.get(template.subjectName);
        const gradeId = gradeMap.get(template.gradeName);
        
        if (!subjectId) {
          console.error(`错误: 未找到科目 "${template.subjectName}"，跳过模板 "${template.name}"`);
          errorCount++;
          continue;
        }
        
        if (!gradeId) {
          console.error(`错误: 未找到年级 "${template.gradeName}"，跳过模板 "${template.name}"`);
          errorCount++;
          continue;
        }
        
        // 检查是否已存在同名模板
        const existing = await db.select().from(examTemplates)
          .where(eq(examTemplates.name, template.name))
          .limit(1);
        
        if (existing.length > 0) {
          console.log(`跳过: 模板 "${template.name}" 已存在`);
          continue;
        }
        
        // 创建试卷模板
        const result = await db.insert(examTemplates).values({
          name: template.name,
          subjectId: subjectId,
          gradeId: gradeId,
          totalScore: template.totalScore.toString(),
          description: template.description,
          createdBy: 1, // 默认管理员
        });
        
        const templateId = result[0].insertId;
        
        // 批量插入题目
        if (template.questions && template.questions.length > 0) {
          const questionValues = template.questions.map(q => ({
            examTemplateId: templateId,
            questionNumber: q.questionNumber,
            module: q.module,
            knowledgePoint: q.knowledgePoint,
            questionType: q.questionType,
            score: q.score.toString(),
            sortOrder: q.sortOrder,
          }));
          
          await db.insert(questions).values(questionValues);
        }
        
        console.log(`✓ 导入成功: ${template.name} (${template.questions.length}道题)`);
        successCount++;
      } catch (error) {
        console.error(`错误: 导入模板 "${template.name}" 失败:`, error.message);
        errorCount++;
      }
    }
    
    console.log(`\n导入完成:`);
    console.log(`  成功: ${successCount} 个模板`);
    console.log(`  失败: ${errorCount} 个模板`);
    
    process.exit(0);
  } catch (error) {
    console.error('导入过程发生错误:', error);
    process.exit(1);
  }
}

importTemplates();
