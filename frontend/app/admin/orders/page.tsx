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
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const orders = [
  {
    id: "#1001",
    customer: "John Doe",
    date: "2024-01-15",
    total: "$129.99",
    status: "delivered",
  },
  {
    id: "#1002",
    customer: "Jane Smith",
    date: "2024-01-16",
    total: "$89.99",
    status: "processing",
  },
  {
    id: "#1003",
    customer: "Bob Wilson",
    date: "2024-01-16",
    total: "$299.99",
    status: "shipped",
  },
  {
    id: "#1004",
    customer: "Alice Johnson",
    date: "2024-01-17",
    total: "$49.99",
    status: "pending",
  },
  {
    id: "#1005",
    customer: "Mike Brown",
    date: "2024-01-17",
    total: "$199.99",
    status: "processing",
  },
  {
    id: "#1006",
    customer: "Sarah Davis",
    date: "2024-01-18",
    total: "$159.99",
    status: "delivered",
  },
];

const statusColors = {
  pending: "border-yellow-500 text-yellow-600",
  processing: "border-blue-500 text-blue-600",
  shipped: "border-purple-500 text-purple-600",
  delivered: "border-green-500 text-green-600",
};

export default function OrdersPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filteredOrders = orders.filter((order) => {
    const matchesSearch =
      order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.customer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || order.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Orders Management</h1>
        <p className="text-muted-foreground">
          Track and manage all shop orders
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Orders</CardTitle>
          <CardDescription>View and filter orders by status</CardDescription>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search orders..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="shipped">Shipped</SelectItem>
                <SelectItem value="delivered">Delivered</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left">
                  <th className="pb-3 text-sm font-medium">Order ID</th>
                  <th className="pb-3 text-sm font-medium">Customer</th>
                  <th className="pb-3 text-sm font-medium">Date</th>
                  <th className="pb-3 text-sm font-medium">Total</th>
                  <th className="pb-3 text-sm font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredOrders.map((order) => (
                  <tr key={order.id} className="border-b last:border-0">
                    <td className="py-4 text-sm font-medium">{order.id}</td>
                    <td className="py-4 text-sm">{order.customer}</td>
                    <td className="py-4 text-sm text-muted-foreground">
                      {order.date}
                    </td>
                    <td className="py-4 text-sm font-medium">{order.total}</td>
                    <td className="py-4">
                      <Badge
                        variant="outline"
                        className={
                          statusColors[
                            order.status as keyof typeof statusColors
                          ]
                        }
                      >
                        {order.status}
                      </Badge>
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
