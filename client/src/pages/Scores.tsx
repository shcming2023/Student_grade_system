import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { trpc } from "@/lib/trpc";
import { FileText, Loader2 } from "lucide-react";
import { useState } from "react";
import { useLocation } from "wouter";

export default function Scores() {
  const [, setLocation] = useLocation();
  const [selectedExam, setSelectedExam] = useState<string>("");

  const { data: exams, isLoading: loadingExams } = trpc.exams.list.useQuery();
  const { data: classes } = trpc.classes.list.useQuery();

  const { data: examScores, isLoading: loadingScores } = trpc.scores.byExam.useQuery(
    { examId: parseInt(selectedExam) },
    { enabled: !!selectedExam }
  );

  // 按学生分组成绩
  const studentScores = examScores?.reduce((acc: Record<number, any>, score: any) => {
    if (!acc[score.studentId]) {
      acc[score.studentId] = {
        studentId: score.studentId,
        studentName: score.studentName,
        studentNumber: score.studentNumber,
        className: score.className,
        scores: [],
        totalScore: 0,
      };
    }
    acc[score.studentId].scores.push(score);
    acc[score.studentId].totalScore += parseFloat(score.score?.toString() || '0');
    return acc;
  }, {});

  const studentList = studentScores ? Object.values(studentScores).sort((a: any, b: any) => b.totalScore - a.totalScore) : [];

  const selectedExamData = exams?.find((e: any) => e.id === parseInt(selectedExam));

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground">成绩查询</h1>
          <p className="text-muted-foreground mt-2">查看和分析学生成绩数据</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>选择考试</CardTitle>
            <CardDescription>选择要查看的考试</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Select value={selectedExam} onValueChange={setSelectedExam}>
                <SelectTrigger className="w-[400px]">
                  <SelectValue placeholder="选择考试" />
                </SelectTrigger>
                <SelectContent>
                  {loadingExams ? (
                    <div className="p-4 text-center text-muted-foreground">
                      <Loader2 className="h-4 w-4 animate-spin mx-auto" />
                    </div>
                  ) : exams && exams.length > 0 ? (
                    exams.map((exam: any) => {
                      const examClass = classes?.find((c: any) => c.id === exam.classId);
                      return (
                        <SelectItem key={exam.id} value={exam.id.toString()}>
                          {exam.name} - {examClass?.name || '未知班级'} - {new Date(exam.examDate).toLocaleDateString('zh-CN')}
                        </SelectItem>
                      );
                    })
                  ) : (
                    <div className="p-4 text-center text-muted-foreground">暂无考试记录</div>
                  )}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {selectedExam && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>成绩列表</CardTitle>
                  <CardDescription>
                    {selectedExamData?.name} - 共{studentList.length}名学生
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loadingScores ? (
                <div className="text-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
                </div>
              ) : studentList.length > 0 ? (
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[80px]">排名</TableHead>
                        <TableHead>学号</TableHead>
                        <TableHead>姓名</TableHead>
                        <TableHead>班级</TableHead>
                        <TableHead className="text-center">总分</TableHead>
                        <TableHead className="text-center w-[120px]">操作</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {studentList.map((student: any, index: number) => (
                        <TableRow key={student.studentId}>
                          <TableCell className="font-medium">
                            {index + 1}
                          </TableCell>
                          <TableCell>{student.studentNumber}</TableCell>
                          <TableCell className="font-medium">{student.studentName}</TableCell>
                          <TableCell>{student.className}</TableCell>
                          <TableCell className="text-center font-bold text-lg">
                            {student.totalScore.toFixed(1)}
                          </TableCell>
                          <TableCell className="text-center">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setLocation(`/report-card/${selectedExam}/${student.studentId}`)}
                            >
                              <FileText className="h-4 w-4 mr-2" />
                              成绩单
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  该考试暂无成绩记录
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
