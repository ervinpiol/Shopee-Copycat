"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { Pen } from "lucide-react";
import { Spinner } from "./spinner";

interface EditProductModalProps {
  productId: string;
}

export function EditProductModal({ productId }: EditProductModalProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    price: 0,
    stock: 0,
    category: "",
    is_active: true,
    image: "",
    rating: 5,
    reviews: 0,
  });
  const [imageFile, setImageFile] = useState<File | null>(null);

  useEffect(() => {
    if (!open) return;

    const fetchProduct = async () => {
      try {
        const res = await fetch(`http://localhost:8000/product/${productId}`);
        const data = await res.json();
        const product = data.product || data;

        setForm({
          name: product.name ?? "",
          description: product.description ?? "",
          price: product.price ?? 0,
          stock: product.stock ?? 0,
          category: product.category ?? "",
          is_active: product.is_active ?? true,
          image: product.image ?? "",
          rating: product.rating ?? 5,
          reviews: product.reviews ?? 0,
        });
      } catch (err) {
        toast.error("Failed to load product");
      }
    };

    fetchProduct();
  }, [open, productId]);

  const handleChange = (e: any) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // Update product info via PATCH
      const res = await fetch(`http://localhost:8000/product/${productId}`, {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to update product");
      }

      // Upload image if selected
      if (imageFile) {
        const formData = new FormData();
        formData.append("image", imageFile);

        const imgRes = await fetch(
          `http://localhost:8000/product/${productId}/image`,
          {
            method: "POST",
            body: formData,
            credentials: "include",
          }
        );

        if (!imgRes.ok) {
          const imgError = await imgRes.json();
          throw new Error(imgError.detail || "Failed to upload image");
        }
      }

      toast.success("Product updated successfully!");
      setOpen(false);
    } catch (err: any) {
      toast.error(err.message || "Update failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {loading && <Spinner />}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button className="w-full">
            <Pen size={20} />
            Edit Product
          </Button>
        </DialogTrigger>

        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Product</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="block mb-1 font-medium">Name</label>
              <Input name="name" value={form.name} onChange={handleChange} />
            </div>

            <div>
              <label className="block mb-1 font-medium">Description</label>
              <Textarea
                name="description"
                value={form.description}
                onChange={handleChange}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block mb-1 font-medium">Price</label>
                <Input
                  type="number"
                  step="0.01"
                  name="price"
                  value={form.price}
                  onChange={(e) =>
                    setForm({ ...form, price: Number(e.target.value) })
                  }
                />
              </div>

              <div>
                <label className="block mb-1 font-medium">Stock</label>
                <Input
                  type="number"
                  name="stock"
                  value={form.stock}
                  onChange={(e) =>
                    setForm({ ...form, stock: Number(e.target.value) })
                  }
                />
              </div>
            </div>

            <div>
              <label className="block mb-1 font-medium">Category</label>
              <Select
                value={form.category}
                onValueChange={(v) => setForm({ ...form, category: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Electronics">Electronics</SelectItem>
                  <SelectItem value="Accessories">Accessories</SelectItem>
                  <SelectItem value="Storage">Storage</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="block mb-1 font-medium">Image File</label>
              <div className="space-y-2">
                {/* Current image preview */}
                {form.image && !imageFile && (
                  <img
                    src={form.image}
                    alt="Product image"
                    className="w-24 h-24 object-cover rounded-md border"
                  />
                )}

                {/* New image preview if file selected */}
                {imageFile && (
                  <img
                    src={URL.createObjectURL(imageFile)}
                    alt="Selected image"
                    className="w-24 h-24 object-cover rounded-md border"
                  />
                )}

                {/* File input */}
                <Input
                  type="file"
                  onChange={(e) => setImageFile(e.target.files?.[0] ?? null)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block mb-1 font-medium">Rating</label>
                <Input
                  type="number"
                  min={0}
                  max={5}
                  name="rating"
                  value={form.rating}
                  onChange={(e) =>
                    setForm({ ...form, rating: Number(e.target.value) })
                  }
                />
              </div>

              <div>
                <label className="block mb-1 font-medium">Reviews</label>
                <Input
                  type="number"
                  name="reviews"
                  value={form.reviews}
                  onChange={(e) =>
                    setForm({ ...form, reviews: Number(e.target.value) })
                  }
                />
              </div>
            </div>
          </div>

          <DialogFooter className="mt-6">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={loading}>
              {loading ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
