import { drizzle } from 'drizzle-orm/mysql2';
import { sql } from 'drizzle-orm';
import dotenv from 'dotenv';
dotenv.config();

const db = drizzle(process.env.DATABASE_URL);

console.log('=== 检查题目数据完整性 ===\n');

// 随机抽取几个试卷模板的题目查看
const templates = await db.execute(sql`SELECT id, name FROM exam_templates LIMIT 5`);

for (const template of templates[0]) {
  console.log(`\n试卷: ${template.name}`);
  const questions = await db.execute(sql`
    SELECT questionNumber, module, knowledgePoint, questionType, score 
    FROM questions 
    WHERE examTemplateId = ${template.id} 
    LIMIT 5
  `);
  
  if (questions[0].length === 0) {
    console.log('  ❌ 没有题目');
  } else {
    questions[0].forEach(q => {
      console.log(`  题${q.questionNumber}: 模块=${q.module || '空'}, 知识点=${q.knowledgePoint || '空'}, 题型=${q.questionType || '空'}, 分值=${q.score}`);
    });
  }
}

// 统计空字段
console.log('\n=== 字段完整性统计 ===');
const stats = await db.execute(sql`
  SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN module IS NULL OR module = '' THEN 1 ELSE 0 END) as empty_module,
    SUM(CASE WHEN knowledgePoint IS NULL OR knowledgePoint = '' THEN 1 ELSE 0 END) as empty_knowledge,
    SUM(CASE WHEN questionType IS NULL OR questionType = '' THEN 1 ELSE 0 END) as empty_type
  FROM questions
`);

const stat = stats[0][0];
console.log(`总题目数: ${stat.total}`);
console.log(`模块为空: ${stat.empty_module} (${(stat.empty_module/stat.total*100).toFixed(1)}%)`);
console.log(`知识点为空: ${stat.empty_knowledge} (${(stat.empty_knowledge/stat.total*100).toFixed(1)}%)`);
console.log(`题型为空: ${stat.empty_type} (${(stat.empty_type/stat.total*100).toFixed(1)}%)`);

process.exit(0);
