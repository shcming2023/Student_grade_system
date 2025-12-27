import { drizzle } from 'drizzle-orm/mysql2';
import { mysqlTable, int, varchar, text } from 'drizzle-orm/mysql-core';
import dotenv from 'dotenv';
dotenv.config();

const subjects = mysqlTable('subjects', {
  id: int('id').autoincrement().primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
  code: varchar('code', { length: 100 }).notNull(),
  category: varchar('category', { length: 50 }),
  description: text('description'),
});

const db = drizzle(process.env.DATABASE_URL);

const newSubjects = [
  { name: '朗文英语', code: 'longman_english', category: 'english', description: '朗文英语教材' },
  { name: '牛津英语', code: 'oxford_english', category: 'english', description: '牛津英语教材' },
  { name: '先锋英语', code: 'pioneer_english', category: 'english', description: '先锋英语教材' },
  { name: '中数', code: 'chinese_math', category: 'math', description: '中文数学' },
  { name: '英数', code: 'english_math', category: 'math', description: '英文数学' },
  { name: '语文', code: 'chinese', category: 'chinese', description: '语文' },
];

for (const subject of newSubjects) {
  try {
    await db.insert(subjects).values(subject);
    console.log(`✓ 创建科目: ${subject.name}`);
  } catch (error) {
    console.log(`跳过: ${subject.name} (可能已存在)`);
  }
}

console.log('科目创建完成');
process.exit(0);
