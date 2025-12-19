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
import { Search, ChevronDown, ChevronUp, Package, User } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import axios from "axios";
import { Loading } from "@/components/loading";

interface OrderItem {
  id: number;
  product_id: number;
  seller_id: number;
  quantity: number;
  total_price: number;
  product_name: string;
  status: string;
  image: string;
}

interface Order {
  id: number;
  owner_id: number;
  owner_name: string;
  status: string;
  total_price: number;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

const statusColors = {
  pending: "border-yellow-500 bg-yellow-50 text-yellow-700",
  processing: "border-blue-500 bg-blue-50 text-blue-700",
  shipped: "border-purple-500 bg-purple-50 text-purple-700",
  delivered: "border-green-500 bg-green-50 text-green-700",
};

export default function Main() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedOrders, setExpandedOrders] = useState<number[]>([]);

  const fetchOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.get<Order[]>("http://localhost:8000/order", {
        withCredentials: true,
      });
      setOrders(data);
    } catch (err: any) {
      console.error("Failed to fetch orders", err);
      setError(err.response?.data?.detail || "Failed to fetch orders");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const toggleExpand = (orderId: number) => {
    setExpandedOrders((prev) =>
      prev.includes(orderId)
        ? prev.filter((id) => id !== orderId)
        : [...prev, orderId]
    );
  };

  const filteredOrders = orders.filter((order) => {
    const matchesSearch =
      order.id.toString().includes(searchTerm.toLowerCase()) ||
      order.owner_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || order.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (loading) return <Loading />;

  if (error)
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="text-center">
          <p className="text-lg font-semibold text-red-600">{error}</p>
        </div>
      </div>
    );

  return (
    <div>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by order ID or customer name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-[200px]">
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

      {filteredOrders.length === 0 ? (
        <Card>
          <CardContent className="flex min-h-[300px] items-center justify-center">
            <div className="text-center">
              <Package className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
              <p className="text-lg font-medium text-muted-foreground">
                No orders found
              </p>
              <p className="text-sm text-muted-foreground">
                Try adjusting your search or filters
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredOrders.map((order) => {
            const isExpanded = expandedOrders.includes(order.id);
            return (
              <Card
                key={order.id}
                className="overflow-hidden transition-shadow hover:shadow-lg"
              >
                <CardHeader className="pb-4">
                  <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        <CardTitle className="text-2xl">
                          Order #{order.id}
                        </CardTitle>
                        <Badge
                          variant="outline"
                          className={
                            statusColors[
                              order.status as keyof typeof statusColors
                            ]
                          }
                        >
                          {order.status.charAt(0).toUpperCase() +
                            order.status.slice(1)}
                        </Badge>
                      </div>
                      <CardDescription className="text-base">
                        Placed on{" "}
                        {new Date(order.created_at).toLocaleDateString(
                          "en-US",
                          {
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                          }
                        )}
                      </CardDescription>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold">
                        ${order.total_price.toFixed(2)}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {order.items.length}{" "}
                        {order.items.length === 1 ? "item" : "items"}
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Customer Info */}
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <User className="h-4 w-4" />
                    <span className="font-medium">{order.owner_name}</span>
                  </div>

                  {/* Toggle Items Button */}
                  <button
                    onClick={() => toggleExpand(order.id)}
                    className="flex w-full items-center justify-center gap-2 rounded-lg border bg-muted/50 px-4 py-3 text-sm font-medium transition-colors hover:bg-muted"
                  >
                    {isExpanded ? (
                      <>
                        <ChevronUp className="h-4 w-4" />
                        Hide Order Items
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-4 w-4" />
                        View Order Items
                      </>
                    )}
                  </button>

                  {/* Expanded Items */}
                  {isExpanded && (
                    <div className="space-y-3 rounded-lg border bg-muted/30 p-4">
                      <h4 className="font-semibold">Order Items</h4>
                      <div className="space-y-3">
                        {order.items.map((item) => (
                          <div
                            key={item.id}
                            className="flex flex-col gap-3 rounded-lg border bg-background p-4 sm:flex-row sm:items-center sm:justify-between"
                          >
                            <div className="relative w-24 h-24 shrink-0 bg-muted rounded-lg overflow-hidden">
                              {item.image ? (
                                <img
                                  src={item.image}
                                  alt={item.product_name}
                                  className="object-cover w-full h-full rounded-sm"
                                  onError={(e) => {
                                    const fallback =
                                      document.createElement("span");
                                    fallback.textContent = item.product_name
                                      .charAt(0)
                                      .toUpperCase();
                                    fallback.className =
                                      "text-sm bg-black uppercase font-bold flex items-center justify-center rounded-sm text-inverted w-10 h-10";
                                    e.currentTarget.replaceWith(fallback);
                                  }}
                                />
                              ) : (
                                <span className="text-lg bg-black uppercase font-bold flex items-center justify-center rounded-sm text-white w-full h-full">
                                  {item.product_name.charAt(0)}
                                </span>
                              )}
                            </div>
                            <div className="flex-1 space-y-1">
                              <div className="font-medium">
                                {item.product_name}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                Quantity: {item.quantity}
                              </div>
                            </div>
                            <div className="flex items-center gap-4">
                              <div className="text-right">
                                <div className="font-semibold">
                                  ${item.total_price.toFixed(2)}
                                </div>
                              </div>
                              <Badge
                                variant="outline"
                                className={
                                  statusColors[
                                    item.status as keyof typeof statusColors
                                  ]
                                }
                              >
                                {item.status.charAt(0).toUpperCase() +
                                  item.status.slice(1)}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
