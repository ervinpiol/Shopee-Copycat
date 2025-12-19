"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarHeader,
  SidebarFooter,
} from "@/components/ui/sidebar";
import {
  LayoutDashboard,
  Users,
  ShoppingCart,
  Package,
  BarChart3,
  Settings,
} from "lucide-react";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<any>;
}

const adminNavItems: NavItem[] = [
  { href: "/admin/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/analytics", label: "Analytics", icon: BarChart3 },
];

const sellerNavItems: NavItem[] = [
  { href: "/seller/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/seller/orders", label: "Orders", icon: ShoppingCart },
  { href: "/seller/products", label: "Products", icon: Package },
  { href: "/seller/analytics", label: "Analytics", icon: BarChart3 },
];

interface AppSidebarProps {
  role: "admin" | "seller";
}

export function AppSidebar({ role }: AppSidebarProps) {
  const pathname = usePathname();
  const navItems = role === "admin" ? adminNavItems : sellerNavItems;

  return (
    <Sidebar side="left" variant="sidebar">
      <SidebarHeader className="border-b px-6 py-4">
        <div className="flex items-center gap-2">
          <Link href="/">
            <div className="h-8 w-8 rounded-lg bg-primary" />
          </Link>
          <span className="text-lg font-semibold">
            {role === "admin" ? "Admin Panel" : "Seller Panel"}
          </span>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      asChild
                      isActive={pathname === item.href}
                      tooltip={item.label}
                    >
                      <Link href={item.href}>
                        <Icon />
                        <span>{item.label}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild tooltip="Settings">
              <Link href={`/${role}/settings`}>
                <Settings />
                <span>Settings</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
