"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Shield,
  Trash2,
  CheckCircle,
  XCircle,
  ChevronLeft,
  ChevronRight,
  Users,
  Activity,
  Loader2,
  ArrowUpDown,
} from "lucide-react";
import {
  AdminAPI,
  type AdminUser,
  type ActivityLog,
} from "@/lib/api";

type Tab = "users" | "activity";

export function AdminConsole() {
  const [tab, setTab] = useState<Tab>("users");

  return (
    <Card className="pixel-card pixel-border">
      <CardHeader>
        <CardTitle className="pixel-heading text-2xl flex items-center gap-2">
          <Shield className="w-5 h-5 text-orange-500" />
          Admin Console
        </CardTitle>
        <div className="flex gap-2 mt-2">
          <Button
            variant={tab === "users" ? "gold" : "outline"}
            size="sm"
            className="gap-1 pixel-border"
            onClick={() => setTab("users")}
          >
            <Users className="w-4 h-4" />
            Users
          </Button>
          <Button
            variant={tab === "activity" ? "gold" : "outline"}
            size="sm"
            className="gap-1 pixel-border"
            onClick={() => setTab("activity")}
          >
            <Activity className="w-4 h-4" />
            Activity Logs
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {tab === "users" ? <UsersTab /> : <ActivityTab />}
      </CardContent>
    </Card>
  );
}

/* ─── Users Tab ─── */

