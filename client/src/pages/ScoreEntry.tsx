import { useState, useEffect, useMemo } from "react";
import { trpc } from "@/lib/trpc";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Loader2, Save } from "lucide-react";

export default function ScoreEntry() {
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  const [selectedExamId, setSelectedExamId] = useState<number | null>(null);
  const [examName, setExamName] = useState("");
  const [examDate, setExamDate] = useState(new Date().toISOString().split('T')[0]);
  const [scores, setScores] = useState<Record<string, number>>({});
  const [savingScores, setSavingScores] = useState<Set<string>>(new Set());

  const utils = trpc.useUtils();

  // 获取所有班级
  const { data: classes = [] } = trpc.classes.list.useQuery();

  // 获取所有试卷模板
  const { data: templates = [] } = trpc.examTemplates.list.useQuery();

  // 获取选中班级的考试列表
  const { data: exams = [] } = trpc.exams.byClass.useQuery(
    { classId: selectedClassId! },
    { enabled: !!selectedClassId }
  );

  // 获取考试详细数据（学生、题目、成绩）
  const { data: examDetails, isLoading: loadingDetails } = trpc.scores.byExamWithDetails.useQuery(
    { examId: selectedExamId! },
    { enabled: !!selectedExamId }
  );

  // 创建考试
  const createExamMutation = trpc.exams.create.useMutation({
    onSuccess: (data) => {
      if (data.id) {
        setSelectedExamId(data.id);
        utils.exams.byClass.invalidate({ classId: selectedClassId! });
        toast.success("考试创建成功");
      }
    },
    onError: (error) => {
      toast.error(`创建考试失败: ${error.message}`);
    },
  });

  // 保存单个分数
  const upsertScoreMutation = trpc.scores.upsert.useMutation({
    onSuccess: () => {
      utils.scores.byExamWithDetails.invalidate({ examId: selectedExamId! });
    },
    onError: (error) => {
      toast.error(`保存失败: ${error.message}`);
    },
  });

  // 根据选中的模板过滤考试
  const filteredExams = useMemo(() => {
    if (!selectedTemplateId) return exams;
    return exams.filter(exam => exam.examTemplateId === selectedTemplateId);
  }, [exams, selectedTemplateId]);

  // 构建分数映射
  const scoreMap = useMemo(() => {
    if (!examDetails) return {};
    const map: Record<string, number> = {};
    examDetails.scores.forEach(score => {
      const key = `${score.studentId}-${score.questionId}`;
      map[key] = parseFloat(score.score);
    });
    return map;
  }, [examDetails]);

  // 初始化分数状态
  useEffect(() => {
    setScores(scoreMap);
  }, [scoreMap]);

  // 计算学生总分
  const calculateStudentTotal = (studentId: number) => {
    if (!examDetails) return 0;
    let total = 0;
    examDetails.questions.forEach(question => {
      const key = `${studentId}-${question.id}`;
      const score = scores[key] ?? scoreMap[key] ?? 0;
      total += score;
    });
    return total;
  };

  // 处理分数输入
  const handleScoreChange = async (studentId: number, questionId: number, value: string) => {
    const key = `${studentId}-${questionId}`;
    const numValue = value === "" ? 0 : parseFloat(value);

    if (isNaN(numValue)) return;

    // 查找题目满分
    const question = examDetails?.questions.find(q => q.id === questionId);
    const maxScore = question ? parseFloat(question.score) : 0;

    if (numValue > maxScore) {
      toast.error(`分数不能超过满分 ${maxScore}`);
      return;
    }

    if (numValue < 0) {
      toast.error("分数不能为负数");
      return;
    }

    // 更新本地状态
    setScores(prev => ({ ...prev, [key]: numValue }));

    // 标记为保存中
    setSavingScores(prev => new Set(prev).add(key));

    // 自动保存到服务器
    try {
      await upsertScoreMutation.mutateAsync({
        examId: selectedExamId!,
        studentId,
        questionId,
        score: numValue,
      });
      
      // 移除保存中标记
      setSavingScores(prev => {
        const newSet = new Set(prev);
        newSet.delete(key);
        return newSet;
      });
    } catch (error) {
      // 恢复原值
      setScores(prev => ({ ...prev, [key]: scoreMap[key] ?? 0 }));
      setSavingScores(prev => {
        const newSet = new Set(prev);
        newSet.delete(key);
        return newSet;
      });
    }
  };

  // 创建新考试
  const handleCreateExam = () => {
    if (!selectedClassId || !selectedTemplateId || !examName) {
      toast.error("请填写完整的考试信息");
      return;
    }

    createExamMutation.mutate({
      examTemplateId: selectedTemplateId,
      classId: selectedClassId,
      examDate: new Date(examDate),
      name: examName,
      status: "draft",
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">成绩录入</h1>
          <p className="text-muted-foreground mt-2">为学生录入考试成绩，支持实时保存</p>
        </div>

        {/* 选择器区域 */}
        <Card>
          <CardHeader>
            <CardTitle>选择考试</CardTitle>
            <CardDescription>请先选择班级和试卷模板，然后选择或创建考试</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* 班级选择 */}
              <div className="space-y-2">
                <label className="text-sm font-medium">班级</label>
                <Select
                  value={selectedClassId?.toString() || ""}
                  onValueChange={(value) => {
                    setSelectedClassId(parseInt(value));
                    setSelectedExamId(null);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择班级" />
                  </SelectTrigger>
                  <SelectContent>
                    {classes.map((cls) => (
                      <SelectItem key={cls.id} value={cls.id.toString()}>
                        {cls.fullName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* 试卷模板选择 */}
              <div className="space-y-2">
                <label className="text-sm font-medium">试卷模板</label>
                <Select
                  value={selectedTemplateId?.toString() || ""}
                  onValueChange={(value) => {
                    setSelectedTemplateId(parseInt(value));
                    setSelectedExamId(null);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择试卷模板" />
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id.toString()}>
                        {template.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* 考试选择或创建 */}
            {selectedClassId && selectedTemplateId && (
              <div className="space-y-4 pt-4 border-t">
                <div className="space-y-2">
                  <label className="text-sm font-medium">选择已有考试</label>
                  <Select
                    value={selectedExamId?.toString() || ""}
                    onValueChange={(value) => setSelectedExamId(parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="选择考试或创建新考试" />
                    </SelectTrigger>
                    <SelectContent>
                      {filteredExams.map((exam) => (
                        <SelectItem key={exam.id} value={exam.id.toString()}>
                          {exam.name} - {new Date(exam.examDate).toLocaleDateString()}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">或创建新考试</label>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    <Input
                      placeholder="考试名称"
                      value={examName}
                      onChange={(e) => setExamName(e.target.value)}
                    />
                    <Input
                      type="date"
                      value={examDate}
                      onChange={(e) => setExamDate(e.target.value)}
                    />
                    <Button
                      onClick={handleCreateExam}
                      disabled={createExamMutation.isPending || !examName}
                    >
                      {createExamMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      创建考试
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 成绩录入表格 */}
        {selectedExamId && (
          <Card>
            <CardHeader>
              <CardTitle>成绩录入表格</CardTitle>
              <CardDescription>输入分数后自动保存，总分实时计算</CardDescription>
            </CardHeader>
            <CardContent>
              {loadingDetails ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : examDetails && examDetails.students.length > 0 && examDetails.questions.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="p-3 text-left font-medium sticky left-0 bg-muted/50 z-10">学号</th>
                        <th className="p-3 text-left font-medium sticky left-20 bg-muted/50 z-10">姓名</th>
                        {examDetails.questions.map((question) => (
                          <th key={question.id} className="p-3 text-center font-medium min-w-[80px]">
                            <div className="text-xs">第{question.questionNumber}题</div>
                            <div className="text-xs text-muted-foreground">({parseFloat(question.score)}分)</div>
                          </th>
                        ))}
                        <th className="p-3 text-center font-medium bg-primary/10 min-w-[100px]">总分</th>
                      </tr>
                    </thead>
                    <tbody>
                      {examDetails.students.map((student) => {
                        const total = calculateStudentTotal(student.id);
                        return (
                          <tr key={student.id} className="border-b hover:bg-muted/30">
                            <td className="p-3 sticky left-0 bg-background">{student.studentNumber}</td>
                            <td className="p-3 sticky left-20 bg-background font-medium">{student.name}</td>
                            {examDetails.questions.map((question) => {
                              const key = `${student.id}-${question.id}`;
                              const isSaving = savingScores.has(key);
                              const currentScore = scores[key] ?? scoreMap[key] ?? "";
                              
                              return (
                                <td key={question.id} className="p-2">
                                  <div className="relative">
                                    <Input
                                      type="number"
                                      min="0"
                                      max={parseFloat(question.score)}
                                      step="0.5"
                                      value={currentScore}
                                      onChange={(e) => handleScoreChange(student.id, question.id, e.target.value)}
                                      className="text-center h-9"
                                      disabled={isSaving}
                                    />
                                    {isSaving && (
                                      <Loader2 className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
                                    )}
                                  </div>
                                </td>
                              );
                            })}
                            <td className="p-3 text-center font-bold bg-primary/5">
                              {total.toFixed(1)}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  {examDetails?.students.length === 0 ? "该班级暂无学生" : "该试卷暂无题目"}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {!selectedExamId && (
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-muted-foreground">
                <Save className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>请选择班级、试卷模板和考试后开始录入成绩</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
