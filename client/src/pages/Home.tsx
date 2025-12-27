import { useAuth } from "@/_core/hooks/useAuth";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { trpc } from "@/lib/trpc";
import { Users, School, BookOpen, FileText, TrendingUp, Award } from "lucide-react";

export default function Home() {
  const { user } = useAuth();
  
  // 获取统计数据
  const { data: students } = trpc.students.list.useQuery();
  const { data: classes } = trpc.classes.list.useQuery();
  const { data: subjects } = trpc.subjects.list.useQuery();
  const { data: examTemplates } = trpc.examTemplates.list.useQuery();

  const stats = [
    {
      title: "学生总数",
      value: students?.length || 0,
      icon: Users,
      description: "在校学生人数",
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      title: "班级数量",
      value: classes?.length || 0,
      icon: School,
      description: "活跃班级数",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      title: "科目数量",
      value: subjects?.length || 0,
      icon: BookOpen,
      description: "开设科目数",
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      title: "试卷模板",
      value: examTemplates?.length || 0,
      icon: FileText,
      description: "已创建模板",
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* 欢迎区域 */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">欢迎回来，{user?.name || "老师"}！</h1>
          <p className="text-muted-foreground mt-2">这是您的成绩管理系统仪表盘</p>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <Card key={index} className="border-border hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={`h-5 w-5 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-foreground">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* 快速操作 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                快速操作
              </CardTitle>
              <CardDescription>常用功能快捷入口</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <a
                href="/students"
                className="block p-4 rounded-lg border border-border hover:bg-muted transition-colors"
              >
                <div className="font-medium text-foreground">管理学生信息</div>
                <div className="text-sm text-muted-foreground mt-1">添加、编辑或删除学生档案</div>
              </a>
              <a
                href="/score-entry"
                className="block p-4 rounded-lg border border-border hover:bg-muted transition-colors"
              >
                <div className="font-medium text-foreground">录入成绩</div>
                <div className="text-sm text-muted-foreground mt-1">为学生录入考试成绩</div>
              </a>
              <a
                href="/scores"
                className="block p-4 rounded-lg border border-border hover:bg-muted transition-colors"
              >
                <div className="font-medium text-foreground">查询成绩</div>
                <div className="text-sm text-muted-foreground mt-1">查看和分析学生成绩数据</div>
              </a>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="h-5 w-5 text-primary" />
                系统说明
              </CardTitle>
              <CardDescription>了解系统功能</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-4 rounded-lg bg-muted/50">
                <div className="font-medium text-foreground">学生管理</div>
                <div className="text-sm text-muted-foreground mt-1">
                  管理学生基本信息、班级分配和学籍状态
                </div>
              </div>
              <div className="p-4 rounded-lg bg-muted/50">
                <div className="font-medium text-foreground">试卷模板</div>
                <div className="text-sm text-muted-foreground mt-1">
                  创建试卷模板，定义题目结构和分值
                </div>
              </div>
              <div className="p-4 rounded-lg bg-muted/50">
                <div className="font-medium text-foreground">成绩分析</div>
                <div className="text-sm text-muted-foreground mt-1">
                  自动计算排名、生成分析报告和学习建议
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
