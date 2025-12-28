"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { CreditCard, Wallet } from "lucide-react";
import { cn } from "@/lib/utils";
import { useCart } from "@/context/CartContext";
import { toast } from "sonner";
import { Spinner } from "@/components/spinner";

interface Address {
  id: number;
  label: string;
  recipient_name: string;
  phone: number; // matches backend response
  address_line1: string;
  address_line2?: string;
  city: string;
  province: string;
  postal_code: number;
  country: string;
  is_default: boolean;
}

export default function CheckoutPage() {
  const { cartItems, subtotal, clearCart, isFetching, hasFetched } = useCart();

  const [addresses, setAddresses] = useState<Address[]>([]);
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(
    null
  );
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [loading, setLoading] = useState(true);

  const shippingFee = subtotal > 100 ? 0 : 10;
  const total = subtotal + shippingFee;

  /* ============================
     Fetch addresses only
  ============================ */
  useEffect(() => {
    const fetchAddresses = async () => {
      try {
        const res = await axios.get(
          "http://localhost:8000/users/me/addresses",
          { withCredentials: true }
        );

        setAddresses(res.data);

        const defaultAddress = res.data.find((a: Address) => a.is_default);

        if (defaultAddress) {
          setSelectedAddressId(defaultAddress.id);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchAddresses();
  }, []);

  /* ============================
     Checkout
  ============================ */
  const handleCheckout = async () => {
    if (!selectedAddressId || !cartItems.length) return;

    setLoading(true);
    try {
      await axios.post(
        "http://localhost:8000/checkout",
        {
          address_id: selectedAddressId,
          payment_method: paymentMethod,
        },
        { withCredentials: true }
      );

      clearCart();
      toast.success("Order placed successfully!");
    } catch (err: any) {
      const detail = err.response?.data?.detail;

      let message = "Checkout failed";

      if (typeof detail === "string") {
        message = detail;
      } else if (Array.isArray(detail)) {
        message = detail.map((d) => d.msg).join(", ");
      }

      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  /* ============================
     States
  ============================ */
  if (isFetching && !hasFetched) {
    return <p className="text-center py-12">Loading checkout…</p>;
  }

  if (!cartItems.length) {
    return <p className="text-center py-12">Your cart is empty</p>;
  }

  /* ============================
     UI
  ============================ */
  return (
    <div className="mx-auto py-8 max-w-6xl">
      {loading && <Spinner />}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Checkout</h1>
        <p className="text-sm text-muted-foreground">
          Review your order before placing it
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT */}
        <div className="lg:col-span-2 space-y-6">
          {/* Delivery Address */}
          <Card className="border-2">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Delivery Address</CardTitle>
              <Button size="sm" variant="outline">
                Change
              </Button>
            </CardHeader>

            <CardContent className="space-y-4">
              {addresses.map((address) => {
                const isSelected = selectedAddressId === address.id;

                return (
                  <div
                    key={address.id}
                    onClick={() => setSelectedAddressId(address.id)}
                    className={cn(
                      "flex gap-3 border rounded-md p-4 cursor-pointer transition",
                      isSelected
                        ? "border-primary bg-primary/5"
                        : "hover:bg-muted/50"
                    )}
                  >
                    <input
                      type="radio"
                      checked={isSelected}
                      readOnly
                      className="mt-1"
                    />

                    <div className="flex-1 space-y-1 text-sm">
                      <div className="flex items-center gap-2 font-semibold">
                        <span>{address.recipient_name}</span>
                        <span className="text-muted-foreground">
                          {address.phone}
                        </span>

                        {address.is_default && (
                          <span className="text-xs border border-primary text-primary px-1 rounded">
                            Default
                          </span>
                        )}
                      </div>

                      <p className="text-muted-foreground">
                        {address.address_line1}
                        {address.address_line2
                          ? `, ${address.address_line2}`
                          : ""}
                      </p>

                      <p className="text-muted-foreground">
                        {address.city}, {address.province},{" "}
                        {address.postal_code}
                      </p>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* Payment Method */}
          <Card className="border-2">
            <CardHeader>
              <CardTitle>Payment Method</CardTitle>
            </CardHeader>

            <CardContent>
              <RadioGroup
                value={paymentMethod}
                onValueChange={setPaymentMethod}
                className="space-y-3"
              >
                <div className="flex items-center gap-3 border p-4 rounded-md">
                  <RadioGroupItem value="card" />
                  <CreditCard className="h-5 w-5" />
                  Card
                </div>

                <div className="flex items-center gap-3 border p-4 rounded-md">
                  <RadioGroupItem value="wallet" />
                  <Wallet className="h-5 w-5" />
                  Wallet
                </div>
              </RadioGroup>
            </CardContent>
          </Card>
        </div>

        {/* RIGHT — ORDER SUMMARY */}
        <Card className="border-2 h-fit sticky top-4">
          <CardHeader>
            <CardTitle>Order Summary</CardTitle>
          </CardHeader>

          <CardContent className="space-y-3 text-sm">
            {cartItems.map((item) => (
              <div key={item.id} className="flex justify-between">
                <span>
                  {item.product.name} × {item.quantity}
                </span>
                <span>₱{(item.product.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}

            <div className="border-t pt-3 space-y-2">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>₱{subtotal.toFixed(2)}</span>
              </div>

              <div className="flex justify-between">
                <span>Shipping</span>
                <span>{shippingFee === 0 ? "FREE" : `₱${shippingFee}`}</span>
              </div>

              <div className="flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>₱{total.toFixed(2)}</span>
              </div>
            </div>

            <Button
              size="lg"
              className="w-full"
              disabled={!selectedAddressId}
              onClick={handleCheckout}
            >
              Place Order
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
