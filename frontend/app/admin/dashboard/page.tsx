import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, Users, ShoppingCart, TrendingUp } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const stats = [
  {
    title: "Total Revenue",
    value: "$45,231.89",
    change: "+20.1% from last month",
    icon: DollarSign,
  },
  {
    title: "Total Users",
    value: "2,350",
    change: "+180 new users",
    icon: Users,
  },
  {
    title: "Total Orders",
    value: "1,234",
    change: "+12% from last month",
    icon: ShoppingCart,
  },
  {
    title: "Conversion Rate",
    value: "3.2%",
    change: "+0.4% from last month",
    icon: TrendingUp,
  },
];

const activities = [
  { action: "New order received", time: "2 minutes ago", user: "John Doe" },
  { action: "User registered", time: "15 minutes ago", user: "Jane Smith" },
  { action: "Product updated", time: "1 hour ago", user: "Admin" },
  { action: "Order shipped", time: "2 hours ago", user: "Mike Johnson" },
];

export default function DashboardPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">
          Dashboard Overview
        </h1>
        <p className="text-muted-foreground">
          {"Welcome back! Here's what's happening with your shop today."}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">{stat.change}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activities.map((activity, i) => (
                <div key={i} className="flex items-center gap-4 text-sm">
                  <div className="h-2 w-2 rounded-full bg-primary" />
                  <div className="flex-1">
                    <p className="font-medium">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">
                      {activity.user}
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {activity.time}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button asChild className="w-full">
              <Link href="/products">Add New Product</Link>
            </Button>
            <Button asChild variant="outline" className="w-full bg-transparent">
              <Link href="/orders">View Pending Orders</Link>
            </Button>
            <Button asChild variant="outline" className="w-full bg-transparent">
              <Link href="/users">Manage Users</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
