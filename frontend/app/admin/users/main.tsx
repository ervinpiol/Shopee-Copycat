"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Check, X, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import axios from "axios";
import { Loading } from "@/components/loading";

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  is_active: boolean;
}

export default function Main() {
  const [users, setUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch users from backend
  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.get<User[]>(
        "http://localhost:8000/admin/users/",
        {
          withCredentials: true,
        }
      );
      setUsers(data);
    } catch (err: any) {
      console.error("Failed to fetch users", err);
      setError(err.response?.data?.detail || "Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleApprove = (userId: number, role: string) => {
    setUsers((prev) =>
      prev.map((user) =>
        user.id === userId ? { ...user, role, is_active: true } : user
      )
    );
  };

  const handleReject = (userId: number) => {
    setUsers((prev) =>
      prev.map((user) =>
        user.id === userId ? { ...user, is_active: true } : user
      )
    );
  };

  const filteredUsers = users.filter(
    (user) =>
      `${user.first_name} ${user.last_name}`
        .toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <Loading />;

  if (error)
    return (
      <div className="p-8 text-center text-red-500">
        <p>{error}</p>
      </div>
    );

  return (
    <Card>
      <CardHeader>
        <CardTitle>All Users</CardTitle>
        <CardDescription>
          View and manage user accounts and permissions
        </CardDescription>
        <div className="relative mt-2">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b text-left">
                <th className="pb-3 text-sm font-medium">Name</th>
                <th className="pb-3 text-sm font-medium">Email</th>
                <th className="pb-3 text-sm font-medium">Role</th>
                <th className="pb-3 text-sm font-medium">Status</th>
                <th className="pb-3 text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id} className="border-b last:border-0">
                  <td className="py-4 text-sm font-medium">
                    {user.first_name} {user.last_name}
                  </td>
                  <td className="py-4 text-sm text-muted-foreground">
                    {user.email}
                  </td>
                  <td className="py-4">
                    <Badge
                      variant={
                        user.role === "admin"
                          ? "default"
                          : user.role === "seller"
                          ? "secondary"
                          : "outline"
                      }
                    >
                      {user.role}
                    </Badge>
                  </td>
                  <td className="py-4">
                    {user.is_active ? (
                      <Badge
                        variant="outline"
                        className="border-green-500 text-green-600"
                      >
                        Active
                      </Badge>
                    ) : (
                      <Badge
                        variant="outline"
                        className="border-yellow-500 text-yellow-600"
                      >
                        Pending
                      </Badge>
                    )}
                  </td>
                  <td className="py-4">
                    {!user.is_active ? (
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleApprove(user.id, user.role)}
                        >
                          <Check className="mr-1 h-4 w-4" />
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleReject(user.id)}
                        >
                          <X className="mr-1 h-4 w-4" />
                          Reject
                        </Button>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">
                        No action needed
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredUsers.length === 0 && (
            <p className="mt-4 text-center text-sm text-muted-foreground">
              No users found
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
