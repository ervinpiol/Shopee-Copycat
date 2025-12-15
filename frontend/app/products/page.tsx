"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { ProductCard } from "@/components/product-card";
import type { Product } from "@/lib/products";
import { useRouter } from "next/navigation";
import { Header } from "@/components/header";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { Loading } from "@/components/loading";

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const { data } = await axios.get("http://localhost:8000/product");
        setProducts(data.product || data);
      } catch (err: any) {
        setError(
          err.response?.data?.detail || err.message || "Failed to load products"
        );
        console.log(error);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  return (
    <div>
      <Header />
      <div className="px-4 py-8">
        <div className="flex justify-between items-center gap-10 mb-8">
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">
              Welcome to Shop
            </h1>
            <p className="text-muted-foreground">
              Browse our curated collection of premium products
            </p>
          </div>

          <Link href="/products/new">
            <Button>
              <Plus size={20} /> Create New Product
            </Button>
          </Link>
        </div>

        {loading ? (
          <Loading />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                {...product}
                onClick={() => router.push(`/products/${product.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
