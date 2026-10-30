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
  LogOut,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/jobs", label: "Jobs", icon: Briefcase },
  { href: "/applications", label: "Applications", icon: ClipboardList },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/resume", label: "Resume", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="hidden md:flex flex-col w-[240px] min-h-screen bg-sidebar border-r border-sidebar-border">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 h-14 border-b border-sidebar-border">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-sidebar-primary/20">
          <Plane className="w-4 h-4 text-sidebar-primary" />
        </div>
        <span className="text-[15px] font-bold tracking-tight text-sidebar-foreground">
          JobPilot
        </span>
        <span className="ml-auto text-[10px] font-medium text-sidebar-primary bg-sidebar-primary/15 px-1.5 py-0.5 rounded-md">
          PRO
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-200",
                isActive
                  ? "bg-sidebar-primary/15 text-sidebar-primary shadow-sm"
                  : "text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent"
              )}
            >
              <item.icon className={cn("w-4 h-4", isActive && "text-sidebar-primary")} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* User + Logout */}
      <div className="px-3 pb-4 space-y-2">
        {user && (
          <div className="rounded-lg bg-sidebar-accent/50 border border-sidebar-border p-3">
            <p className="text-[12px] font-medium text-sidebar-foreground truncate">
              {user.name}
            </p>
            <p className="text-[10px] text-sidebar-foreground/50 truncate">
              {user.email}
            </p>
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-[12px] font-medium text-sidebar-foreground/50 hover:text-red-400 hover:bg-sidebar-accent transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
