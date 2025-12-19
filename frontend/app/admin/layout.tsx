import type React from "react";
import {
  SidebarProvider,
  SidebarInset,
  // SidebarTrigger,
} from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex min-h-screen w-full">
        <AppSidebar role="admin" />
        <SidebarInset className="flex-1">
          {/* <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
            <SidebarTrigger />
          </header> */}
          <main className="flex-1">{children}</main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
