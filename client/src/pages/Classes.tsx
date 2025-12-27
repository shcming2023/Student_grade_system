import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { Plus, Pencil, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function Classes() {
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    gradeId: "",
    name: "",
    fullName: "",
  });

  const utils = trpc.useUtils();
  const { data: classes, isLoading } = trpc.classes.list.useQuery();
  const { data: grades } = trpc.grades.list.useQuery();
  const createMutation = trpc.classes.create.useMutation({
    onSuccess: () => {
      utils.classes.list.invalidate();
      toast.success("班级添加成功");
      setOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error("添加失败：" + error.message);
    },
  });
  const updateMutation = trpc.classes.update.useMutation({
    onSuccess: () => {
      utils.classes.list.invalidate();
      toast.success("班级信息更新成功");
      setOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error("更新失败：" + error.message);
    },
  });
  const deleteMutation = trpc.classes.delete.useMutation({
    onSuccess: () => {
      utils.classes.list.invalidate();
      toast.success("班级删除成功");
    },
    onError: (error) => {
      toast.error("删除失败：" + error.message);
    },
  });

  const resetForm = () => {
    setFormData({
      gradeId: "",
      name: "",
      fullName: "",
    });
    setEditingId(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.gradeId || !formData.name || !formData.fullName) {
      toast.error("请填写所有必填字段");
      return;
    }

    const data = {
      gradeId: parseInt(formData.gradeId),
      name: formData.name,
      fullName: formData.fullName,
      teacherId: null,
    };

    if (editingId) {
      updateMutation.mutate({ id: editingId, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (classItem: any) => {
    setEditingId(classItem.id);
    setFormData({
      gradeId: classItem.gradeId.toString(),
      name: classItem.name,
      fullName: classItem.fullName,
    });
    setOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm("确定要删除这个班级吗？")) {
      deleteMutation.mutate({ id });
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">班级管理</h1>
            <p className="text-muted-foreground mt-2">管理班级信息和班级配置</p>
          </div>
          <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) resetForm(); }}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                添加班级
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingId ? "编辑班级" : "添加班级"}</DialogTitle>
                <DialogDescription>填写班级基本信息</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="gradeId">年级 *</Label>
                    <Select value={formData.gradeId} onValueChange={(value) => setFormData({ ...formData, gradeId: value })}>
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
                  <div className="space-y-2">
                    <Label htmlFor="name">班级名称 *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="例如：1班"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="fullName">完整名称 *</Label>
                    <Input
                      id="fullName"
                      value={formData.fullName}
                      onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                      placeholder="例如：G1-1班"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                    {editingId ? "更新" : "添加"}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>班级列表</CardTitle>
            <CardDescription>共 {classes?.length || 0} 个班级</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">加载中...</div>
            ) : classes && classes.length > 0 ? (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>完整名称</TableHead>
                      <TableHead>年级</TableHead>
                      <TableHead>班级名称</TableHead>
                      <TableHead className="text-right">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {classes.map((classItem) => {
                      const grade = grades?.find((g) => g.id === classItem.gradeId);
                      return (
                        <TableRow key={classItem.id}>
                          <TableCell className="font-medium">{classItem.fullName}</TableCell>
                          <TableCell>{grade?.displayName || "-"}</TableCell>
                          <TableCell>{classItem.name}</TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleEdit(classItem)}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDelete(classItem.id)}
                              >
                                <Trash2 className="h-4 w-4 text-destructive" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                暂无班级数据，请添加班级
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
