"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Star, Heart, ShoppingCart, Check } from "lucide-react";
import type { Product } from "@/lib/products";
import { useCart } from "@/context/CartContext"; // adjust path
import { EditProductModal } from "./edit-product-modal";
import { Spinner } from "./spinner";
import { Loading } from "./loading";

interface ProductDetailProps {
  productId: string;
}

export function ProductDetail({ productId }: ProductDetailProps) {
  const [product, setProduct] = useState<Product | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [added, setAdded] = useState(false);

  const { addToCart } = useCart(); // use context function

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setIsFetching(true);
        const res = await fetch(`http://localhost:8000/product/${productId}`);
        const data = await res.json();
        setProduct(data.product || data);
      } catch (err: any) {
        setError(err.message || "Failed to load product");
      } finally {
        setIsFetching(false);
      }
    };

    fetchProduct();
  }, [productId]);

  const handleAddToCart = async () => {
    setLoading(true);
    if (!product) return;
    try {
      await addToCart(product.id, quantity); // use context method
      setAdded(true);
      setQuantity(1);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (isFetching) return <Loading />;

  if (error || !product)
    return (
      <div className="py-12 text-center text-destructive">
        {error || "Product not found"}
      </div>
    );

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 px-4 py-8">
      {loading && <Spinner />}
      {/* Product Image */}
      <div className="flex items-center justify-center bg-muted rounded-lg overflow-hidden">
        <div className="relative w-full aspect-square">
          <img
            src={product.image}
            alt={product.name}
            className="object-contain w-full h-full group-hover:scale-110 transition-transform duration-300"
            onError={(e) => {
              e.currentTarget.style.display = "none"; // hide broken img
              e.currentTarget.insertAdjacentHTML(
                "afterend",
                `<span class="text-2xl bg-black uppercase font-bold flex items-center justify-center rounded-sm text-inverted w-full h-full">
                                        ${product.name.charAt(0)}
                                      </span>`
              );
            }}
          />
        </div>
      </div>

      {/* Product Info */}
      <div className="space-y-6">
        <div>
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                {product.name}
              </h1>
              <p className="text-muted-foreground text-sm">
                {product.category}
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="text-muted-foreground hover:text-destructive"
            >
              <Heart className="w-6 h-6" />
            </Button>
          </div>

          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center gap-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  className={`w-5 h-5 ${
                    i < Math.floor(product.rating)
                      ? "fill-primary text-primary"
                      : "text-muted-foreground"
                  }`}
                />
              ))}
            </div>
            <span className="font-semibold text-foreground">
              {product.rating}
            </span>
            <span className="text-muted-foreground text-sm">
              ({product.reviews} reviews)
            </span>
          </div>
        </div>

        <div className="border-t border-b py-4">
          <div
            className={`text-4xl font-bold text-primary mb-2 ${
              product.stock === 0 ? "line-through" : ""
            }`}
          >
            ${product.price.toFixed(2)}
          </div>
          <p className="text-sm text-muted-foreground">
            {product.stock > 0 ? (
              <span className="text-primary font-medium">
                {product.stock} in stock
              </span>
            ) : (
              <span className="text-destructive font-medium">Out of stock</span>
            )}
          </p>
        </div>

        <p className="text-foreground leading-relaxed">{product.description}</p>

        {/* Quantity Selector */}
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-foreground">Quantity:</span>
          <div className="flex items-center border border-border rounded-lg">
            <Button
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              variant="ghost"
              disabled={product.stock === 0}
              className="rounded-r-none"
            >
              −
            </Button>
            <span className="py-1.5 w-10 text-foreground font-medium text-sm text-center flex items-center justify-center">
              {quantity}
            </span>
            <Button
              onClick={() => setQuantity(Math.min(product.stock, quantity + 1))}
              variant="ghost"
              disabled={quantity >= product.stock || product.stock === 0}
              className="rounded-l-none"
            >
              +
            </Button>
          </div>
        </div>

        {/* Add to Cart Button */}
        <div className="flex flex-col gap-2">
          <Button
            onClick={handleAddToCart}
            disabled={product.stock === 0}
            className="w-full"
          >
            {added ? (
              <>
                <Check size={20} />
                Added to Cart
              </>
            ) : (
              <>
                <ShoppingCart size={20} />
                Add to Cart
              </>
            )}
          </Button>

          <EditProductModal productId={product.id} />
        </div>
      </div>
    </div>
  );
}
