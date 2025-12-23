"use client";

import CheckoutForm from "@/components/checkout-form";
import { OrderSummary } from "@/components/order-summary";

export default function Main() {
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

      <CheckoutForm />
    </div>
  );
}
