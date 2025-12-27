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
import { Badge } from "@/components/ui/badge";
import { UserPlus, Pencil, Trash2, Key, Shield, Users, GraduationCap } from "lucide-react";
import { toast } from "sonner";

type Teacher = {
  id: number;
  username: string;
  name: string;
  email: string | null;
  phone: string | null;
  role: "admin" | "teacher";
  status: "active" | "inactive";
  createdAt: Date;
};

type TeacherFormData = {
  username: string;
  password: string;
  name: string;
  email: string;
  phone: string;
  role: "admin" | "teacher";
};

type EditTeacherFormData = {
  name: string;
  email: string;
  phone: string;
  role: "admin" | "teacher";
  status: "active" | "inactive";
};

const roleLabels = {
  admin: "管理员",
  teacher: "普通教师",
};

const roleIcons = {
  admin: Shield,
  teacher: Users,
};

const statusLabels = {
  active: "启用",
  inactive: "停用",
};

export default function Teachers() {
  const utils = trpc.useUtils();

  // 获取教师列表
  const { data: teachers, isLoading } = trpc.teachers.list.useQuery();

  // 对话框状态
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isResetPasswordDialogOpen, setIsResetPasswordDialogOpen] = useState(false);

  // 表单数据
  const [addFormData, setAddFormData] = useState<TeacherFormData>({
    username: "",
    password: "",
    name: "",
    email: "",
    phone: "",
    role: "teacher",
  });

  const [editFormData, setEditFormData] = useState<EditTeacherFormData>({
    name: "",
    email: "",
    phone: "",
    role: "teacher",
    status: "active",
  });

  const [newPassword, setNewPassword] = useState("");
  const [selectedTeacher, setSelectedTeacher] = useState<Teacher | null>(null);

  // 创建教师
  const createMutation = trpc.teachers.create.useMutation({
    onSuccess: () => {
      toast.success("教师账户已创建");
      utils.teachers.list.invalidate();
      setIsAddDialogOpen(false);
      resetAddForm();
    },
    onError: (error) => {
      toast.error("创建失败：" + error.message);
    },
  });

  // 更新教师
  const updateMutation = trpc.teachers.update.useMutation({
    onSuccess: () => {
      toast.success("教师信息已更新");
      utils.teachers.list.invalidate();
      setIsEditDialogOpen(false);
    },
    onError: (error) => {
      toast.error("更新失败：" + error.message);
    },
  });

  // 删除教师
  const deleteMutation = trpc.teachers.delete.useMutation({
    onSuccess: () => {
      toast.success("教师账户已删除");
      utils.teachers.list.invalidate();
      setIsDeleteDialogOpen(false);
    },
    onError: (error) => {
      toast.error("删除失败：" + error.message);
    },
  });

  // 修改密码
  const changePasswordMutation = trpc.teachers.changePassword.useMutation({
    onSuccess: () => {
      toast.success("密码重置成功");
      setIsResetPasswordDialogOpen(false);
      setNewPassword("");
    },
    onError: (error) => {
      toast.error("密码重置失败：" + error.message);
    },
  });

  const resetAddForm = () => {
    setAddFormData({
      username: "",
      password: "",
      name: "",
      email: "",
      phone: "",
      role: "teacher",
    });
  };

  const handleAdd = () => {
    if (!addFormData.username || !addFormData.password || !addFormData.name) {
      toast.error("请填写必填项：用户名、密码和姓名");
      return;
    }

    if (addFormData.password.length < 6) {
      toast.error("密码至少需要6个字符");
      return;
    }

    createMutation.mutate(addFormData);
  };

  const handleEdit = (teacher: Teacher) => {
    setSelectedTeacher(teacher);
    setEditFormData({
      name: teacher.name,
      email: teacher.email || "",
      phone: teacher.phone || "",
      role: teacher.role,
      status: teacher.status,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdate = () => {
    if (!selectedTeacher) return;

    if (!editFormData.name) {
      toast.error("请填写姓名");
      return;
    }

    updateMutation.mutate({
      id: selectedTeacher.id,
      data: {
        name: editFormData.name,
        email: editFormData.email || null,
        phone: editFormData.phone || null,
        role: editFormData.role,
        status: editFormData.status,
      },
    });
  };

  const handleDelete = (teacher: Teacher) => {
    setSelectedTeacher(teacher);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (!selectedTeacher) return;
    deleteMutation.mutate({ id: selectedTeacher.id });
  };

  const handleResetPassword = (teacher: Teacher) => {
    setSelectedTeacher(teacher);
    setNewPassword("");
    setIsResetPasswordDialogOpen(true);
  };

  const confirmResetPassword = () => {
    if (!selectedTeacher) return;

    if (newPassword.length < 6) {
      toast.error("密码至少需要6个字符");
      return;
    }

    changePasswordMutation.mutate({
      id: selectedTeacher.id,
      newPassword,
    });
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
          <h1 className="text-3xl font-bold tracking-tight">教师管理</h1>
          <p className="text-muted-foreground mt-1">
            管理教师账户和权限分配
          </p>
        </div>
        <Button onClick={() => setIsAddDialogOpen(true)}>
          <UserPlus className="mr-2 h-4 w-4" />
          添加教师
        </Button>
      </div>

      {/* 教师列表 */}
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>用户名</TableHead>
              <TableHead>姓名</TableHead>
              <TableHead>角色</TableHead>
              <TableHead>邮箱</TableHead>
              <TableHead>电话</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>创建时间</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {teachers && teachers.length > 0 ? (
              teachers.map((teacher) => {
                const RoleIcon = roleIcons[teacher.role];
                return (
                  <TableRow key={teacher.id}>
                    <TableCell className="font-medium">{teacher.username}</TableCell>
                    <TableCell>{teacher.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="gap-1">
                        <RoleIcon className="h-3 w-3" />
                        {roleLabels[teacher.role]}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {teacher.email || <span className="italic">未填写</span>}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {teacher.phone || <span className="italic">未填写</span>}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={teacher.status === "active" ? "default" : "secondary"}
                      >
                        {statusLabels[teacher.status]}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(teacher.createdAt).toLocaleDateString("zh-CN")}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(teacher)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleResetPassword(teacher)}
                        >
                          <Key className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(teacher)}
                          disabled={teacher.role === "admin"}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  暂无教师数据
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* 添加教师对话框 */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>添加教师</DialogTitle>
            <DialogDescription>创建新的教师账户并分配角色权限</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="username">
                用户名 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="username"
                value={addFormData.username}
                onChange={(e) =>
                  setAddFormData({ ...addFormData, username: e.target.value })
                }
                placeholder="用于登录的用户名"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">
                密码 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="password"
                type="password"
                value={addFormData.password}
                onChange={(e) =>
                  setAddFormData({ ...addFormData, password: e.target.value })
                }
                placeholder="至少6个字符"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="name">
                姓名 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                value={addFormData.name}
                onChange={(e) =>
                  setAddFormData({ ...addFormData, name: e.target.value })
                }
                placeholder="教师姓名"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">邮箱</Label>
              <Input
                id="email"
                type="email"
                value={addFormData.email}
                onChange={(e) =>
                  setAddFormData({ ...addFormData, email: e.target.value })
                }
                placeholder="可选"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">电话</Label>
              <Input
                id="phone"
                value={addFormData.phone}
                onChange={(e) =>
                  setAddFormData({ ...addFormData, phone: e.target.value })
                }
                placeholder="可选"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">
                角色 <span className="text-destructive">*</span>
              </Label>
              <Select
                value={addFormData.role}
                onValueChange={(value: any) =>
                  setAddFormData({ ...addFormData, role: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">管理员</SelectItem>
                  <SelectItem value="teacher">普通教师</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                {addFormData.role === "admin" && "拥有所有系统管理权限"}
                {addFormData.role === "teacher" && "可以创建试卷、录入成绩等基础操作"}
              </p>
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

      {/* 编辑教师对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>编辑教师</DialogTitle>
            <DialogDescription>
              修改教师信息和权限（用户名：{selectedTeacher?.username}）
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">
                姓名 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="edit-name"
                value={editFormData.name}
                onChange={(e) =>
                  setEditFormData({ ...editFormData, name: e.target.value })
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-email">邮箱</Label>
              <Input
                id="edit-email"
                type="email"
                value={editFormData.email}
                onChange={(e) =>
                  setEditFormData({ ...editFormData, email: e.target.value })
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-phone">电话</Label>
              <Input
                id="edit-phone"
                value={editFormData.phone}
                onChange={(e) =>
                  setEditFormData({ ...editFormData, phone: e.target.value })
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-role">角色</Label>
              <Select
                value={editFormData.role}
                onValueChange={(value: any) =>
                  setEditFormData({ ...editFormData, role: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">管理员</SelectItem>
                  <SelectItem value="teacher">普通教师</SelectItem>
                </SelectContent>
              </Select>
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
                  <SelectItem value="active">启用</SelectItem>
                  <SelectItem value="inactive">停用</SelectItem>
                </SelectContent>
              </Select>
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
              {updateMutation.isPending ? "保存中..." : "保存"}
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
              确定要删除教师 <strong>{selectedTeacher?.name}</strong>（{selectedTeacher?.username}）吗？
              此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteMutation.isPending ? "删除中..." : "删除"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* 重置密码对话框 */}
      <Dialog open={isResetPasswordDialogOpen} onOpenChange={setIsResetPasswordDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>重置密码</DialogTitle>
            <DialogDescription>
              为教师 <strong>{selectedTeacher?.name}</strong>（{selectedTeacher?.username}）设置新密码
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="new-password">
                新密码 <span className="text-destructive">*</span>
              </Label>
              <Input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="至少6个字符"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsResetPasswordDialogOpen(false);
                setNewPassword("");
              }}
            >
              取消
            </Button>
            <Button
              onClick={confirmResetPassword}
              disabled={changePasswordMutation.isPending}
            >
              {changePasswordMutation.isPending ? "重置中..." : "重置密码"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
