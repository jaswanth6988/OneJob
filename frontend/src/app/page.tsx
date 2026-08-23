"use client";

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Briefcase, Send, Target, ChevronRight, Activity, Loader2 } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    resumes: 0,
    jobs: 0,
    applications: 0,
    matched: 0,
  });
  const [userName, setUserName] = useState("there");
  const [loading, setLoading] = useState(true);
  const [recentJobs, setRecentJobs] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        // Load in parallel
        const [resumesRes, jobsRes, appsRes, prefsRes] = await Promise.allSettled([
          api.get<any>("/resumes"),
          api.get<any>("/jobs?page_size=5&page=1"),
          api.applications.list(),
          api.get<any>("/preferences"),
        ]);

        if (resumesRes.status === "fulfilled") {
          setStats(s => ({ ...s, resumes: (resumesRes.value.data || []).length }));
        }
        if (jobsRes.status === "fulfilled") {
          const data = jobsRes.value.data;
          setStats(s => ({ ...s, jobs: data?.total || 0, matched: data?.items?.filter((j: any) => j.score >= 60).length || 0 }));
          setRecentJobs(data?.items?.slice(0, 4) || []);
        }
        if (appsRes.status === "fulfilled") {
          setStats(s => ({ ...s, applications: (appsRes.value.data || []).length }));
        }
        if (prefsRes.status === "fulfilled") {
          const name = prefsRes.value.data?.name;
          if (name) setUserName(name.split(" ")[0]);
        }
      } catch (e) {
        console.error("Dashboard load error:", e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const statCards = [
    { label: "Resumes", value: stats.resumes, icon: FileText, color: "text-blue-400", bg: "bg-blue-400/10", href: "/resumes" },
    { label: "Jobs Discovered", value: stats.jobs, icon: Briefcase, color: "text-purple-400", bg: "bg-purple-400/10", href: "/jobs" },
    { label: "Applications Sent", value: stats.applications, icon: Send, color: "text-teal-400", bg: "bg-teal-400/10", href: "/applications" },
    { label: "60%+ Matches", value: stats.matched, icon: Target, color: "text-emerald-400", bg: "bg-emerald-400/10", href: "/jobs?min_score=60" },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2 text-white">
          Welcome back, <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">{loading ? "..." : userName}</span>
        </h1>
        <p className="text-slate-400">Here's what's happening with your job search today.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <Link key={stat.label} href={stat.href}>
            <Card className="p-6 hover:border-slate-600 transition-all cursor-pointer group">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg ${stat.bg}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-400">{stat.label}</p>
                  {loading
                    ? <div className="h-7 w-10 bg-slate-700 rounded animate-pulse mt-1" />
                    : <p className="text-2xl font-bold text-slate-100">{stat.value}</p>
                  }
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* CTA */}
        <Card className="lg:col-span-2 p-6 flex flex-col justify-center bg-gradient-to-br from-slate-800/60 to-slate-900/60 border-slate-700">
          <h2 className="text-xl font-semibold mb-2 text-white">Ready to accelerate your search?</h2>
          <p className="text-slate-400 mb-6 max-w-lg">
            Let our AI analyze your resume and automatically find and apply to the best matching jobs while you sleep.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link href="/resumes">
              <Button size="lg" className="gap-2">
                Upload New Resume <ChevronRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/settings?tab=crawl">
              <Button variant="secondary" size="lg">Discover Jobs</Button>
            </Link>
          </div>
        </Card>

        {/* Recent Jobs */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2 text-white">
              <Activity className="h-4 w-4 text-blue-400" />
              Recent Jobs
            </h3>
            <Link href="/jobs" className="text-xs text-blue-400 hover:text-blue-300 transition-colors">View all →</Link>
          </div>
          <div className="space-y-3">
            {loading
              ? [1, 2, 3, 4].map(i => <div key={i} className="h-10 bg-slate-800 rounded animate-pulse" />)
              : recentJobs.length === 0
                ? <p className="text-sm text-slate-500 text-center py-4">No jobs yet. <Link href="/settings" className="text-blue-400 hover:underline">Discover jobs →</Link></p>
                : recentJobs.map((job) => (
                  <Link key={job._id} href={`/jobs/${job._id}`}>
                    <div className="flex items-start gap-2 p-2 rounded-lg hover:bg-slate-800/50 transition-colors group">
                      <div className="mt-1.5 h-2 w-2 rounded-full bg-blue-500 shrink-0 shadow-[0_0_8px_rgba(59,130,246,0.6)]" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-200 truncate group-hover:text-white">{job.title}</p>
                        <p className="text-xs text-slate-500">{job.company}</p>
                      </div>
                      {job.score > 0 && (
                        <span className={`text-xs font-bold shrink-0 ${job.score >= 80 ? "text-emerald-400" : job.score >= 60 ? "text-yellow-400" : "text-slate-400"}`}>
                          {Math.round(job.score)}%
                        </span>
                      )}
                    </div>
                  </Link>
                ))
            }
          </div>
        </Card>
      </div>
    </div>
  );
}
