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

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
}

interface Address {
  id: number;
  label: string;
  recipient_name: string;
  phone: number;
  address_line1: string;
  address_line2?: string;
  city: string;
  province: string;
  postal_code: number;
  country: string;
  is_default: boolean;
}

export default function Main() {
  const { cartItems, subtotal, clearCart, isFetching, hasFetched } = useCart();

  const [user, setUser] = useState<User | null>(null);
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(
    null
  );
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [loading, setLoading] = useState(true);

  const shippingFee = subtotal > 100 ? 0 : 10;
  const total = subtotal + shippingFee;

  useEffect(() => {
    const fetchCheckoutData = async () => {
      try {
        const [userRes, addressRes] = await Promise.all([
          axios.get("http://localhost:8000/users/me", {
            withCredentials: true,
          }),
          axios.get("http://localhost:8000/users/me/addresses", {
            withCredentials: true,
          }),
        ]);

        setUser(userRes.data);
        setAddresses(addressRes.data);

        const defaultAddress = addressRes.data.find(
          (a: Address) => a.is_default
        );
        if (defaultAddress) {
          setSelectedAddressId(defaultAddress.id);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchCheckoutData();
  }, []);

  const handleCheckout = async () => {
    if (!selectedAddressId || !cartItems.length) return;

    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:8000/checkout",
        {}, // empty body, backend uses current_user
        { withCredentials: true }
      );
      clearCart();

      toast.success("Checkout successful!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Checkout failed");
    } finally {
      setLoading(false);
    }
  };

  if (loading || (isFetching && !hasFetched)) {
    return <p className="text-center py-12">Loading checkout…</p>;
  }

  if (!cartItems.length) {
    return <p className="text-center py-12">Your cart is empty</p>;
  }

  return (
    <div className="mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Checkout
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Complete your purchase securely
        </p>
      </div>

      <div className="mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT */}
        <div className="lg:col-span-2 space-y-6">
          {/* Contact Info */}
          <Card className="border-2">
            <CardHeader>
              <CardTitle>1. Contact Information</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <div>
                <p className="text-muted-foreground">Name</p>
                <p className="font-medium">
                  {user?.first_name} {user?.last_name || ""}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Email</p>
                <p className="font-medium">{user?.email}</p>
              </div>
            </CardContent>
          </Card>

          {/* Shipping Address */}
          <Card className="border-2">
            <CardHeader className="flex flex-row justify-between">
              <CardTitle>2. Shipping Address</CardTitle>
              <Button size="sm" variant="outline">
                Add Address
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {addresses.map((address) => (
                <div
                  key={address.id}
                  onClick={() => setSelectedAddressId(address.id)}
                  className={cn(
                    "border-2 rounded-sm p-4 cursor-pointer transition",
                    selectedAddressId === address.id
                      ? "border-primary bg-primary/5"
                      : "hover:bg-muted/50"
                  )}
                >
                  <p className="font-semibold">
                    {address.label} — {address.recipient_name}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {address.address_line1}
                    {address.address_line2 ? `, ${address.address_line2}` : ""}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {address.city}, {address.province} {address.postal_code}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    📞 {address.phone}
                  </p>

                  {address.is_default && (
                    <span className="text-xs font-bold text-primary">
                      DEFAULT
                    </span>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Payment */}
          <Card className="border-2">
            <CardHeader>
              <CardTitle>3. Payment Method</CardTitle>
            </CardHeader>
            <CardContent>
              <RadioGroup
                value={paymentMethod}
                onValueChange={setPaymentMethod}
                className="space-y-3"
              >
                <div className="flex items-center gap-3 border-2 p-4 rounded-sm">
                  <RadioGroupItem value="card" />
                  <CreditCard className="h-5 w-5" /> Card
                </div>
                <div className="flex items-center gap-3 border-2 p-4 rounded-sm">
                  <RadioGroupItem value="wallet" />
                  <Wallet className="h-5 w-5" /> Wallet
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
                <span>${(item.product.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}

            <div className="border-t pt-3 space-y-2">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>Shipping</span>
                <span>{shippingFee === 0 ? "FREE" : `$${shippingFee}`}</span>
              </div>
              <div className="flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>${total.toFixed(2)}</span>
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
