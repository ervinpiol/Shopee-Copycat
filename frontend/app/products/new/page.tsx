"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";
import { Header } from "@/components/header";

export default function CreateProductPage() {
  const router = useRouter();

  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    price: "",
    stock: "",
    category: "",
  });
  const [imageFile, setImageFile] = useState<File | null>(null);

  const handleChange = (e: any) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e: any) => {
    setImageFile(e.target.files[0]);
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("name", form.name);
      formData.append("description", form.description);
      formData.append("price", String(form.price));
      formData.append("stock", String(form.stock));
      if (form.category) formData.append("category", form.category);
      if (imageFile) formData.append("image", imageFile);

      const res = await fetch("http://localhost:8000/product", {
        method: "POST",
        credentials: "include", // send cookies
        body: formData, // FormData automatically sets multipart/form-data
      });

      if (!res.ok) {
        console.error(await res.json());
        alert("Failed to create product");
        return;
      }

      router.push("/products");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Header />
      <div className="px-4 py-8">
        <div className="max-w-2xl mx-auto mt-10 p-6 border rounded-xl shadow-sm">
          <h1 className="text-2xl font-bold mb-6">Create Product</h1>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name */}
            <div>
              <label className="block mb-1 font-medium">Product Name</label>
              <Input
                name="name"
                value={form.name}
                onChange={handleChange}
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block mb-1 font-medium">Description</label>
              <Textarea
                name="description"
                value={form.description}
                onChange={handleChange}
              />
            </div>

            {/* Price */}
            <div>
              <label className="block mb-1 font-medium">Price</label>
              <Input
                type="number"
                step="0.01"
                name="price"
                value={form.price}
                onChange={handleChange}
                required
              />
            </div>

            {/* Stock */}
            <div>
              <label className="block mb-1 font-medium">Stock</label>
              <Input
                type="number"
                name="stock"
                value={form.stock}
                onChange={handleChange}
                required
              />
            </div>

            {/* Image */}
            <div>
              <label className="block mb-1 font-medium">Image</label>
              <Input type="file" onChange={handleFileChange} />
            </div>

            {/* Category */}
            <div>
              <label className="block mb-1 font-medium">Category</label>
              <Select
                onValueChange={(value) => setForm({ ...form, category: value })}
                value={form.category}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Electronics">Electronics</SelectItem>
                  <SelectItem value="Accessories">Accessories</SelectItem>
                  <SelectItem value="Storage">Storage</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Submit */}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating..." : "Create Product"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
