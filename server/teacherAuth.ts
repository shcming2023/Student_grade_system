import bcrypt from 'bcryptjs';
import { SignJWT, jwtVerify } from 'jose';
import { ENV } from './_core/env';
import * as db from './db';

const JWT_SECRET = new TextEncoder().encode(process.env.JWT_SECRET || 'default-secret-key-change-in-production');

/**
 * 教师登录
 * @param username 用户名
 * @param password 密码
 * @returns 教师信息和token，如果登录失败返回null
 */
export async function loginTeacher(username: string, password: string) {
  // 查找教师
  const teacher = await db.getTeacherByUsername(username);
  
  if (!teacher) {
    return null;
  }
  
  // 检查账户状态
  if (teacher.status !== 'active') {
    throw new Error('账户已被禁用');
  }
  
  // 验证密码
  const isPasswordValid = await bcrypt.compare(password, teacher.password);
  
  if (!isPasswordValid) {
    return null;
  }
  
  // 更新最后登录时间
  await db.updateTeacherLastLogin(teacher.id);
  
  // 生成JWT token
  const token = await new SignJWT({
      teacherId: teacher.id,
      username: teacher.username,
      role: teacher.role,
      type: 'teacher',
    })
    .setProtectedHeader({ alg: 'HS256' })
    .setExpirationTime('7d')
    .sign(JWT_SECRET);
  
  // 返回教师信息（不包含密码）和token
  const { password: _, ...teacherWithoutPassword } = teacher;
  
  return {
    teacher: teacherWithoutPassword,
    token,
  };
}

/**
 * 验证教师token
 * @param token JWT token
 * @returns 解码后的payload，如果验证失败返回null
 */
export async function verifyTeacherToken(token: string) {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET);
    return payload as { teacherId: number; username: string; role: string; type: string };
  } catch (error) {
    return null;
  }
}

/**
 * 创建密码哈希
 * @param password 明文密码
 * @returns 哈希后的密码
 */
export async function hashPassword(password: string): Promise<string> {
  const salt = await bcrypt.genSalt(10);
  return await bcrypt.hash(password, salt);
}

/**
 * 初始化管理员账户
 * 如果admin账户不存在，则创建
 */
export async function initializeAdminAccount() {
  const existingAdmin = await db.getTeacherByUsername('admin');
  
  if (!existingAdmin) {
    const defaultPassword = 'admin123'; // 默认密码，建议首次登录后修改
    const hashedPassword = await hashPassword(defaultPassword);
    
    await db.createTeacher({
      username: 'admin',
      password: hashedPassword,
      name: '系统管理员',
      role: 'admin',
      status: 'active',
    });
    
    console.log('[Auth] Admin account created with default password: admin123');
    console.log('[Auth] Please change the password after first login!');
  }
}
