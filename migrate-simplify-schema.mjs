import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

dotenv.config();

async function migrateData() {
  const connection = await mysql.createConnection(process.env.DATABASE_URL);
  
  try {
    console.log('开始数据迁移...');
    
    // 1. 为学生表添加新字段
    console.log('1. 为学生表添加grade和className字段...');
    await connection.execute(`
      ALTER TABLE students 
      ADD COLUMN IF NOT EXISTS grade VARCHAR(50),
      ADD COLUMN IF NOT EXISTS className VARCHAR(100)
    `);
    
    // 2. 迁移学生数据：从classId获取年级和班级名称
    console.log('2. 迁移学生数据...');
    await connection.execute(`
      UPDATE students s
      INNER JOIN classes c ON s.classId = c.id
      INNER JOIN grades g ON c.gradeId = g.id
      SET s.grade = g.name, s.className = c.name
      WHERE s.grade IS NULL
    `);
    
    // 3. 设置grade为NOT NULL
    console.log('3. 设置grade为必填字段...');
    await connection.execute(`
      ALTER TABLE students 
      MODIFY COLUMN grade VARCHAR(50) NOT NULL
    `);
    
    // 4. 删除classId字段和索引
    console.log('4. 删除students表的classId字段...');
    await connection.execute(`ALTER TABLE students DROP INDEX IF EXISTS class_idx`);
    await connection.execute(`ALTER TABLE students DROP COLUMN IF EXISTS classId`);
    
    // 5. 为试卷表添加新字段
    console.log('5. 为试卷表添加subjectName和grade字段...');
    await connection.execute(`
      ALTER TABLE exam_templates 
      ADD COLUMN IF NOT EXISTS subjectName VARCHAR(100),
      ADD COLUMN IF NOT EXISTS grade VARCHAR(50)
    `);
    
    // 6. 迁移试卷数据：从subjectId和gradeId获取名称
    console.log('6. 迁移试卷数据...');
    await connection.execute(`
      UPDATE exam_templates et
      INNER JOIN subjects s ON et.subjectId = s.id
      INNER JOIN grades g ON et.gradeId = g.id
      SET et.subjectName = s.name, et.grade = g.name
      WHERE et.subjectName IS NULL
    `);
    
    // 7. 设置subjectName和grade为NOT NULL
    console.log('7. 设置subjectName和grade为必填字段...');
    await connection.execute(`
      ALTER TABLE exam_templates 
      MODIFY COLUMN subjectName VARCHAR(100) NOT NULL,
      MODIFY COLUMN grade VARCHAR(50) NOT NULL
    `);
    
    // 8. 删除subjectId和gradeId字段和索引
    console.log('8. 删除exam_templates表的subjectId和gradeId字段...');
    await connection.execute(`ALTER TABLE exam_templates DROP INDEX IF EXISTS subject_grade_idx`);
    await connection.execute(`ALTER TABLE exam_templates DROP COLUMN IF EXISTS subjectId`);
    await connection.execute(`ALTER TABLE exam_templates DROP COLUMN IF EXISTS gradeId`);
    
    console.log('数据迁移完成！');
    console.log('注意：classes和subjects表的数据已保留，但不再使用。如需删除这些表，请手动执行。');
    
  } catch (error) {
    console.error('迁移失败:', error);
    throw error;
  } finally {
    await connection.end();
  }
}

migrateData().catch(console.error);
