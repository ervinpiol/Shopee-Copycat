"use client";

import Main from "./main";

export default function OrdersPage() {
  return (
    <div className="container mx-auto max-w-7xl p-6 md:p-8">
      <div className="mb-8">
        <h1 className="mb-2 text-4xl font-bold tracking-tight">
          Orders Management
        </h1>
        <p className="text-lg text-muted-foreground">
          Track and manage all shop orders
        </p>
      </div>

      <Main />
    </div>
  );
}
