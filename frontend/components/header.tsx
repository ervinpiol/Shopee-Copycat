"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ShoppingCart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useCart } from "@/context/CartContext";
import { useAuth } from "@/context/AuthContext";
import axios from "axios";
import { Spinner } from "./spinner";
import { useState } from "react";

export function Header() {
  const { itemCount } = useCart();
  const { user } = useAuth(); // 👈 get logged-in user
  const pathname = usePathname();
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const baseClasses = "font-medium";

  const getLinkClasses = (href: string) => {
    const isActive = pathname === href;
    return `${baseClasses} ${
      isActive
        ? "text-primary border-b-2 border-primary"
        : "text-foreground hover:text-primary/80"
    }`;
  };

  // 👇 LOGOUT HANDLER
  async function handleLogout() {
    setLoading(true);
    try {
      await axios.post(
        "http://localhost:8000/auth/jwt/logout",
        {},
        { withCredentials: true }
      );

      router.push("/auth/login");
      router.refresh(); // refresh the page state
    } catch (err) {
      console.error("Logout failed", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
      {loading && <Spinner />}
      <div className="container mx-auto px-4 flex items-center justify-between gap-4 h-16">
        <div className="flex items-center gap-10">
          <Link href="/products" className={getLinkClasses("/products")}>
            Shop
          </Link>

          <Link href="/orders" className={getLinkClasses("/orders")}>
            Orders
          </Link>

          <Link href="/todo" className={getLinkClasses("/todo")}>
            Todo App
          </Link>
        </div>

        <div className="flex items-center gap-4">
          {/* Cart */}
          <Link href="/cart">
            <Button variant="ghost" size="icon" className="relative">
              <ShoppingCart className="size-5" />
              {itemCount > 0 && (
                <span className="absolute top-1 right-4 translate-x-full px-1 h-4 bg-primary text-primary-foreground rounded-full text-xs font-bold flex items-center justify-center">
                  {itemCount}
                </span>
              )}
            </Button>
          </Link>

          {/* 👇 Show Logout only if logged in */}
          {user && (
            <Button variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
