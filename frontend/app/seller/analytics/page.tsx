import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  ShoppingBag,
} from "lucide-react";

const metrics = [
  { title: "Revenue Growth", value: "+24.5%", trend: "up", icon: TrendingUp },
  { title: "Order Volume", value: "+12.3%", trend: "up", icon: ShoppingBag },
  { title: "Avg Order Value", value: "$87.50", trend: "up", icon: DollarSign },
  { title: "Return Rate", value: "-2.1%", trend: "down", icon: TrendingDown },
];

const topProducts = [
  { name: "Wireless Headphones", sales: 234, revenue: "$30,366" },
  { name: "Smart Watch", sales: 189, revenue: "$56,681" },
  { name: "Mechanical Keyboard", sales: 156, revenue: "$24,958" },
  { name: "USB-C Cable", sales: 423, revenue: "$8,458" },
];

const salesByCategory = [
  { category: "Electronics", percentage: 65, amount: "$89,234" },
  { category: "Accessories", percentage: 25, amount: "$34,567" },
  { category: "Clothing", percentage: 10, amount: "$13,825" },
];

export default function AnalyticsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">
          Track your shop performance and insights
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <Card key={metric.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {metric.title}
                </CardTitle>
                <Icon
                  className={`h-4 w-4 ${
                    metric.trend === "up" ? "text-green-600" : "text-red-600"
                  }`}
                />
              </CardHeader>
              <CardContent>
                <div
                  className={`text-2xl font-bold ${
                    metric.trend === "up" ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {metric.value}
                </div>
                <p className="text-xs text-muted-foreground">vs last period</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Products</CardTitle>
            <CardDescription>Best selling products this month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topProducts.map((product, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{product.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {product.sales} sales
                    </p>
                  </div>
                  <p className="font-semibold">{product.revenue}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Sales by Category</CardTitle>
            <CardDescription>Revenue breakdown by category</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {salesByCategory.map((item, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{item.category}</span>
                    <span className="text-muted-foreground">{item.amount}</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
