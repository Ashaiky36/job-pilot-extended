"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "motion/react";
import {
  getCompanies,
  addCompany,
  removeCompany,
  type Company,
} from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  Building2,
  Plus,
  Trash2,
  ExternalLink,
  Loader2,
  CheckCircle2,
  XCircle,
  Globe,
} from "lucide-react";

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [careersUrl, setCareersUrl] = useState("");
  const [adding, setAdding] = useState(false);
  const [status, setStatus] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);

  const loadCompanies = useCallback(async () => {
    try {
      const data = await getCompanies();
      setCompanies(data.companies);
    } catch (err) {
      console.error("Companies load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCompanies();
  }, [loadCompanies]);

  const handleAdd = async () => {
    if (!name.trim()) {
      setStatus({ message: "Please enter a company name", type: "error" });
      return;
    }

    setAdding(true);
    setStatus(null);
    try {
      const data = await addCompany(name.trim(), careersUrl.trim());
      setStatus({ message: data.message, type: data.crawlable ? "success" : "error" });
      setName("");
      setCareersUrl("");
      loadCompanies();
    } catch (err) {
      setStatus({
        message: `Failed: ${err instanceof Error ? err.message : "Unknown error"}`,
        type: "error",
      });
    } finally {
      setAdding(false);
    }
  };

  const handleRemove = async (companyId: number) => {
    try {
      await removeCompany(companyId);
      loadCompanies();
    } catch (err) {
      console.error("Remove failed:", err);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Add Company Form */}
      <Card className="p-5 shadow-none border">
        <h2 className="text-sm font-semibold text-foreground mb-1">
          Track a Company
        </h2>
        <p className="text-[11px] text-muted-foreground mb-4">
          Add companies to monitor their career pages. JobPilot will check if
          jobs can be fetched automatically.
        </p>

        <div className="flex flex-col sm:flex-row gap-2 max-w-xl">
          <Input
            placeholder="Company name (e.g. Swiggy)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="h-9 text-xs"
          />
          <Input
            placeholder="Careers URL (optional)"
            value={careersUrl}
            onChange={(e) => setCareersUrl(e.target.value)}
            className="h-9 text-xs"
          />
          <Button
            onClick={handleAdd}
            disabled={adding}
            size="sm"
            className="h-9 px-4 text-xs gap-1.5 whitespace-nowrap"
          >
            {adding ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Plus className="w-3.5 h-3.5" />
            )}
            Add Company
          </Button>
        </div>

        {status && (
          <div
            className={cn(
              "flex items-center gap-2 mt-3 px-3 py-2 rounded-lg text-xs font-medium",
              status.type === "success"
                ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                : "bg-red-50 text-red-700 border border-red-100"
            )}
          >
            {status.type === "success" ? (
              <CheckCircle2 className="w-3.5 h-3.5" />
            ) : (
              <XCircle className="w-3.5 h-3.5" />
            )}
            {status.message}
          </div>
        )}
      </Card>

      {/* Companies List */}
      <div>
        <p className="text-[11px] text-muted-foreground mb-3">
          {companies.length} {companies.length === 1 ? "company" : "companies"} tracked
        </p>

        {loading ? (
          <div className="space-y-3">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-20 rounded-xl bg-muted animate-pulse" />
            ))}
          </div>
        ) : companies.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center mx-auto mb-3">
              <Building2 className="w-5 h-5 text-muted-foreground" />
            </div>
            <p className="text-sm font-medium text-foreground">
              No companies tracked
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Add companies above to start monitoring their career pages.
            </p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {companies.map((company, i) => (
              <motion.div
                key={company.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: i * 0.03 }}
              >
                <Card className="p-4 shadow-none border hover:shadow-md transition-shadow duration-200">
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                          <Building2 className="w-3.5 h-3.5 text-primary" />
                        </div>
                        <div className="min-w-0">
                          <h3 className="text-[13px] font-semibold text-foreground truncate">
                            {company.name}
                          </h3>
                          {company.careers_url ? (
                            <a
                              href={company.careers_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 text-[10px] text-primary hover:underline truncate"
                            >
                              <Globe className="w-2.5 h-2.5 shrink-0" />
                              {company.careers_url}
                            </a>
                          ) : (
                            <span className="text-[10px] text-muted-foreground">
                              No URL found
                            </span>
                          )}
                        </div>
                      </div>
                      {company.note && (
                        <p className="text-[10px] text-muted-foreground mt-1.5 ml-9">
                          {company.note}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <Badge
                        variant="secondary"
                        className={cn(
                          "text-[10px] font-medium",
                          company.crawlable
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                            : "bg-amber-50 text-amber-700 border-amber-200"
                        )}
                      >
                        {company.crawlable ? "✓ Trackable" : "⚠ Manual"}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-muted-foreground hover:text-red-500"
                        onClick={() => handleRemove(company.id)}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}
