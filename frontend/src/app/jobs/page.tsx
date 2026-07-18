"use client";

import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Briefcase, Building, MapPin, Globe, Sparkles, RefreshCcw } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [crawling, setCrawling] = useState(false);
  const [scoring, setScoring] = useState(false);

  const [location, setLocation] = useState("");

  const fetchJobs = async () => {
    try {
      const res = await api.get(`/jobs${location ? `?location=${encodeURIComponent(location)}` : ''}`);
      setJobs(res.data.items || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const triggerCrawl = async () => {
    setCrawling(true);
    try {
      await api.post("/jobs/crawl");
      setTimeout(fetchJobs, 3000);
    } finally {
      setCrawling(false);
    }
  };

  const triggerScore = async () => {
    setScoring(true);
    try {
      await api.post("/jobs/score");
      setTimeout(fetchJobs, 3000);
    } finally {
      setScoring(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400 border-emerald-400/30 bg-emerald-400/10";
    if (score >= 60) return "text-yellow-400 border-yellow-400/30 bg-yellow-400/10";
    if (score > 0) return "text-red-400 border-red-400/30 bg-red-400/10";
    return "text-slate-400 border-slate-700 bg-slate-800/50";
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Job Discovery</h1>
          <p className="text-slate-400 mt-1 mb-4">
            Automated sourcing and AI matching.
          </p>
          <div className="flex gap-2">
            <input 
              type="text" 
              placeholder="Filter by location (e.g. US, Remote, London)..."
              className="px-3 py-2 rounded bg-slate-800 border border-slate-700 text-white text-sm w-64 focus:outline-none focus:border-blue-500"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchJobs()}
            />
            <button onClick={fetchJobs} className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm text-white transition-colors">
              Filter
            </button>
          </div>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={triggerCrawl}
            disabled={crawling}
            className="flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 disabled:opacity-50"
          >
            <RefreshCcw className={`w-4 h-4 mr-2 ${crawling ? 'animate-spin' : ''}`} />
            Discover Jobs
          </button>
          <button 
            onClick={triggerScore}
            disabled={scoring}
            className="flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:shadow-lg hover:shadow-blue-500/25 disabled:opacity-50"
          >
            <Sparkles className={`w-4 h-4 mr-2 ${scoring ? 'animate-pulse' : ''}`} />
            Run AI Matcher
          </button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Card key={i} className="h-64 animate-pulse bg-slate-800/50 border-slate-700/50" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-12 text-center border-dashed">
          <div className="w-16 h-16 rounded-full bg-blue-500/10 flex items-center justify-center mb-4">
            <Briefcase className="w-8 h-8 text-blue-400" />
          </div>
          <h3 className="text-xl font-medium text-white mb-2">No jobs found</h3>
          <p className="text-slate-400 max-w-sm mb-6">
            Click "Discover Jobs" to trigger the background crawlers and fetch jobs from RemoteOK and Adzuna.
          </p>
          <button onClick={triggerCrawl} className="px-6 py-2.5 rounded-lg bg-blue-500 text-white font-medium hover:bg-blue-600 transition-colors">
            Start Discovery
          </button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <Link href={`/jobs/${job._id}`} key={job._id}>
              <Card className="h-full flex flex-col p-5 hover:border-slate-600 transition-colors group cursor-pointer">
                <div className="flex justify-between items-start mb-4">
                  <div className="space-y-1">
                    <h3 className="font-semibold text-slate-200 line-clamp-1 group-hover:text-blue-400 transition-colors">{job.title}</h3>
                    <div className="flex items-center text-sm text-slate-400">
                      <Building className="w-3.5 h-3.5 mr-1.5" />
                      {job.company}
                    </div>
                  </div>
                  <div className={`px-2.5 py-1 rounded-full border text-xs font-semibold flex items-center ${getScoreColor(job.score)}`}>
                    <Sparkles className="w-3 h-3 mr-1" />
                    {job.score > 0 ? `${Math.round(job.score)}%` : 'New'}
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  <Badge variant="outline" className="text-slate-300 border-slate-700 bg-slate-800/50">
                    <Globe className="w-3 h-3 mr-1" /> {job.remote_type}
                  </Badge>
                  {job.location && (
                    <Badge variant="outline" className="text-slate-300 border-slate-700 bg-slate-800/50">
                      <MapPin className="w-3 h-3 mr-1" /> {job.location}
                    </Badge>
                  )}
                </div>

                <div className="mt-auto pt-4 border-t border-slate-800 flex justify-between items-center text-sm">
                  <span className="text-slate-500">{job.source_name}</span>
                  <span className="text-slate-400 font-medium">{job.salary_range || 'Salary Unknown'}</span>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
