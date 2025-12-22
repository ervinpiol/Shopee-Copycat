import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

const orderItems = [
  {
    id: 1,
    name: "Premium Wireless Headphones",
    price: 299.99,
    quantity: 1,
    image: "/wireless-headphones.png",
  },
  {
    id: 2,
    name: "USB-C Charging Cable",
    price: 24.99,
    quantity: 2,
    image: "/usb-cable.png",
  },
];

export function OrderSummary() {
  const subtotal = orderItems.reduce(
    (acc, item) => acc + item.price * item.quantity,
    0
  );
  const shipping = 15.0;
  const tax = subtotal * 0.08;
  const total = subtotal + shipping + tax;

  return (
    <Card className="border-2 sticky top-8 pt-0 overflow-hidden">
      <CardHeader className="bg-black py-4">
        <CardTitle className="text-background">Order Summary</CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {orderItems.map((item) => (
            <div key={item.id} className="flex gap-4">
              <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-sm border-2">
                <img
                  src={item.image || "/placeholder.svg"}
                  alt={item.name}
                  className="h-full w-full object-cover"
                />
                <div className="absolute -right-2 -top-2 flex h-6 w-6 items-center justify-center rounded-full bg-secondary text-xs font-bold text-background">
                  {item.quantity}
                </div>
              </div>
              <div className="flex flex-1 flex-col justify-between">
                <div>
                  <h3 className="text-sm font-semibold leading-tight">
                    {item.name}
                  </h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    Qty: {item.quantity}
                  </p>
                </div>
                <p className="text-sm font-bold">
                  ${(item.price * item.quantity).toFixed(2)}
                </p>
              </div>
            </div>
          ))}
        </div>

        <Separator className="my-6" />

        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Subtotal</span>
            <span className="font-medium">${subtotal.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Shipping</span>
            <span className="font-medium">${shipping.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Tax</span>
            <span className="font-medium">${tax.toFixed(2)}</span>
          </div>
        </div>

        <Separator className="my-4" />

        <div className="flex justify-between">
          <span className="text-lg font-bold uppercase tracking-wider">
            Total
          </span>
          <span className="text-2xl font-bold">${total.toFixed(2)}</span>
        </div>
      </CardContent>
    </Card>
  );
}
