import { drizzle } from "drizzle-orm/mysql2";
import { grades, subjects, classes } from "./drizzle/schema.ts";

const db = drizzle(process.env.DATABASE_URL);

async function initData() {
  console.log("Initializing base data...");

  // 插入年级数据
  const gradeData = [
    { name: "G1", displayName: "一年级", sortOrder: 1 },
    { name: "G2", displayName: "二年级", sortOrder: 2 },
    { name: "G3", displayName: "三年级", sortOrder: 3 },
    { name: "G4", displayName: "四年级", sortOrder: 4 },
    { name: "G5", displayName: "五年级", sortOrder: 5 },
    { name: "G6", displayName: "六年级", sortOrder: 6 },
  ];

  for (const grade of gradeData) {
    try {
      await db.insert(grades).values(grade).onDuplicateKeyUpdate({ set: {} });
      console.log(`Grade ${grade.name} inserted`);
    } catch (e) {
      console.log(`Grade ${grade.name} already exists`);
    }
  }

  // 插入科目数据
  const subjectData = [
    { name: "朗文英语", code: "longman_english", category: "english", description: "朗文英语课程" },
    { name: "牛津英语", code: "oxford_english", category: "english", description: "牛津英语课程" },
    { name: "先锋英语", code: "pioneer_english", category: "english", description: "先锋英语课程" },
    { name: "中数", code: "chinese_math", category: "math", description: "中文数学课程" },
    { name: "英数", code: "english_math", category: "math", description: "英文数学课程" },
    { name: "语文", code: "chinese", category: "chinese", description: "语文课程" },
  ];

  for (const subject of subjectData) {
    try {
      await db.insert(subjects).values(subject).onDuplicateKeyUpdate({ set: {} });
      console.log(`Subject ${subject.name} inserted`);
    } catch (e) {
      console.log(`Subject ${subject.name} already exists`);
    }
  }

  console.log("Base data initialization completed!");
}

initData().catch(console.error);
