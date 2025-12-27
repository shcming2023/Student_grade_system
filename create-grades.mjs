import { drizzle } from 'drizzle-orm/mysql2';
import { mysqlTable, int, varchar } from 'drizzle-orm/mysql-core';
import dotenv from 'dotenv';
dotenv.config();

const grades = mysqlTable('grades', {
  id: int('id').autoincrement().primaryKey(),
  name: varchar('name', { length: 50 }).notNull(),
  displayName: varchar('displayName', { length: 100 }).notNull(),
  sortOrder: int('sortOrder').notNull(),
});

const db = drizzle(process.env.DATABASE_URL);

const newGrades = [
  { name: 'G2', displayName: '二年级', sortOrder: 2 },
  { name: 'G3', displayName: '三年级', sortOrder: 3 },
  { name: 'G4', displayName: '四年级', sortOrder: 4 },
  { name: 'G5', displayName: '五年级', sortOrder: 5 },
  { name: 'G6', displayName: '六年级', sortOrder: 6 },
];

for (const grade of newGrades) {
  try {
    await db.insert(grades).values(grade);
    console.log(`✓ 创建年级: ${grade.displayName}`);
  } catch (error) {
    console.log(`跳过: ${grade.displayName} (可能已存在)`);
  }
}

console.log('年级创建完成');
process.exit(0);
