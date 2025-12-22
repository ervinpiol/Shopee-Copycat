"use client";

import type React from "react";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Button } from "@/components/ui/button";
import { CreditCard, Wallet } from "lucide-react";

export function CheckoutForm() {
  const [paymentMethod, setPaymentMethod] = useState("card");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle checkout
    console.log("Processing checkout...");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Step 1: Contact Information */}
      <Card className="border-2 pt-0 overflow-hidden">
        <CardHeader className="bg-black py-2">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center rounded-sm bg-foreground text-background font-bold">
              1.
            </div>
            <CardTitle className="text-background">
              Contact Information
            </CardTitle>
          </div>
          <CardDescription className="text-background/80">
            We&apos;ll use this to send you order updates
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label
                  htmlFor="firstName"
                  className="uppercase text-xs font-bold tracking-wider"
                >
                  First Name
                </Label>
                <Input
                  id="firstName"
                  placeholder="Jane"
                  className="border-2"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label
                  htmlFor="lastName"
                  className="uppercase text-xs font-bold tracking-wider"
                >
                  Last Name
                </Label>
                <Input
                  id="lastName"
                  placeholder="Doe"
                  className="border-2"
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="email"
                className="uppercase text-xs font-bold tracking-wider"
              >
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="jane.doe@example.com"
                className="border-2"
                required
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Step 2: Shipping Address */}
      <Card className="border-2 pt-0 overflow-hidden">
        <CardHeader className="bg-black py-2">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center rounded-sm bg-foreground text-background font-bold">
              2.
            </div>
            <CardTitle className="text-background">Shipping Address</CardTitle>
          </div>
          <CardDescription className="text-background/80">
            Where should we deliver your order?
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label
                htmlFor="address"
                className="uppercase text-xs font-bold tracking-wider"
              >
                Street Address
              </Label>
              <Input
                id="address"
                placeholder="123 Main Street"
                className="border-2"
                required
              />
            </div>
            <div className="space-y-2">
              <Label
                htmlFor="apartment"
                className="uppercase text-xs font-bold tracking-wider"
              >
                Apartment, Suite, etc. (Optional)
              </Label>
              <Input id="apartment" placeholder="Apt 4B" className="border-2" />
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-2">
                <Label
                  htmlFor="city"
                  className="uppercase text-xs font-bold tracking-wider"
                >
                  City
                </Label>
                <Input
                  id="city"
                  placeholder="New York"
                  className="border-2"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label
                  htmlFor="state"
                  className="uppercase text-xs font-bold tracking-wider"
                >
                  Province
                </Label>
                <Input
                  id="province"
                  placeholder="NY"
                  className="border-2"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label
                  htmlFor="zipCode"
                  className="uppercase text-xs font-bold tracking-wider"
                >
                  Zip Code
                </Label>
                <Input
                  id="zipCode"
                  placeholder="10001"
                  className="border-2"
                  required
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Step 3: Payment Method */}
      <Card className="border-2 pt-0 overflow-hidden">
        <CardHeader className="bg-black py-2">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center rounded-sm bg-foreground text-background font-bold">
              3.
            </div>
            <CardTitle className="text-background">Payment Method</CardTitle>
          </div>
          <CardDescription className="text-background/80">
            All transactions are secure and encrypted
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <RadioGroup value={paymentMethod} onValueChange={setPaymentMethod}>
              <div className="flex items-center space-x-3 rounded-sm border-2 p-4 cursor-pointer hover:bg-muted/50 transition-colors">
                <RadioGroupItem value="card" id="card" />
                <Label
                  htmlFor="card"
                  className="flex flex-1 items-center gap-2 cursor-pointer"
                >
                  <CreditCard className="h-5 w-5" />
                  <span className="font-semibold">Credit / Debit Card</span>
                </Label>
              </div>
              <div className="flex items-center space-x-3 rounded-sm border-2 p-4 cursor-pointer hover:bg-muted/50 transition-colors">
                <RadioGroupItem value="wallet" id="wallet" />
                <Label
                  htmlFor="wallet"
                  className="flex flex-1 items-center gap-2 cursor-pointer"
                >
                  <Wallet className="h-5 w-5" />
                  <span className="font-semibold">Digital Wallet</span>
                </Label>
              </div>
            </RadioGroup>

            {paymentMethod === "card" && (
              <div className="space-y-4 pt-4 border-t-2">
                <div className="space-y-2">
                  <Label
                    htmlFor="cardNumber"
                    className="uppercase text-xs font-bold tracking-wider"
                  >
                    Card Number
                  </Label>
                  <Input
                    id="cardNumber"
                    placeholder="1234 5678 9012 3456"
                    className="border-2"
                    required
                  />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label
                      htmlFor="expiry"
                      className="uppercase text-xs font-bold tracking-wider"
                    >
                      Expiry Date
                    </Label>
                    <Input
                      id="expiry"
                      placeholder="MM/YY"
                      className="border-2"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label
                      htmlFor="cvv"
                      className="uppercase text-xs font-bold tracking-wider"
                    >
                      CVV
                    </Label>
                    <Input
                      id="cvv"
                      placeholder="123"
                      className="border-2"
                      required
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Button type="submit" className="w-full">
        Complete Purchase
      </Button>
    </form>
  );
}
