import { useState } from "react";
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
import { Badge } from "@/components/ui/badge";
import { Plus, Pencil, Trash2, FileText } from "lucide-react";
import { toast } from "sonner";
import { useLocation } from "wouter";

type ExamSession = {
  id: number;
  name: string;
  schoolYear: string;
  semester: string;
  startDate: Date | null;
  endDate: Date | null;
  description: string | null;
  status: "draft" | "active" | "completed" | "archived";
  createdBy: number;
  createdAt: Date;
  updatedAt: Date;
};

type ExamSessionFormData = {
  name: string;
  schoolYear: string;
  semester: string;
  startDate: string;
  endDate: string;
  description: string;
  status: "draft" | "active" | "completed" | "archived";
};

const statusLabels = {
  draft: "草稿",
  active: "进行中",
  completed: "已完成",
  archived: "已归档",
};

const statusColors = {
  draft: "secondary",
  active: "default",
  completed: "outline",
  archived: "secondary",
} as const;

export default function ExamSessions() {
  const [, setLocation] = useLocation();
  const utils = trpc.useUtils();

  // 获取考试列表
  const { data: examSessions, isLoading } = trpc.examSessions.list.useQuery();

  // 对话框状态
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  // 表单数据
  const [addFormData, setAddFormData] = useState<ExamSessionFormData>({
    name: "",
    schoolYear: "",
    semester: "S1",
    startDate: "",
    endDate: "",
    description: "",
    status: "draft",
  });

  const [editFormData, setEditFormData] = useState<ExamSessionFormData>({
    name: "",
    schoolYear: "",
    semester: "S1",
    startDate: "",
    endDate: "",
    description: "",
    status: "draft",
  });

  const [selectedExamSession, setSelectedExamSession] = useState<ExamSession | null>(null);

  // 创建考试
  const createMutation = trpc.examSessions.create.useMutation({
    onSuccess: () => {
      toast.success("考试已创建");
      utils.examSessions.list.invalidate();
      setIsAddDialogOpen(false);
      resetAddForm();
    },
    onError: (error) => {
      toast.error("创建失败：" + error.message);
    },
  });

  // 更新考试
  const updateMutation = trpc.examSessions.update.useMutation({
    onSuccess: () => {
      toast.success("考试信息已更新");
      utils.examSessions.list.invalidate();
      setIsEditDialogOpen(false);
    },
    onError: (error) => {
      toast.error("更新失败：" + error.message);
    },
  });

  // 删除考试
  const deleteMutation = trpc.examSessions.delete.useMutation({
    onSuccess: () => {
      toast.success("考试已删除");
      utils.examSessions.list.invalidate();
      setIsDeleteDialogOpen(false);
    },
    onError: (error) => {
      toast.error("删除失败：" + error.message);
    },
  });

  const resetAddForm = () => {
    setAddFormData({
      name: "",
      schoolYear: "",
      semester: "S1",
      startDate: "",
      endDate: "",
      description: "",
      status: "draft",
    });
  };

  const handleAdd = () => {
    if (!addFormData.name || !addFormData.schoolYear || !addFormData.semester) {
      toast.error("请填写必填项：考试名称、学年和学期");
      return;
    }

    createMutation.mutate(addFormData);
  };

  const handleEdit = (examSession: ExamSession) => {
    setSelectedExamSession(examSession);
    setEditFormData({
      name: examSession.name,
      schoolYear: examSession.schoolYear,
      semester: examSession.semester,
      startDate: examSession.startDate ? new Date(examSession.startDate).toISOString().split("T")[0] : "",
      endDate: examSession.endDate ? new Date(examSession.endDate).toISOString().split("T")[0] : "",
      description: examSession.description || "",
      status: examSession.status,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdate = () => {
    if (!selectedExamSession) return;

    if (!editFormData.name || !editFormData.schoolYear || !editFormData.semester) {
      toast.error("请填写必填项：考试名称、学年和学期");
      return;
    }

    updateMutation.mutate({
      id: selectedExamSession.id,
      data: {
        name: editFormData.name,
        schoolYear: editFormData.schoolYear,
        semester: editFormData.semester,
        startDate: editFormData.startDate || null,
        endDate: editFormData.endDate || null,
        description: editFormData.description || null,
        status: editFormData.status,
      },
    });
  };

  const handleDelete = (examSession: ExamSession) => {
    setSelectedExamSession(examSession);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (!selectedExamSession) return;
    deleteMutation.mutate({ id: selectedExamSession.id });
  };

  const handleViewExams = (examSessionId: number) => {
    setLocation(`/exam-templates?examSessionId=${examSessionId}`);
  };

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
        <div>
          <h1 className="text-3xl font-bold tracking-tight">考试管理</h1>
          <p className="text-muted-foreground mt-1">
            管理考试信息和试卷
          </p>
        </div>
        <Button onClick={() => setIsAddDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          创建考试
        </Button>
      </div>

      {/* 考试列表 */}
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>考试名称</TableHead>
              <TableHead>学年</TableHead>
              <TableHead>学期</TableHead>
              <TableHead>开始日期</TableHead>
              <TableHead>结束日期</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>创建时间</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {examSessions && examSessions.length > 0 ? (
              examSessions.map((examSession) => (
                <TableRow key={examSession.id}>
                  <TableCell className="font-medium">{examSession.name}</TableCell>
                  <TableCell>{examSession.schoolYear}</TableCell>
                  <TableCell>{examSession.semester}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {examSession.startDate
                      ? new Date(examSession.startDate).toLocaleDateString("zh-CN")
                      : <span className="italic">未设置</span>}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {examSession.endDate
                      ? new Date(examSession.endDate).toLocaleDateString("zh-CN")
                      : <span className="italic">未设置</span>}
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusColors[examSession.status]}>
                      {statusLabels[examSession.status]}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(examSession.createdAt).toLocaleDateString("zh-CN")}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewExams(examSession.id)}
                        title="查看试卷"
                      >
                        <FileText className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(examSession)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(examSession)}
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
                  暂无考试数据
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* 添加考试对话框 */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>创建考试</DialogTitle>
            <DialogDescription>填写考试的基本信息</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">
                考试名称 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                value={addFormData.name}
                onChange={(e) =>
                  setAddFormData({ ...addFormData, name: e.target.value })
                }
                placeholder="如：2025-2026学年Way To Future考试 S2"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="schoolYear">
                  学年 <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="schoolYear"
                  value={addFormData.schoolYear}
                  onChange={(e) =>
                    setAddFormData({ ...addFormData, schoolYear: e.target.value })
                  }
                  placeholder="如：2025-2026"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="semester">
                  学期 <span className="text-destructive">*</span>
                </Label>
                <Select
                  value={addFormData.semester}
                  onValueChange={(value) =>
                    setAddFormData({ ...addFormData, semester: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="S1">第一学期 (S1)</SelectItem>
                    <SelectItem value="S2">第二学期 (S2)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startDate">开始日期</Label>
                <Input
                  id="startDate"
                  type="date"
                  value={addFormData.startDate}
                  onChange={(e) =>
                    setAddFormData({ ...addFormData, startDate: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="endDate">结束日期</Label>
                <Input
                  id="endDate"
                  type="date"
                  value={addFormData.endDate}
                  onChange={(e) =>
                    setAddFormData({ ...addFormData, endDate: e.target.value })
                  }
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="status">状态</Label>
              <Select
                value={addFormData.status}
                onValueChange={(value: any) =>
                  setAddFormData({ ...addFormData, status: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">草稿</SelectItem>
                  <SelectItem value="active">进行中</SelectItem>
                  <SelectItem value="completed">已完成</SelectItem>
                  <SelectItem value="archived">已归档</SelectItem>
                </SelectContent>
              </Select>
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

      {/* 编辑考试对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>编辑考试</DialogTitle>
            <DialogDescription>
              修改考试信息
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">
                考试名称 <span className="text-destructive">*</span>
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
                <Label htmlFor="edit-schoolYear">
                  学年 <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="edit-schoolYear"
                  value={editFormData.schoolYear}
                  onChange={(e) =>
                    setEditFormData({ ...editFormData, schoolYear: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-semester">
                  学期 <span className="text-destructive">*</span>
                </Label>
                <Select
                  value={editFormData.semester}
                  onValueChange={(value) =>
                    setEditFormData({ ...editFormData, semester: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="S1">第一学期 (S1)</SelectItem>
                    <SelectItem value="S2">第二学期 (S2)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-startDate">开始日期</Label>
                <Input
                  id="edit-startDate"
                  type="date"
                  value={editFormData.startDate}
                  onChange={(e) =>
                    setEditFormData({ ...editFormData, startDate: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-endDate">结束日期</Label>
                <Input
                  id="edit-endDate"
                  type="date"
                  value={editFormData.endDate}
                  onChange={(e) =>
                    setEditFormData({ ...editFormData, endDate: e.target.value })
                  }
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-status">状态</Label>
              <Select
                value={editFormData.status}
                onValueChange={(value: any) =>
                  setEditFormData({ ...editFormData, status: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">草稿</SelectItem>
                  <SelectItem value="active">进行中</SelectItem>
                  <SelectItem value="completed">已完成</SelectItem>
                  <SelectItem value="archived">已归档</SelectItem>
                </SelectContent>
              </Select>
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

      {/* 删除确认对话框 */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除考试 "{selectedExamSession?.name}" 吗？此操作将同时删除该考试下的所有试卷，且无法撤销。
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
