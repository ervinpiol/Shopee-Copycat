"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import type { Order } from "@/lib/types";
import { useRouter } from "next/navigation";
import { Header } from "@/components/header";
import { Loading } from "@/components/loading";

export default function OrderPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);

        const { data } = await axios.get("http://localhost:8000/order", {
          withCredentials: true,
        });

        setOrders(data.order ?? data);
      } catch (err: any) {
        setError(
          err.response?.data?.detail || err.message || "Failed to load orders"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  return (
    <div>
      <Header />
      <div className="px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">Orders</h1>
          <p className="text-muted-foreground">
            Browse our curated collection of premium orders
          </p>
        </div>

        {loading ? (
          <Loading />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {orders.map((order) => (
              <div
                key={order.id}
                className="p-4 border rounded-lg shadow-sm space-y-3"
              >
                <h3 className="font-semibold">Order #{order.id}</h3>

                <p className="text-sm text-muted-foreground">
                  Status: {order.status}
                </p>

                <p className="text-lg font-bold">
                  Total: ${order.total_price.toFixed(2)}
                </p>

                {/* Order Items */}
                <div className="mt-4 border-t pt-3 space-y-2">
                  <p className="text-sm font-semibold">Items</p>

                  {order.items.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No items</p>
                  ) : (
                    order.items.map((item) => (
                      <div
                        key={item.id}
                        className="flex justify-between text-sm"
                      >
                        <span>
                          Product #{item.product_id} × {item.quantity}
                        </span>
                        <span className="font-medium">
                          ${item.total_price.toFixed(2)}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
