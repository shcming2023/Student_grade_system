import { useState, useEffect } from "react";
import { trpc } from "@/lib/trpc";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Pencil, Trash2, ArrowLeft, Link, Eye } from "lucide-react";
import { toast } from "sonner";
import { useLocation } from "wouter";

type ExamTemplate = {
  id: number;
  examSessionId: number;
  name: string;
  subjectId: number;
  gradeId: number;
  totalScore: string;
  description: string | null;
  creatorId: number | null;
  graderId: number | null;
  createdBy: number;
  createdAt: Date;
  updatedAt: Date;
};

type ExamTemplateFormData = {
  examSessionId: string;
  name: string;
  subjectId: string;
  gradeId: string;
  totalScore: string;
  description: string;
  creatorId: string;
  graderId: string;
};

export default function ExamTemplates() {
  const [location, setLocation] = useLocation();
  const utils = trpc.useUtils();

  // 从URL参数获取examSessionId
  const urlParams = new URLSearchParams(window.location.search);
  const examSessionIdParam = urlParams.get("examSessionId");
  const examSessionId = examSessionIdParam ? parseInt(examSessionIdParam) : null;

  // 获取考试信息
  const { data: examSession } = trpc.examSessions.getById.useQuery(
    { id: examSessionId! },
    { enabled: !!examSessionId }
  );

  // 获取试卷列表
  const { data: examTemplates, isLoading } = trpc.examTemplates.byExamSession.useQuery(
    { examSessionId: examSessionId! },
    { enabled: !!examSessionId }
  );

  // 获取未关联的试卷（试卷库）
  const { data: unassignedTemplates } = trpc.examTemplates.unassigned.useQuery();

  // 获取科目、年级和教师列表
  const { data: subjects } = trpc.subjects.list.useQuery();
  const { data: grades } = trpc.grades.list.useQuery();
  const { data: teachers } = trpc.teachers.list.useQuery();

  // 对话框状态
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isAssignDialogOpen, setIsAssignDialogOpen] = useState(false);

  // 表单数据
  const [addFormData, setAddFormData] = useState<ExamTemplateFormData>({
    examSessionId: examSessionId?.toString() || "",
    name: "",
    subjectId: "",
    gradeId: "",
    totalScore: "100",
    description: "",
    creatorId: "0",
    graderId: "0",
  });

  const [editFormData, setEditFormData] = useState<ExamTemplateFormData>({
    examSessionId: examSessionId?.toString() || "",
    name: "",
    subjectId: "",
    gradeId: "",
    totalScore: "100",
    description: "",
    creatorId: "0",
    graderId: "0",
  });

  const [selectedTemplate, setSelectedTemplate] = useState<ExamTemplate | null>(null);

  // 当examSessionId变化时更新表单
  useEffect(() => {
    if (examSessionId) {
      setAddFormData(prev => ({ ...prev, examSessionId: examSessionId.toString() }));
    }
  }, [examSessionId]);

  // 创建试卷
  const createMutation = trpc.examTemplates.create.useMutation({
    onSuccess: () => {
      toast.success("试卷已创建");
      utils.examTemplates.byExamSession.invalidate();
      setIsAddDialogOpen(false);
      resetAddForm();
    },
    onError: (error) => {
      toast.error("创建失败：" + error.message);
    },
  });

  // 更新试卷
  const updateMutation = trpc.examTemplates.update.useMutation({
    onSuccess: () => {
      toast.success("试卷信息已更新");
      utils.examTemplates.byExamSession.invalidate();
      setIsEditDialogOpen(false);
    },
    onError: (error) => {
      toast.error("更新失败：" + error.message);
    },
  });

  // 删除试卷
  const deleteMutation = trpc.examTemplates.delete.useMutation({
    onSuccess: () => {
      toast.success("试卷已删除");
      utils.examTemplates.byExamSession.invalidate();
      setIsDeleteDialogOpen(false);
    },
    onError: (error) => {
      toast.error("删除失败：" + error.message);
    },
  });

  // 关联试卷到考试
  const assignMutation = trpc.examTemplates.assignToExam.useMutation({
    onSuccess: () => {
      toast.success("试卷已关联到考试");
      utils.examTemplates.byExamSession.invalidate();
      utils.examTemplates.unassigned.invalidate();
      setIsAssignDialogOpen(false);
    },
    onError: (error) => {
      toast.error("关联失败：" + error.message);
    },
  });

  const resetAddForm = () => {
    setAddFormData({
      examSessionId: examSessionId?.toString() || "",
      name: "",
      subjectId: "",
      gradeId: "",
      totalScore: "100",
      description: "",
      creatorId: "0",
      graderId: "0",
    });
  };

  const handleAdd = () => {
    if (!addFormData.name || !addFormData.subjectId || !addFormData.gradeId) {
      toast.error("请填写必填项：试卷名称、科目和年级");
      return;
    }

    createMutation.mutate({
      examSessionId: parseInt(addFormData.examSessionId),
      name: addFormData.name,
      subjectId: parseInt(addFormData.subjectId),
      gradeId: parseInt(addFormData.gradeId),
      totalScore: parseFloat(addFormData.totalScore),
      description: addFormData.description || null,
        creatorId: addFormData.creatorId && addFormData.creatorId !== "0" ? parseInt(addFormData.creatorId) : null,
        graderId: addFormData.graderId && addFormData.graderId !== "0" ? parseInt(addFormData.graderId) : null,
    });
  };

  const handleEdit = (template: ExamTemplate) => {
    setSelectedTemplate(template);
    setEditFormData({
      examSessionId: template.examSessionId.toString(),
      name: template.name,
      subjectId: template.subjectId.toString(),
      gradeId: template.gradeId.toString(),
      totalScore: template.totalScore,
      description: template.description || "",
      creatorId: template.creatorId?.toString() || "0",
      graderId: template.graderId?.toString() || "0",
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdate = () => {
    if (!selectedTemplate) return;

    if (!editFormData.name || !editFormData.subjectId || !editFormData.gradeId) {
      toast.error("请填写必填项：试卷名称、科目和年级");
      return;
    }

    updateMutation.mutate({
      id: selectedTemplate.id,
      data: {
        name: editFormData.name,
        subjectId: parseInt(editFormData.subjectId),
        gradeId: parseInt(editFormData.gradeId),
        totalScore: parseFloat(editFormData.totalScore),
        description: editFormData.description || null,
        creatorId: editFormData.creatorId && editFormData.creatorId !== "0" ? parseInt(editFormData.creatorId) : null,
        graderId: editFormData.graderId && editFormData.graderId !== "0" ? parseInt(editFormData.graderId) : null,
      },
    });
  };

  const handleDelete = (template: ExamTemplate) => {
    setSelectedTemplate(template);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (!selectedTemplate) return;
    deleteMutation.mutate({ id: selectedTemplate.id });
  };

  const getSubjectName = (subjectId: number) => {
    return subjects?.find(s => s.id === subjectId)?.name || "-";
  };

  const getGradeName = (gradeId: number) => {
    return grades?.find(g => g.id === gradeId)?.displayName || "-";
  };

  const getTeacherName = (teacherId: number | null) => {
    if (!teacherId) return <span className="text-muted-foreground italic">未分配</span>;
    return teachers?.find(t => t.id === teacherId)?.name || "-";
  };

  if (!examSessionId) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <p className="text-muted-foreground">请从考试管理页面选择一个考试</p>
        <Button onClick={() => setLocation("/exam-sessions")}>
          前往考试管理
        </Button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-muted-foreground">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题和操作按钮 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setLocation("/exam-sessions")}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回考试列表
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">试卷管理</h1>
            <p className="text-muted-foreground mt-1">
              考试：{examSession?.name || "加载中..."}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setIsAssignDialogOpen(true)}>
            <Link className="mr-2 h-4 w-4" />
            关联试卷
          </Button>
          <Button onClick={() => setIsAddDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            创建试卷
          </Button>
        </div>
      </div>

      {/* 试卷列表 */}
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>试卷名称</TableHead>
              <TableHead>科目</TableHead>
              <TableHead>年级</TableHead>
              <TableHead>总分</TableHead>
              <TableHead>出卷老师</TableHead>
              <TableHead>阅卷老师</TableHead>
              <TableHead>创建时间</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {examTemplates && examTemplates.length > 0 ? (
              examTemplates.map((template) => (
                <TableRow key={template.id}>
                  <TableCell className="font-medium">{template.name}</TableCell>
                  <TableCell>{getSubjectName(template.subjectId)}</TableCell>
                  <TableCell>{getGradeName(template.gradeId)}</TableCell>
                  <TableCell>{template.totalScore}</TableCell>
                  <TableCell>{getTeacherName(template.creatorId)}</TableCell>
                  <TableCell>{getTeacherName(template.graderId)}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(template.createdAt).toLocaleDateString("zh-CN")}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setLocation(`/exam-templates/${template.id}`)}
                        title="查看题目"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(template)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(template)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  暂无试卷数据
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* 添加试卷对话框 */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>创建试卷</DialogTitle>
            <DialogDescription>填写试卷的基本信息</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">
                试卷名称 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                value={addFormData.name}
                onChange={(e) =>
                  setAddFormData({ ...addFormData, name: e.target.value })
                }
                placeholder="如：G1朗文英语"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="subject">
                  科目 <span className="text-destructive">*</span>
                </Label>
                <Select
                  value={addFormData.subjectId}
                  onValueChange={(value) =>
                    setAddFormData({ ...addFormData, subjectId: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择科目" />
                  </SelectTrigger>
                  <SelectContent>
                    {subjects?.map((subject) => (
                      <SelectItem key={subject.id} value={subject.id.toString()}>
                        {subject.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="grade">
                  年级 <span className="text-destructive">*</span>
                </Label>
                <Select
                  value={addFormData.gradeId}
                  onValueChange={(value) =>
                    setAddFormData({ ...addFormData, gradeId: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择年级" />
                  </SelectTrigger>
                  <SelectContent>
                    {grades?.map((grade) => (
                      <SelectItem key={grade.id} value={grade.id.toString()}>
                        {grade.displayName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="totalScore">
                总分 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="totalScore"
                type="number"
                value={addFormData.totalScore}
                onChange={(e) =>
                  setAddFormData({ ...addFormData, totalScore: e.target.value })
                }
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="creator">出卷老师</Label>
                <Select
                  value={addFormData.creatorId}
                  onValueChange={(value) =>
                    setAddFormData({ ...addFormData, creatorId: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择出卷老师（可选）" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">未分配</SelectItem>
                    {teachers?.map((teacher) => (
                      <SelectItem key={teacher.id} value={teacher.id.toString()}>
                        {teacher.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="grader">阅卷老师</Label>
                <Select
                  value={addFormData.graderId}
                  onValueChange={(value) =>
                    setAddFormData({ ...addFormData, graderId: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择阅卷老师（可选）" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">未分配</SelectItem>
                    {teachers?.map((teacher) => (
                      <SelectItem key={teacher.id} value={teacher.id.toString()}>
                        {teacher.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">描述</Label>
              <Textarea
                id="description"
                value={addFormData.description}
                onChange={(e) =>
                  setAddFormData({ ...addFormData, description: e.target.value })
                }
                placeholder="可选"
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsAddDialogOpen(false);
                resetAddForm();
              }}
            >
              取消
            </Button>
            <Button onClick={handleAdd} disabled={createMutation.isPending}>
              {createMutation.isPending ? "创建中..." : "创建"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑试卷对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>编辑试卷</DialogTitle>
            <DialogDescription>修改试卷信息和教师分配</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">
                试卷名称 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="edit-name"
                value={editFormData.name}
                onChange={(e) =>
                  setEditFormData({ ...editFormData, name: e.target.value })
                }
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-subject">
                  科目 <span className="text-destructive">*</span>
                </Label>
                <Select
                  value={editFormData.subjectId}
                  onValueChange={(value) =>
                    setEditFormData({ ...editFormData, subjectId: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {subjects?.map((subject) => (
                      <SelectItem key={subject.id} value={subject.id.toString()}>
                        {subject.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-grade">
                  年级 <span className="text-destructive">*</span>
                </Label>
                <Select
                  value={editFormData.gradeId}
                  onValueChange={(value) =>
                    setEditFormData({ ...editFormData, gradeId: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {grades?.map((grade) => (
                      <SelectItem key={grade.id} value={grade.id.toString()}>
                        {grade.displayName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-totalScore">
                总分 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="edit-totalScore"
                type="number"
                value={editFormData.totalScore}
                onChange={(e) =>
                  setEditFormData({ ...editFormData, totalScore: e.target.value })
                }
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-creator">出卷老师</Label>
                <Select
                  value={editFormData.creatorId}
                  onValueChange={(value) =>
                    setEditFormData({ ...editFormData, creatorId: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">未分配</SelectItem>
                    {teachers?.map((teacher) => (
                      <SelectItem key={teacher.id} value={teacher.id.toString()}>
                        {teacher.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-grader">阅卷老师</Label>
                <Select
                  value={editFormData.graderId}
                  onValueChange={(value) =>
                    setEditFormData({ ...editFormData, graderId: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">未分配</SelectItem>
                    {teachers?.map((teacher) => (
                      <SelectItem key={teacher.id} value={teacher.id.toString()}>
                        {teacher.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">描述</Label>
              <Textarea
                id="edit-description"
                value={editFormData.description}
                onChange={(e) =>
                  setEditFormData({ ...editFormData, description: e.target.value })
                }
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsEditDialogOpen(false)}
            >
              取消
            </Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? "更新中..." : "更新"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 关联试卷对话框 */}
      <Dialog open={isAssignDialogOpen} onOpenChange={setIsAssignDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>从试卷库关联试卷</DialogTitle>
            <DialogDescription>
              选择要关联到当前考试的试卷
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {!unassignedTemplates || unassignedTemplates.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                试卷库中暂无可用试卷
              </div>
            ) : (
              <div className="rounded-lg border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>试卷名称</TableHead>
                      <TableHead>科目</TableHead>
                      <TableHead>年级</TableHead>
                      <TableHead>总分</TableHead>
                      <TableHead className="text-right">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {unassignedTemplates.map((template) => {
                      const subject = subjects?.find((s) => s.id === template.subjectId);
                      const grade = grades?.find((g) => g.id === template.gradeId);
                      return (
                        <TableRow key={template.id}>
                          <TableCell className="font-medium">{template.name}</TableCell>
                          <TableCell>{subject?.name || "-"}</TableCell>
                          <TableCell>{grade?.name || "-"}</TableCell>
                          <TableCell>{template.totalScore}</TableCell>
                          <TableCell className="text-right">
                            <Button
                              size="sm"
                              onClick={() => {
                                if (examSessionId) {
                                  assignMutation.mutate({
                                    templateId: template.id,
                                    examSessionId: examSessionId,
                                  });
                                }
                              }}
                              disabled={assignMutation.isPending}
                            >
                              {assignMutation.isPending ? "关联中..." : "关联"}
                            </Button>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsAssignDialogOpen(false)}
            >
              关闭
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
              确定要删除试卷 "{selectedTemplate?.name}" 吗？此操作将同时删除该试卷的所有题目，且无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
