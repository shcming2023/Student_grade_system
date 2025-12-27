import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { trpc } from '@/lib/trpc';

// 教师信息类型
export interface Teacher {
  id: number;
  username: string;
  name: string;
  email: string | null;
  phone: string | null;
  role: 'admin' | 'teacher';
  status: 'active' | 'inactive';
  createdAt: Date;
  lastLoginAt: Date | null;
}

// Context类型定义
interface TeacherAuthContextType {
  teacher: Teacher | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isTeacher: boolean;
}

const TeacherAuthContext = createContext<TeacherAuthContextType | undefined>(undefined);

const TOKEN_KEY = 'teacher_auth_token';

export function TeacherAuthProvider({ children }: { children: ReactNode }) {
  const [teacher, setTeacher] = useState<Teacher | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loginMutation = trpc.teacherAuth.login.useMutation();
  const verifyTokenQuery = trpc.teacherAuth.verifyToken.useQuery(
    { token: token || '' },
    { enabled: !!token, retry: false }
  );

  // 初始化：从localStorage恢复token
  useEffect(() => {
    const savedToken = localStorage.getItem(TOKEN_KEY);
    if (savedToken) {
      setToken(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  // 验证token并获取教师信息
  useEffect(() => {
    if (verifyTokenQuery.data) {
      setTeacher(verifyTokenQuery.data as Teacher);
      setLoading(false);
    } else if (verifyTokenQuery.error) {
      // Token无效，清除
      localStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setTeacher(null);
      setLoading(false);
    }
  }, [verifyTokenQuery.data, verifyTokenQuery.error]);

  // 登录函数
  const login = async (username: string, password: string) => {
    try {
      const result = await loginMutation.mutateAsync({ username, password });
      const { token: newToken, teacher: teacherData } = result;
      
      // 保存token
      localStorage.setItem(TOKEN_KEY, newToken);
      setToken(newToken);
      setTeacher(teacherData as Teacher);
    } catch (error: any) {
      throw new Error(error.message || '登录失败');
    }
  };

  // 登出函数
  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setTeacher(null);
  };

  // 计算派生状态
  const isAuthenticated = !!teacher && !!token;
  const isAdmin = teacher?.role === 'admin';
  const isTeacher = teacher?.role === 'teacher';

  const value: TeacherAuthContextType = {
    teacher,
    token,
    loading,
    login,
    logout,
    isAuthenticated,
    isAdmin,
    isTeacher,
  };

  return (
    <TeacherAuthContext.Provider value={value}>
      {children}
    </TeacherAuthContext.Provider>
  );
}

// Hook：使用教师认证
export function useTeacherAuth() {
  const context = useContext(TeacherAuthContext);
  if (context === undefined) {
    throw new Error('useTeacherAuth must be used within a TeacherAuthProvider');
  }
  return context;
}
