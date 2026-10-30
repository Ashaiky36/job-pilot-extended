"use client";

import Link from "next/link";
import { motion } from "motion/react";
import {
  Plane,
  Search,
  Cpu,
  Target,
  Bell,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Shield,
  BarChart3,
  Zap,
  FileText,
  Building2,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const fadeUp = {
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
};

const features = [
  {
    icon: Search,
    title: "Multi-Source Scanning",
    description:
      "Continuously monitors LinkedIn, Indeed, Glassdoor, and company career pages. Never miss an opportunity.",
    color: "from-blue-500 to-indigo-600",
  },
  {
    icon: Cpu,
    title: "AI-Powered Matching",
    description:
      "Gemini AI analyzes your resume and scores each job for relevance, skills match, and career fit.",
    color: "from-violet-500 to-purple-600",
  },
  {
    icon: Target,
    title: "Smart Prioritization",
    description:
      "Automatically categorizes matches as High Priority, Review, or Skip based on your profile.",
    color: "from-emerald-500 to-teal-600",
  },
  {
    icon: Bell,
    title: "Instant Alerts",
    description:
      "Get notified the moment a high-match job appears. Apply while positions are fresh.",
    color: "from-amber-500 to-orange-600",
  },
];

const steps = [
  {
    step: "01",
    title: "Upload Your Resume",
    description: "Drop your resume and let AI extract your skills, experience, and preferences.",
    icon: FileText,
  },
  {
    step: "02",
    title: "AI Scans & Matches",
    description: "JobPilot fetches jobs from 10+ sources and scores each against your profile.",
    icon: Sparkles,
  },
  {
    step: "03",
    title: "Review & Apply",
    description: "Focus only on top matches. One-click apply with tailored cover letters.",
    icon: CheckCircle2,
  },
];

const stats = [
  { value: "10+", label: "Job Sources" },
  { value: "95%", label: "Match Accuracy" },
  { value: "3x", label: "Faster Applications" },
  { value: "24/7", label: "Monitoring" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* ── Navbar ────────────────────────────────────────────────── */}
      <nav className="fixed top-0 inset-x-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-100">
        <div className="max-w-6xl mx-auto flex items-center justify-between h-16 px-6">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
              <Plane className="w-4 h-4 text-white" />
            </div>
            <span className="text-[16px] font-bold text-slate-900 tracking-tight">
              JobPilot
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="text-xs text-slate-600 hover:text-slate-900">
                Sign In
              </Button>
            </Link>
            <Link href="/login?tab=register">
              <Button size="sm" className="text-xs bg-indigo-600 hover:bg-indigo-700 text-white gap-1.5">
                Get Started
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────────────────── */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-50/80 via-white to-violet-50/60" />
        <div className="absolute top-20 -right-40 w-[600px] h-[600px] rounded-full bg-gradient-to-br from-indigo-200/30 to-violet-200/20 blur-3xl" />
        <div className="absolute bottom-0 -left-40 w-[500px] h-[500px] rounded-full bg-gradient-to-tr from-blue-200/20 to-indigo-200/10 blur-3xl" />

        <div className="relative max-w-4xl mx-auto text-center">
          <motion.div
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 mb-6"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span className="text-[12px] font-semibold text-indigo-700">
              Powered by Gemini AI
            </span>
          </motion.div>

          <motion.h1
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.1]"
          >
            Stop Scrolling.
            <br />
            <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 bg-clip-text text-transparent">
              Start Landing.
            </span>
          </motion.h1>

          <motion.p
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-6 text-base sm:text-lg text-slate-500 max-w-2xl mx-auto leading-relaxed"
          >
            JobPilot monitors job boards 24/7, matches listings against your resume
            using AI, and surfaces only the roles worth your time. What used to take
            hours now takes minutes.
          </motion.p>

          <motion.div
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3"
          >
            <Link href="/login?tab=register">
              <Button
                size="lg"
                className="px-8 h-12 text-sm bg-indigo-600 hover:bg-indigo-700 text-white gap-2 shadow-lg shadow-indigo-200"
              >
                <Zap className="w-4 h-4" />
                Get Started — Free
              </Button>
            </Link>
            <Link href="#features">
              <Button
                variant="outline"
                size="lg"
                className="px-8 h-12 text-sm border-slate-200 text-slate-600 hover:text-slate-900"
              >
                See How It Works
              </Button>
            </Link>
          </motion.div>

          {/* Stats row */}
          <motion.div
            {...fadeUp}
            transition={{ duration: 0.6, delay: 0.55 }}
            className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-6 max-w-2xl mx-auto"
          >
            {stats.map((s) => (
              <div key={s.label} className="text-center">
                <p className="text-2xl sm:text-3xl font-extrabold text-slate-900">
                  {s.value}
                </p>
                <p className="text-[11px] font-medium text-slate-400 mt-0.5 uppercase tracking-wider">
                  {s.label}
                </p>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────── */}
      <section id="features" className="py-20 px-6 bg-slate-50/50">
        <div className="max-w-5xl mx-auto">
          <motion.div
            {...fadeUp}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            whileInView="animate"
            initial="initial"
            className="text-center mb-14"
          >
            <span className="text-[11px] font-bold text-indigo-600 uppercase tracking-widest">
              Features
            </span>
            <h2 className="mt-2 text-2xl sm:text-3xl font-bold text-slate-900">
              Everything You Need to Land Faster
            </h2>
            <p className="mt-3 text-sm text-slate-500 max-w-lg mx-auto">
              From automatic job discovery to AI-powered matching, JobPilot handles
              the busywork so you can focus on what matters.
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 gap-5">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                className="group relative rounded-2xl bg-white border border-slate-100 p-6 hover:shadow-xl hover:shadow-slate-100/80 transition-all duration-300"
              >
                <div
                  className={`w-10 h-10 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 shadow-lg shadow-indigo-100/50`}
                >
                  <f.icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-[15px] font-semibold text-slate-900">
                  {f.title}
                </h3>
                <p className="mt-1.5 text-[13px] text-slate-500 leading-relaxed">
                  {f.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────────────── */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            {...fadeUp}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            whileInView="animate"
            initial="initial"
            className="text-center mb-14"
          >
            <span className="text-[11px] font-bold text-indigo-600 uppercase tracking-widest">
              How It Works
            </span>
            <h2 className="mt-2 text-2xl sm:text-3xl font-bold text-slate-900">
              Three Steps to Your Next Role
            </h2>
          </motion.div>

          <div className="space-y-8">
            {steps.map((s, i) => (
              <motion.div
                key={s.step}
                initial={{ opacity: 0, x: i % 2 === 0 ? -24 : 24 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
                className="flex items-start gap-5 p-6 rounded-2xl bg-white border border-slate-100 hover:shadow-lg hover:shadow-slate-100/60 transition-all"
              >
                <div className="shrink-0 w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center">
                  <span className="text-sm font-bold text-indigo-600">{s.step}</span>
                </div>
                <div>
                  <h3 className="text-[15px] font-semibold text-slate-900 flex items-center gap-2">
                    <s.icon className="w-4 h-4 text-indigo-500" />
                    {s.title}
                  </h3>
                  <p className="mt-1 text-[13px] text-slate-500 leading-relaxed">
                    {s.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Trust Bar ─────────────────────────────────────────────── */}
      <section className="py-12 px-6 bg-slate-50/50 border-y border-slate-100">
        <div className="max-w-4xl mx-auto flex flex-wrap items-center justify-center gap-x-10 gap-y-4 text-[12px] text-slate-400">
          <span className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5" /> End-to-end encrypted
          </span>
          <span className="flex items-center gap-1.5">
            <BarChart3 className="w-3.5 h-3.5" /> Real-time analytics
          </span>
          <span className="flex items-center gap-1.5">
            <Building2 className="w-3.5 h-3.5" /> Company tracking
          </span>
          <span className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> Gemini AI powered
          </span>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────────────── */}
      <section className="py-20 px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="max-w-3xl mx-auto text-center rounded-3xl bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700 p-12 relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.1),transparent)]" />
          <div className="relative">
            <h2 className="text-2xl sm:text-3xl font-bold text-white">
              Ready to Automate Your Job Search?
            </h2>
            <p className="mt-3 text-sm text-white/70 max-w-lg mx-auto">
              Join JobPilot and let AI handle the grunt work. Upload your resume, set
              your preferences, and start receiving curated matches in minutes.
            </p>
            <Link href="/login?tab=register">
              <Button
                size="lg"
                className="mt-8 px-8 h-12 text-sm bg-white text-indigo-700 hover:bg-slate-50 gap-2 shadow-xl"
              >
                Create Your Account
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* ── Footer ────────────────────────────────────────────────── */}
      <footer className="py-8 px-6 border-t border-slate-100">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-indigo-600 flex items-center justify-center">
              <Plane className="w-3 h-3 text-white" />
            </div>
            <span className="text-[13px] font-semibold text-slate-700">JobPilot</span>
          </div>
          <p className="text-[11px] text-slate-400">
            © 2026 JobPilot. AI-powered job discovery.
          </p>
        </div>
      </footer>
    </div>
  );
}
