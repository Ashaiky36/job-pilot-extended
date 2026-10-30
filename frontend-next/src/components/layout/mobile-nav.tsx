"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import {
  LayoutDashboard,
  Briefcase,
  ClipboardList,
  Building2,
  FileText,
  Plane,
  Menu,
  LogOut,
} from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/jobs", label: "Jobs", icon: Briefcase },
  { href: "/applications", label: "Applications", icon: ClipboardList },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/resume", label: "Resume", icon: FileText },
];

export function MobileNav() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);

  return (
    <div className="md:hidden flex items-center h-14 px-4 border-b border-border bg-sidebar">
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger
          render={
            <Button variant="ghost" size="icon" className="text-sidebar-foreground">
              <Menu className="w-5 h-5" />
            </Button>
          }
        />
        <SheetContent side="left" className="w-[260px] bg-sidebar border-sidebar-border p-0">
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <div className="flex items-center gap-2.5 px-5 h-14 border-b border-sidebar-border">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-sidebar-primary/20">
              <Plane className="w-4 h-4 text-sidebar-primary" />
            </div>
            <span className="text-[15px] font-bold tracking-tight text-sidebar-foreground">
              JobPilot
            </span>
          </div>
          <nav className="px-3 py-4 space-y-1">
            {navItems.map((item) => {
              const isActive =
                pathname === item.href ||
                (item.href !== "/dashboard" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all",
                    isActive
                      ? "bg-sidebar-primary/15 text-sidebar-primary"
                      : "text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent"
                  )}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
          {user && (
            <div className="px-3 mt-auto pb-4">
              <div className="rounded-lg bg-sidebar-accent/50 border border-sidebar-border p-3 mb-2">
                <p className="text-[12px] font-medium text-sidebar-foreground truncate">
                  {user.name}
                </p>
                <p className="text-[10px] text-sidebar-foreground/50 truncate">
                  {user.email}
                </p>
              </div>
              <button
                onClick={() => { setOpen(false); logout(); }}
                className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-[12px] font-medium text-sidebar-foreground/50 hover:text-red-400 hover:bg-sidebar-accent transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sign Out
              </button>
            </div>
          )}
        </SheetContent>
      </Sheet>
      <div className="flex items-center gap-2 ml-3">
        <Plane className="w-4 h-4 text-sidebar-primary" />
        <span className="text-sm font-bold text-sidebar-foreground">JobPilot</span>
      </div>
    </div>
  );
}
