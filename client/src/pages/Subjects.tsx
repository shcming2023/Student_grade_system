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
import { Textarea } from "@/components/ui/textarea";
import { trpc } from "@/lib/trpc";
import { Plus, Pencil, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

const CATEGORIES = [
  { value: "english", label: "英语" },
  { value: "math", label: "数学" },
  { value: "chinese", label: "语文" },
  { value: "other", label: "其他" },
];

export default function Subjects() {
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    code: "",
    category: "other",
    description: "",
  });

  const utils = trpc.useUtils();
  const { data: subjects, isLoading } = trpc.subjects.list.useQuery();
  const createMutation = trpc.subjects.create.useMutation({
    onSuccess: () => {
      utils.subjects.list.invalidate();
      toast.success("科目添加成功");
      setOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error("添加失败：" + error.message);
    },
  });
  const updateMutation = trpc.subjects.update.useMutation({
    onSuccess: () => {
      utils.subjects.list.invalidate();
      toast.success("科目信息更新成功");
      setOpen(false);
      resetForm();
    },
    onError: (error) => {
      toast.error("更新失败：" + error.message);
    },
  });
  const deleteMutation = trpc.subjects.delete.useMutation({
    onSuccess: () => {
      utils.subjects.list.invalidate();
      toast.success("科目删除成功");
    },
    onError: (error) => {
      toast.error("删除失败：" + error.message);
    },
  });

  const resetForm = () => {
    setFormData({
      name: "",
      code: "",
      category: "other",
      description: "",
    });
    setEditingId(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.code) {
      toast.error("请填写所有必填字段");
      return;
    }

    const data = {
      name: formData.name,
      code: formData.code,
      category: formData.category,
      description: formData.description || null,
    };

    if (editingId) {
      updateMutation.mutate({ id: editingId, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (subject: any) => {
    setEditingId(subject.id);
    setFormData({
      name: subject.name,
      code: subject.code,
      category: subject.category || "other",
      description: subject.description || "",
    });
    setOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm("确定要删除这个科目吗？")) {
      deleteMutation.mutate({ id });
    }
  };

  const getCategoryLabel = (category: string) => {
    return CATEGORIES.find((c) => c.value === category)?.label || category;
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">科目管理</h1>
            <p className="text-muted-foreground mt-2">管理科目信息和科目配置</p>
          </div>
          <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) resetForm(); }}>
            <DialogTrigger asChild>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                添加科目
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingId ? "编辑科目" : "添加科目"}</DialogTitle>
                <DialogDescription>填写科目基本信息</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">科目名称 *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="例如：朗文英语"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="code">科目代码 *</Label>
                    <Input
                      id="code"
                      value={formData.code}
                      onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                      placeholder="例如：longman_english"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="category">科目分类</Label>
                    <Select value={formData.category} onValueChange={(value) => setFormData({ ...formData, category: value })}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CATEGORIES.map((cat) => (
                          <SelectItem key={cat.value} value={cat.value}>
                            {cat.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">科目描述</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="科目的详细描述"
                      rows={3}
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
            <CardTitle>科目列表</CardTitle>
            <CardDescription>共 {subjects?.length || 0} 个科目</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">加载中...</div>
            ) : subjects && subjects.length > 0 ? (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>科目名称</TableHead>
                      <TableHead>科目代码</TableHead>
                      <TableHead>分类</TableHead>
                      <TableHead>描述</TableHead>
                      <TableHead className="text-right">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {subjects.map((subject) => (
                      <TableRow key={subject.id}>
                        <TableCell className="font-medium">{subject.name}</TableCell>
                        <TableCell>{subject.code}</TableCell>
                        <TableCell>{getCategoryLabel(subject.category || "other")}</TableCell>
                        <TableCell className="max-w-xs truncate">{subject.description || "-"}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEdit(subject)}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(subject.id)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                暂无科目数据，请添加科目
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