function UsersTab() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [bulkLoading, setBulkLoading] = useState(false);
  const perPage = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await AdminAPI.getUsers(page, perPage);
      setUsers(res.users);
      setTotal(res.total);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    load();
  }, [load]);

  const totalPages = Math.ceil(total / perPage);

  const handleApprove = async (userId: number) => {
    setActionLoading(userId);
    try {
      await AdminAPI.approveUser(userId);
      await load();
    } finally {
      setActionLoading(null);
    }
  };

  const handleDisapprove = async (userId: number) => {
    setActionLoading(userId);
    try {
      await AdminAPI.disapproveUser(userId);
      await load();
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleRole = async (user: AdminUser) => {
    setActionLoading(user.id);
    try {
      const newRole = user.role === "admin" ? "user" : "admin";
      await AdminAPI.changeRole(user.id, newRole);
      await load();
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (user: AdminUser) => {
    if (!confirm(`Delete user "${user.username}" and all their data? This cannot be undone.`))
      return;
    setActionLoading(user.id);
    try {
      await AdminAPI.deleteUser(user.id);
      setSelected((prev) => { const next = new Set(prev); next.delete(user.id); return next; });
      await load();
    } finally {
      setActionLoading(null);
    }
  };

  const toggleSelect = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selected.size === users.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(users.map((u) => u.id)));
    }
  };

  const handleBulkDelete = async () => {
    if (selected.size === 0) return;
    if (
      !confirm(
        `Delete ${selected.size} selected user(s) and all their data? This cannot be undone.`
      )
    )
      return;
    setBulkLoading(true);
    try {
      await AdminAPI.bulkDeleteUsers(Array.from(selected));
      setSelected(new Set());
      await load();
    } finally {
      setBulkLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-orange-500" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Bulk action bar */}
      {selected.size > 0 && (
        <div className="flex items-center gap-3 p-3 rounded-none border-2 border-red-500/30 bg-red-500/5">
          <span className="text-sm font-medium">
            {selected.size} user{selected.size !== 1 ? "s" : ""} selected
          </span>
          <Button
            variant="outline"
            size="sm"
            className="h-7 px-3 text-xs rounded-none border-red-500/40 text-red-500 hover:bg-red-500/10 gap-1"
            onClick={handleBulkDelete}
            disabled={bulkLoading}
          >
            {bulkLoading ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <Trash2 className="w-3 h-3" />
            )}
            Delete selected
          </Button>
          <button
            className="text-xs text-muted-foreground hover:text-foreground ml-auto"
            onClick={() => setSelected(new Set())}
          >
            Clear selection
          </button>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-border text-left text-muted-foreground">
              <th className="py-2 pr-2 w-8">
                <input
                  type="checkbox"
                  checked={users.length > 0 && selected.size === users.length}
                  onChange={toggleSelectAll}
                  className="accent-orange-500"
                />
              </th>
              <th className="py-2 pr-4">Username</th>
              <th className="py-2 pr-4">Email</th>
              <th className="py-2 pr-4">Role</th>
              <th className="py-2 pr-4">Approved</th>
              <th className="py-2 pr-4">Created</th>
              <th className="py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr
                key={u.id}
                className={`border-b border-border/50 hover:bg-muted/30 ${
                  selected.has(u.id) ? "bg-orange-500/5" : ""
                }`}
              >
                <td className="py-2 pr-2">
                  <input
                    type="checkbox"
                    checked={selected.has(u.id)}
                    onChange={() => toggleSelect(u.id)}
                    className="accent-orange-500"
                  />
                </td>
                <td className="py-2 pr-4 font-medium">{u.username}</td>
                <td className="py-2 pr-4 text-muted-foreground">{u.email || "—"}</td>
                <td className="py-2 pr-4">
                  <span
                    className={`px-2 py-0.5 text-xs border rounded-none ${
                      u.role === "admin"
                        ? "border-orange-500/40 bg-orange-500/10 text-orange-500"
                        : "border-border bg-muted text-muted-foreground"
                    }`}
                  >
                    {u.role}
                  </span>
                </td>
                <td className="py-2 pr-4">
                  {u.is_approved ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-500" />
                  )}
                </td>
                <td className="py-2 pr-4 text-muted-foreground">
                  {new Date(u.created_at).toLocaleDateString()}
                </td>
                <td className="py-2 text-right">
                  <div className="flex justify-end gap-1">
                    {u.is_approved ? (
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-7 px-2 text-xs rounded-none"
                        onClick={() => handleDisapprove(u.id)}
                        disabled={actionLoading === u.id}
                        title="Revoke approval"
                      >
                        <XCircle className="w-3 h-3" />
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-7 px-2 text-xs rounded-none border-green-500/40 text-green-500 hover:bg-green-500/10"
                        onClick={() => handleApprove(u.id)}
                        disabled={actionLoading === u.id}
                        title="Approve user"
                      >
                        <CheckCircle className="w-3 h-3" />
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-7 px-2 text-xs rounded-none"
                      onClick={() => handleToggleRole(u)}
                      disabled={actionLoading === u.id}
                      title={u.role === "admin" ? "Demote to user" : "Promote to admin"}
                    >
                      <ArrowUpDown className="w-3 h-3" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-7 px-2 text-xs rounded-none border-red-500/40 text-red-500 hover:bg-red-500/10"
                      onClick={() => handleDelete(u)}
                      disabled={actionLoading === u.id}
                      title="Delete user"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <span className="text-sm text-muted-foreground">
            {total} user{total !== 1 ? "s" : ""} total
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="h-7 rounded-none"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span className="text-sm text-muted-foreground">
              {page} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              className="h-7 rounded-none"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── Activity Tab ─── */

function ActivityTab() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const perPage = 30;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await AdminAPI.getActivityLogs(page, perPage);
      setLogs(res.activities);
      setTotal(res.total);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    load();
  }, [load]);

  const totalPages = Math.ceil(total / perPage);

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-orange-500" />
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <p className="text-center text-muted-foreground py-8">No activity logs yet.</p>
    );
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-border text-left text-muted-foreground">
              <th className="py-2 pr-4">Time</th>
              <th className="py-2 pr-4">User</th>
              <th className="py-2 pr-4">Action</th>
              <th className="py-2 pr-4">Detail</th>
              <th className="py-2">IP</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-b border-border/50 hover:bg-muted/30">
                <td className="py-2 pr-4 text-muted-foreground whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleString()}
                </td>
                <td className="py-2 pr-4 font-medium">{log.username}</td>
                <td className="py-2 pr-4">
                  <span className="px-2 py-0.5 text-xs border border-border rounded-none bg-muted">
                    {log.action}
                  </span>
                </td>
                <td className="py-2 pr-4 text-muted-foreground">{log.detail || "—"}</td>
                <td className="py-2 text-muted-foreground font-mono text-xs">
                  {log.ip_address || "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <span className="text-sm text-muted-foreground">
            {total} log{total !== 1 ? "s" : ""} total
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="h-7 rounded-none"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span className="text-sm text-muted-foreground">
              {page} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              className="h-7 rounded-none"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
