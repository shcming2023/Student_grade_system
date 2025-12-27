import { ReactNode } from 'react';
import { useLocation, Redirect } from 'wouter';
import { useTeacherAuth } from '@/contexts/TeacherAuthContext';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: ReactNode;
  requireAdmin?: boolean;
}

/**
 * 路由保护组件
 * - 未登录用户跳转到登录页
 * - requireAdmin为true时，只允许管理员访问
 */
export default function ProtectedRoute({ children, requireAdmin = false }: ProtectedRouteProps) {
  const { isAuthenticated, isAdmin, loading } = useTeacherAuth();
  const [location] = useLocation();

  // 加载中显示loading
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  // 未登录，跳转到登录页
  if (!isAuthenticated) {
    return <Redirect to={`/teacher-login?redirect=${encodeURIComponent(location)}`} />;
  }

  // 需要管理员权限但不是管理员
  if (requireAdmin && !isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-destructive mb-2">权限不足</h1>
          <p className="text-muted-foreground">您没有权限访问此页面</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
