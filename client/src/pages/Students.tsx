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
import { Plus, Pencil, Trash2, Search } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function Students() {
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [formData, setFormData] = useState({
    studentNumber: "",
    name: "",
    classId: "",
    gender: "male" as "male" | "female",
    parentContact: "",
  });

  const utils = trpc.useUtils();
  const { data: students, isLoading } = trpc.students.list.useQuery();
  const { data: classes } = trpc.classes.list.useQuery();
  const createMutation = trpc.students.create.useMutation({
    onSuccess: () => {
      utils.students.list.invalidate();
      toast.success("学生添加成功");
      setOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error("添加失败：" + error.message);
    },
  });
  const updateMutation = trpc.students.update.useMutation({
    onSuccess: () => {
      utils.students.list.invalidate();
      toast.success("学生信息更新成功");
      setOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error("更新失败：" + error.message);
    },
  });
  const deleteMutation = trpc.students.delete.useMutation({
    onSuccess: () => {
      utils.students.list.invalidate();
      toast.success("学生删除成功");
    },
    onError: (error) => {
      toast.error("删除失败：" + error.message);
    },
  });

  const resetForm = () => {
    setFormData({
      studentNumber: "",
      name: "",
      classId: "",
      gender: "male",
      parentContact: "",
    });
    setEditingId(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.studentNumber || !formData.name || !formData.classId) {
      toast.error("请填写必填字段");
      return;
    }

    const data = {
      studentNumber: formData.studentNumber,
      name: formData.name,
      classId: parseInt(formData.classId),
      gender: formData.gender,
      parentContact: formData.parentContact || null,
      status: "active" as const,
    };

    if (editingId) {
      updateMutation.mutate({ id: editingId, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (student: any) => {
    setEditingId(student.id);
    setFormData({
      studentNumber: student.studentNumber,
      name: student.name,
      classId: student.classId.toString(),
      gender: student.gender || "male",
      parentContact: student.parentContact || "",
    });
    setOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm("确定要删除这个学生吗？")) {
      deleteMutation.mutate({ id });
    }
  };

  const filteredStudents = students?.filter(
    (student) =>
      student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      student.studentNumber.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">学生管理</h1>
            <p className="text-muted-foreground mt-2">管理学生基本信息和班级分配</p>
          </div>
          <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) resetForm(); }}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                添加学生
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingId ? "编辑学生" : "添加学生"}</DialogTitle>
                <DialogDescription>填写学生基本信息</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="studentNumber">学号 *</Label>
                    <Input
                      id="studentNumber"
                      value={formData.studentNumber}
                      onChange={(e) => setFormData({ ...formData, studentNumber: e.target.value })}
                      placeholder="请输入学号"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="name">姓名 *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="请输入姓名"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="classId">班级 *</Label>
                    <Select value={formData.classId} onValueChange={(value) => setFormData({ ...formData, classId: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择班级" />
                      </SelectTrigger>
                      <SelectContent>
                        {classes?.map((cls) => (
                          <SelectItem key={cls.id} value={cls.id.toString()}>
                            {cls.fullName}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="gender">性别</Label>
                    <Select value={formData.gender} onValueChange={(value: "male" | "female") => setFormData({ ...formData, gender: value })}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">男</SelectItem>
                        <SelectItem value="female">女</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="parentContact">家长联系方式</Label>
                    <Input
                      id="parentContact"
                      value={formData.parentContact}
                      onChange={(e) => setFormData({ ...formData, parentContact: e.target.value })}
                      placeholder="请输入联系方式"
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
            <CardTitle>学生列表</CardTitle>
            <CardDescription>共 {students?.length || 0} 名学生</CardDescription>
            <div className="pt-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="搜索学生姓名或学号..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">加载中...</div>
            ) : filteredStudents && filteredStudents.length > 0 ? (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>学号</TableHead>
                      <TableHead>姓名</TableHead>
                      <TableHead>班级</TableHead>
                      <TableHead>性别</TableHead>
                      <TableHead>家长联系方式</TableHead>
                      <TableHead className="text-right">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredStudents.map((student) => {
                      const studentClass = classes?.find((c) => c.id === student.classId);
                      return (
                        <TableRow key={student.id}>
                          <TableCell className="font-medium">{student.studentNumber}</TableCell>
                          <TableCell>{student.name}</TableCell>
                          <TableCell>{studentClass?.fullName || "-"}</TableCell>
                          <TableCell>{student.gender === "male" ? "男" : "女"}</TableCell>
                          <TableCell>{student.parentContact || "-"}</TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleEdit(student)}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDelete(student.id)}
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
                {searchTerm ? "未找到匹配的学生" : "暂无学生数据，请添加学生"}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
