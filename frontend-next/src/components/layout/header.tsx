"use client";

import { usePathname } from "next/navigation";
import { Bell, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  "/": { title: "Dashboard", subtitle: "Overview of your job search pipeline" },
  "/jobs": { title: "Job Matches", subtitle: "AI-matched jobs ranked by relevance" },
  "/applications": { title: "Applications", subtitle: "Track your job application status" },
  "/companies": { title: "Companies", subtitle: "Monitor company career pages" },
  "/resume": { title: "Resume", subtitle: "Manage your resume profiles" },
};

export function Header() {
  const pathname = usePathname();
  const page = pageTitles[pathname] || pageTitles["/"];

  return (
    <header className="sticky top-0 z-30 flex items-center h-14 px-6 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="flex-1 min-w-0">
        <h1 className="text-[15px] font-semibold text-foreground truncate">
          {page.title}
        </h1>
        <p className="text-[11px] text-muted-foreground truncate">
          {page.subtitle}
        </p>
      </div>

      <div className="flex items-center gap-2 ml-4">
        <div className="relative hidden lg:block">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
          <Input
            placeholder="Search jobs..."
            className="w-[200px] h-8 pl-8 text-xs bg-muted/50 border-transparent focus:border-border"
          />
        </div>
        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground">
          <Bell className="w-4 h-4" />
        </Button>
        <div className="w-7 h-7 rounded-full bg-primary/15 flex items-center justify-center">
          <span className="text-[11px] font-semibold text-primary">A</span>
        </div>
      </div>
    </header>
  );
}
