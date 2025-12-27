import { useRoute } from "wouter";
import { trpc } from "@/lib/trpc";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2, Plus, Pencil, Trash2 } from "lucide-react";
import { Link } from "wouter";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

type QuestionFormData = {
  questionNumber: string;
  module: string;
  knowledgePoint: string;
  questionType: string;
  score: string;
};

export default function ExamTemplateDetail() {
  const [, params] = useRoute("/exam-templates/:id");
  const templateId = params?.id ? parseInt(params.id) : null;

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<any>(null);
  const [deletingQuestionId, setDeletingQuestionId] = useState<number | null>(null);

  const [formData, setFormData] = useState<QuestionFormData>({
    questionNumber: "",
    module: "",
    knowledgePoint: "",
    questionType: "",
    score: "",
  });

  const utils = trpc.useUtils();

  const { data: template, isLoading: loadingTemplate } = trpc.examTemplates.getById.useQuery(
    { id: templateId! },
    { enabled: !!templateId }
  );

  const { data: questions = [], isLoading: loadingQuestions } = trpc.questions.byExamTemplate.useQuery(
    { examTemplateId: templateId! },
    { enabled: !!templateId }
  );

  const { data: subjects = [] } = trpc.subjects.list.useQuery();
  const { data: grades = [] } = trpc.grades.list.useQuery();

  const createQuestion = trpc.questions.create.useMutation({
    onSuccess: () => {
      utils.questions.byExamTemplate.invalidate({ examTemplateId: templateId! });
      toast.success("题目添加成功");
      setIsAddDialogOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error(`添加失败: ${error.message}`);
    },
  });

  const updateQuestion = trpc.questions.update.useMutation({
    onSuccess: () => {
      utils.questions.byExamTemplate.invalidate({ examTemplateId: templateId! });
      toast.success("题目更新成功");
      setIsEditDialogOpen(false);
      setEditingQuestion(null);
    },
    onError: (error) => {
      toast.error(`更新失败: ${error.message}`);
    },
  });

  const deleteQuestion = trpc.questions.delete.useMutation({
    onSuccess: () => {
      utils.questions.byExamTemplate.invalidate({ examTemplateId: templateId! });
      toast.success("题目删除成功");
      setIsDeleteDialogOpen(false);
      setDeletingQuestionId(null);
    },
    onError: (error) => {
      toast.error(`删除失败: ${error.message}`);
    },
  });

  const subject = subjects.find((s: any) => s.id === template?.subjectId);
  const grade = grades.find((g: any) => g.id === template?.gradeId);

  // 按模块分组题目
  const questionsByModule = questions.reduce((acc: Record<string, any[]>, question: any) => {
    const module = question.module || "未分类";
    if (!acc[module]) {
      acc[module] = [];
    }
    acc[module].push(question);
    return acc;
  }, {});

  const modules = Object.keys(questionsByModule);

  const resetForm = () => {
    setFormData({
      questionNumber: "",
      module: "",
      knowledgePoint: "",
      questionType: "",
      score: "",
    });
  };

  const handleAdd = () => {
    if (!formData.questionNumber || !formData.score) {
      toast.error("请填写题号和分值");
      return;
    }

    const nextSortOrder = questions.length > 0 
      ? Math.max(...questions.map((q: any) => q.sortOrder || 0)) + 1 
      : 1;

    createQuestion.mutate({
      examTemplateId: templateId!,
      questionNumber: parseInt(formData.questionNumber),
      module: formData.module || null,
      knowledgePoint: formData.knowledgePoint || null,
      questionType: formData.questionType || null,
      score: parseFloat(formData.score),
      sortOrder: nextSortOrder,
    });
  };

  const handleEdit = (question: any) => {
    setEditingQuestion(question);
    setFormData({
      questionNumber: question.questionNumber.toString(),
      module: question.module || "",
      knowledgePoint: question.knowledgePoint || "",
      questionType: question.questionType || "",
      score: question.score.toString(),
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdate = () => {
    if (!formData.questionNumber || !formData.score) {
      toast.error("请填写题号和分值");
      return;
    }

    updateQuestion.mutate({
      id: editingQuestion.id,
      data: {
        questionNumber: parseInt(formData.questionNumber),
        module: formData.module || null,
        knowledgePoint: formData.knowledgePoint || null,
        questionType: formData.questionType || null,
        score: parseFloat(formData.score),
      },
    });
  };

  const handleDelete = (questionId: number) => {
    setDeletingQuestionId(questionId);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (deletingQuestionId) {
      deleteQuestion.mutate({ id: deletingQuestionId });
    }
  };

  if (loadingTemplate || loadingQuestions) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </DashboardLayout>
    );
  }

  if (!template) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-muted-foreground">
                <p>试卷模板不存在</p>
                <Link href="/exam-templates">
                  <Button variant="link" className="mt-4">
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    返回试卷模板列表
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* 页头 */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Link href="/exam-templates">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4" />
                </Button>
              </Link>
              <h1 className="text-3xl font-bold tracking-tight">{template.name}</h1>
            </div>
            <p className="text-muted-foreground">查看和管理试卷模板的题目</p>
          </div>
          <Button onClick={() => {
            resetForm();
            setIsAddDialogOpen(true);
          }}>
            <Plus className="mr-2 h-4 w-4" />
            添加题目
          </Button>
        </div>

        {/* 基本信息 */}
        <Card>
          <CardHeader>
            <CardTitle>基本信息</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-muted-foreground mb-1">科目</div>
                <div className="font-medium">{subject?.name || '-'}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground mb-1">年级</div>
                <div className="font-medium">{grade?.displayName || '-'}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground mb-1">总分</div>
                <div className="font-medium">{parseFloat(template.totalScore)}分</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground mb-1">题目数量</div>
                <div className="font-medium">{questions.length}题</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 题目列表 - 按模块分组 */}
        {modules.length > 0 ? (
          modules.map(moduleName => {
            const moduleQuestions = questionsByModule[moduleName];
            const moduleTotal = moduleQuestions.reduce((sum: number, q: any) => sum + parseFloat(q.score), 0);
            
            return (
              <Card key={moduleName}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>{moduleName}</CardTitle>
                    <div className="text-sm text-muted-foreground">
                      {moduleQuestions.length}题 · 共{moduleTotal.toFixed(1)}分
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr className="border-b bg-muted/50">
                          <th className="p-3 text-left font-medium w-20">题号</th>
                          <th className="p-3 text-left font-medium">知识点</th>
                          <th className="p-3 text-left font-medium w-32">题型</th>
                          <th className="p-3 text-center font-medium w-20">分值</th>
                          <th className="p-3 text-center font-medium w-32">操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        {moduleQuestions.map((question: any) => (
                          <tr key={question.id} className="border-b hover:bg-muted/30">
                            <td className="p-3 font-medium">第{question.questionNumber}题</td>
                            <td className="p-3">
                              {question.knowledgePoint || (
                                <span className="text-muted-foreground italic">未填写</span>
                              )}
                            </td>
                            <td className="p-3">
                              {question.questionType || (
                                <span className="text-muted-foreground italic">未填写</span>
                              )}
                            </td>
                            <td className="p-3 text-center font-medium">
                              {parseFloat(question.score)}分
                            </td>
                            <td className="p-3 text-center">
                              <div className="flex items-center justify-center gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleEdit(question)}
                                >
                                  <Pencil className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleDelete(question.id)}
                                >
                                  <Trash2 className="h-4 w-4 text-destructive" />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot>
                        <tr className="border-t-2 bg-muted/30">
                          <td className="p-3 font-bold" colSpan={3}>小计</td>
                          <td className="p-3 text-center font-bold">{moduleTotal.toFixed(1)}分</td>
                          <td></td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </CardContent>
              </Card>
            );
          })
        ) : (
          <Card>
            <CardContent className="py-12">
              <div className="text-center text-muted-foreground">
                <p className="mb-4">该试卷模板暂无题目</p>
                <Button onClick={() => {
                  resetForm();
                  setIsAddDialogOpen(true);
                }}>
                  <Plus className="mr-2 h-4 w-4" />
                  添加第一道题目
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* 添加题目对话框 */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>添加题目</DialogTitle>
            <DialogDescription>为试卷模板添加新题目</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="questionNumber">题号 *</Label>
              <Input
                id="questionNumber"
                type="number"
                value={formData.questionNumber}
                onChange={(e) => setFormData({ ...formData, questionNumber: e.target.value })}
                placeholder="例如: 1"
              />
            </div>
            <div>
              <Label htmlFor="module">模块</Label>
              <Input
                id="module"
                value={formData.module}
                onChange={(e) => setFormData({ ...formData, module: e.target.value })}
                placeholder="例如: 基础计算"
              />
            </div>
            <div>
              <Label htmlFor="knowledgePoint">知识点</Label>
              <Input
                id="knowledgePoint"
                value={formData.knowledgePoint}
                onChange={(e) => setFormData({ ...formData, knowledgePoint: e.target.value })}
                placeholder="例如: 20以内加减法"
              />
            </div>
            <div>
              <Label htmlFor="questionType">题型</Label>
              <Input
                id="questionType"
                value={formData.questionType}
                onChange={(e) => setFormData({ ...formData, questionType: e.target.value })}
                placeholder="例如: 选择题"
              />
            </div>
            <div>
              <Label htmlFor="score">分值 *</Label>
              <Input
                id="score"
                type="number"
                step="0.5"
                value={formData.score}
                onChange={(e) => setFormData({ ...formData, score: e.target.value })}
                placeholder="例如: 5"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleAdd} disabled={createQuestion.isPending}>
              {createQuestion.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              添加
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑题目对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>编辑题目</DialogTitle>
            <DialogDescription>修改题目信息</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-questionNumber">题号 *</Label>
              <Input
                id="edit-questionNumber"
                type="number"
                value={formData.questionNumber}
                onChange={(e) => setFormData({ ...formData, questionNumber: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-module">模块</Label>
              <Input
                id="edit-module"
                value={formData.module}
                onChange={(e) => setFormData({ ...formData, module: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-knowledgePoint">知识点</Label>
              <Input
                id="edit-knowledgePoint"
                value={formData.knowledgePoint}
                onChange={(e) => setFormData({ ...formData, knowledgePoint: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-questionType">题型</Label>
              <Input
                id="edit-questionType"
                value={formData.questionType}
                onChange={(e) => setFormData({ ...formData, questionType: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-score">分值 *</Label>
              <Input
                id="edit-score"
                type="number"
                step="0.5"
                value={formData.score}
                onChange={(e) => setFormData({ ...formData, score: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleUpdate} disabled={updateQuestion.isPending}>
              {updateQuestion.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除确认对话框 */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除这道题目吗？此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} disabled={deleteQuestion.isPending}>
              {deleteQuestion.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </DashboardLayout>
  );
}
