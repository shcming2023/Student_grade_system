import { drizzle } from 'drizzle-orm/mysql2';
import { mysqlTable, int, varchar, text, decimal } from 'drizzle-orm/mysql-core';
import { sql } from 'drizzle-orm';
import dotenv from 'dotenv';
dotenv.config();

const db = drizzle(process.env.DATABASE_URL);

console.log('=== 导入数据统计 ===\n');

// 统计科目
const subjectsCount = await db.execute(sql`SELECT COUNT(*) as count FROM subjects`);
console.log(`科目总数: ${subjectsCount[0][0].count}`);

// 统计年级
const gradesCount = await db.execute(sql`SELECT COUNT(*) as count FROM grades`);
console.log(`年级总数: ${gradesCount[0][0].count}`);

// 统计试卷模板
const templatesCount = await db.execute(sql`SELECT COUNT(*) as count FROM exam_templates`);
console.log(`试卷模板总数: ${templatesCount[0][0].count}`);

// 统计题目
const questionsCount = await db.execute(sql`SELECT COUNT(*) as count FROM questions`);
console.log(`题目总数: ${questionsCount[0][0].count}`);

// 按科目统计模板
console.log('\n=== 按科目统计 ===');
const templatesBySubject = await db.execute(sql`
  SELECT s.name, COUNT(et.id) as count 
  FROM subjects s 
  LEFT JOIN exam_templates et ON s.id = et.subjectId 
  GROUP BY s.id, s.name
  ORDER BY s.name
`);
for (const row of templatesBySubject[0]) {
  console.log(`${row.name}: ${row.count} 个模板`);
}

// 按年级统计模板
console.log('\n=== 按年级统计 ===');
const templatesByGrade = await db.execute(sql`
  SELECT g.name, COUNT(et.id) as count 
  FROM grades g 
  LEFT JOIN exam_templates et ON g.id = et.gradeId 
  GROUP BY g.id, g.name
  ORDER BY g.sortOrder
`);
for (const row of templatesByGrade[0]) {
  console.log(`${row.name}: ${row.count} 个模板`);
}

process.exit(0);
