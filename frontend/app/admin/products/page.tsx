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
import { Search, Plus } from "lucide-react";
import { Input } from "@/components/ui/input";

const products = [
  {
    id: 1,
    name: "Wireless Headphones",
    category: "Electronics",
    price: "$129.99",
    stock: 45,
    status: "in-stock",
  },
  {
    id: 2,
    name: "Smart Watch",
    category: "Electronics",
    price: "$299.99",
    stock: 23,
    status: "in-stock",
  },
  {
    id: 3,
    name: "Laptop Stand",
    category: "Accessories",
    price: "$49.99",
    stock: 0,
    status: "out-of-stock",
  },
  {
    id: 4,
    name: "USB-C Cable",
    category: "Accessories",
    price: "$19.99",
    stock: 156,
    status: "in-stock",
  },
  {
    id: 5,
    name: "Mechanical Keyboard",
    category: "Electronics",
    price: "$159.99",
    stock: 8,
    status: "low-stock",
  },
];

export default function ProductsPage() {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredProducts = products.filter(
    (product) =>
      product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Products Management
          </h1>
          <p className="text-muted-foreground">Manage your product inventory</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Product
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Products</CardTitle>
          <CardDescription>
            View and manage your product catalog
          </CardDescription>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search products..."
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
                  <th className="pb-3 text-sm font-medium">Product Name</th>
                  <th className="pb-3 text-sm font-medium">Category</th>
                  <th className="pb-3 text-sm font-medium">Price</th>
                  <th className="pb-3 text-sm font-medium">Stock</th>
                  <th className="pb-3 text-sm font-medium">Status</th>
                  <th className="pb-3 text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((product) => (
                  <tr key={product.id} className="border-b last:border-0">
                    <td className="py-4 text-sm font-medium">{product.name}</td>
                    <td className="py-4 text-sm text-muted-foreground">
                      {product.category}
                    </td>
                    <td className="py-4 text-sm font-medium">
                      {product.price}
                    </td>
                    <td className="py-4 text-sm">{product.stock}</td>
                    <td className="py-4">
                      <Badge
                        variant="outline"
                        className={
                          product.status === "in-stock"
                            ? "border-green-500 text-green-600"
                            : product.status === "low-stock"
                            ? "border-yellow-500 text-yellow-600"
                            : "border-red-500 text-red-600"
                        }
                      >
                        {product.status}
                      </Badge>
                    </td>
                    <td className="py-4">
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          Edit
                        </Button>
                        <Button size="sm" variant="outline">
                          Delete
                        </Button>
                      </div>
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
