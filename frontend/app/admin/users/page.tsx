"use client";

import { useState } from "react";
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

const initialUsers = [
  {
    id: 1,
    name: "John Doe",
    email: "john@example.com",
    role: "user",
    status: "active",
    requested: null,
  },
  {
    id: 2,
    name: "Jane Smith",
    email: "jane@example.com",
    role: "seller",
    status: "active",
    requested: null,
  },
  {
    id: 3,
    name: "Bob Wilson",
    email: "bob@example.com",
    role: "user",
    status: "pending",
    requested: "seller",
  },
  {
    id: 4,
    name: "Alice Johnson",
    email: "alice@example.com",
    role: "user",
    status: "pending",
    requested: "admin",
  },
  {
    id: 5,
    name: "Mike Brown",
    email: "mike@example.com",
    role: "admin",
    status: "active",
    requested: null,
  },
];

export default function UsersPage() {
  const [users, setUsers] = useState(initialUsers);
  const [searchTerm, setSearchTerm] = useState("");

  const handleApprove = (userId: number, role: string) => {
    setUsers(
      users.map((user) =>
        user.id === userId
          ? { ...user, role, status: "active", requested: null }
          : user
      )
    );
  };

  const handleReject = (userId: number) => {
    setUsers(
      users.map((user) =>
        user.id === userId
          ? { ...user, status: "active", requested: null }
          : user
      )
    );
  };

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
        <p className="text-muted-foreground">
          Manage user roles and approve seller/admin requests
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Users</CardTitle>
          <CardDescription>
            View and manage user accounts and permissions
          </CardDescription>
          <div className="relative">
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
                    <td className="py-4 text-sm font-medium">{user.name}</td>
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
                      {user.status === "pending" && user.requested ? (
                        <Badge
                          variant="outline"
                          className="border-yellow-500 text-yellow-600"
                        >
                          Pending {user.requested}
                        </Badge>
                      ) : (
                        <Badge
                          variant="outline"
                          className="border-green-500 text-green-600"
                        >
                          Active
                        </Badge>
                      )}
                    </td>
                    <td className="py-4">
                      {user.status === "pending" && user.requested ? (
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() =>
                              handleApprove(user.id, user.requested!)
                            }
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
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
