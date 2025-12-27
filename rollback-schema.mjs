import mysql from 'mysql2/promise';
import dotenv from 'dotenv';

dotenv.config();

async function rollbackSchema() {
  const connection = await mysql.createConnection(process.env.DATABASE_URL);
  
  try {
    console.log('开始回滚schema修改...');
    
    // 1. 为学生表恢复classId字段
    console.log('1. 为学生表添加classId字段...');
    await connection.execute(`
      ALTER TABLE students 
      ADD COLUMN IF NOT EXISTS classId INT
    `);
    
    // 2. 从grade和className恢复classId
    console.log('2. 恢复学生的classId数据...');
    await connection.execute(`
      UPDATE students s
      INNER JOIN classes c ON c.fullName = CONCAT(s.grade, '-', IFNULL(s.className, ''))
      SET s.classId = c.id
      WHERE s.classId IS NULL
    `);
    
    // 3. 设置classId为NOT NULL
    console.log('3. 设置classId为必填字段...');
    await connection.execute(`
      ALTER TABLE students 
      MODIFY COLUMN classId INT NOT NULL
    `);
    
    // 4. 添加索引
    console.log('4. 添加classId索引...');
    await connection.execute(`
      ALTER TABLE students 
      ADD INDEX IF NOT EXISTS class_idx (classId)
    `);
    
    // 5. 删除grade和className字段
    console.log('5. 删除students表的grade和className字段...');
    await connection.execute(`ALTER TABLE students DROP COLUMN IF EXISTS grade`);
    await connection.execute(`ALTER TABLE students DROP COLUMN IF EXISTS className`);
    
    // 6. 为试卷表恢复subjectId和gradeId字段
    console.log('6. 为试卷表添加subjectId和gradeId字段...');
    await connection.execute(`
      ALTER TABLE exam_templates 
      ADD COLUMN IF NOT EXISTS subjectId INT,
      ADD COLUMN IF NOT EXISTS gradeId INT
    `);
    
    // 7. 从subjectName和grade恢复subjectId和gradeId
    console.log('7. 恢复试卷的subjectId和gradeId数据...');
    await connection.execute(`
      UPDATE exam_templates et
      INNER JOIN subjects s ON et.subjectName = s.name
      INNER JOIN grades g ON et.grade = g.name
      SET et.subjectId = s.id, et.gradeId = g.id
      WHERE et.subjectId IS NULL
    `);
    
    // 8. 设置subjectId和gradeId为NOT NULL
    console.log('8. 设置subjectId和gradeId为必填字段...');
    await connection.execute(`
      ALTER TABLE exam_templates 
      MODIFY COLUMN subjectId INT NOT NULL,
      MODIFY COLUMN gradeId INT NOT NULL
    `);
    
    // 9. 添加索引
    console.log('9. 添加subjectId和gradeId索引...');
    await connection.execute(`
      ALTER TABLE exam_templates 
      ADD INDEX IF NOT EXISTS subject_grade_idx (subjectId, gradeId)
    `);
    
    // 10. 删除subjectName和grade字段
    console.log('10. 删除exam_templates表的subjectName和grade字段...');
    await connection.execute(`ALTER TABLE exam_templates DROP COLUMN IF EXISTS subjectName`);
    await connection.execute(`ALTER TABLE exam_templates DROP COLUMN IF EXISTS grade`);
    
    console.log('Schema回滚完成！');
    
  } catch (error) {
    console.error('回滚失败:', error);
    throw error;
  } finally {
    await connection.end();
  }
}

rollbackSchema().catch(console.error);
