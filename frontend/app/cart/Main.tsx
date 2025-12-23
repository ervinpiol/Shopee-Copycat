"use client";

import { useRouter } from "next/navigation";
import { useCart } from "@/context/CartContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ShoppingCart, Trash2 } from "lucide-react";
import Link from "next/link";
import { Loading } from "@/components/loading";

export default function Main() {
  const router = useRouter();
  const {
    cartItems,
    updateQuantity,
    removeItem,
    subtotal,
    isFetching,
    hasFetched,
  } = useCart();
  const shipping = subtotal > 100 ? 0 : 10;
  const total = subtotal + shipping;

  const handleCheckout = () => {
    router.push("/checkout");
  };

  if (isFetching && !hasFetched) return <Loading />;

  if (!cartItems.length) {
    return (
      <div className="text-center py-12">
        <ShoppingCart className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Your cart is empty
        </h2>
        <p className="text-muted-foreground mb-6">
          Add items to get started shopping
        </p>
        <Link href="/products">
          <Button size="lg">Browse Products</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="py-8">
      <h1 className="text-3xl font-bold text-foreground mb-6">Shopping Cart</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-4">
          {cartItems.map((item, index) => (
            <Card key={`${item.id}-${index}`} className="p-4 flex gap-4">
              <div className="relative w-24 h-24 shrink-0 bg-muted rounded-lg overflow-hidden">
                <img
                  src={item.product.image}
                  alt={item.product.name}
                  className="object-cover w-full h-full"
                  onError={(e) => {
                    e.currentTarget.style.display = "none"; // hide broken img
                    e.currentTarget.insertAdjacentHTML(
                      "afterend",
                      `<span class="text-2xl bg-black uppercase font-bold flex items-center justify-center rounded-sm text-inverted w-full h-full">
                                        ${item.product.name.charAt(0)}
                                      </span>`
                    );
                  }}
                />
              </div>
              <div className="flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="font-semibold text-foreground mb-1">
                    {item.product.name}
                  </h3>
                  <p className="text-lg font-bold text-primary">
                    ${item.product.price.toFixed(2)}
                  </p>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center border border-border rounded-lg">
                    <Button
                      variant="ghost"
                      onClick={() =>
                        updateQuantity(
                          item.id,
                          item.product.id,
                          item.quantity - 1
                        )
                      }
                      disabled={item.quantity <= 1}
                      className="rounded-r-none"
                    >
                      −
                    </Button>
                    <span className="py-1.5 w-10 text-foreground font-medium text-sm text-center flex items-center justify-center">
                      {item.quantity}
                    </span>
                    <Button
                      variant="ghost"
                      onClick={() =>
                        updateQuantity(
                          item.id,
                          item.product.id,
                          item.quantity + 1
                        )
                      }
                      className="rounded-l-none"
                    >
                      +
                    </Button>
                  </div>

                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Subtotal</p>
                    <p className="font-bold text-foreground">
                      ${(item.product.price * item.quantity).toFixed(2)}
                    </p>
                  </div>
                  <Button
                    variant="destructive"
                    onClick={() => removeItem(item.id, item.product.id)}
                  >
                    <Trash2 className="w-5 h-5" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div className="lg:col-span-1">
          <Card className="sticky top-4">
            <CardContent>
              <h2 className="text-xl font-bold text-foreground mb-4">
                Order Summary
              </h2>
              <div className="space-y-3 mb-4 text-sm">
                <div className="flex justify-between text-muted-foreground">
                  <span>Subtotal ({cartItems.length} items)</span>
                  <span>${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-muted-foreground">
                  <span>Shipping</span>
                  <span
                    className={shipping === 0 ? "text-primary font-medium" : ""}
                  >
                    {shipping === 0 ? "FREE" : `$${shipping.toFixed(2)}`}
                  </span>
                </div>
              </div>
              <div className="border-t border-border pt-3 mb-6">
                <div className="flex justify-between font-bold text-foreground">
                  <span>Total</span>
                  <span className="text-xl">${total.toFixed(2)}</span>
                </div>
              </div>
              <div className="space-y-2">
                <Button className="w-full" size="lg" onClick={handleCheckout}>
                  Proceed to Checkout
                </Button>
                <Link href="/products" className="block">
                  <Button variant="outline" className="w-full bg-transparent">
                    Continue Shopping
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
