"use client";

import { useState, useEffect, useCallback } from "react";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import {
  Briefcase, Building, MapPin, Globe, Sparkles,
  RefreshCcw, Search, SlidersHorizontal, X, ChevronDown, Loader2
} from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

const SOURCES = ["All Sources", "RemoteOK", "Remotive", "Adzuna"];
const REMOTE_TYPES = [
  { label: "All Types", value: "" },
  { label: "Remote", value: "REMOTE" },
  { label: "Hybrid", value: "HYBRID" },
  { label: "On-Site", value: "ONSITE" }
];
const SCORE_FILTERS = [
  { label: "All Scores", value: 0 },
  { label: "80%+ Match", value: 80 },
  { label: "60%+ Match", value: 60 },
  { label: "40%+ Match", value: 40 },
];
const STATUS_FILTERS = ["All", "MATCHED", "PARTIAL_MATCHED", "NEW", "SKIPPED"];

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [crawling, setCrawling] = useState(false);
  const [scoring, setScoring] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Filters
  const [globalSearch, setGlobalSearch] = useState("");
  const [search, setSearch] = useState("");
  const [source, setSource] = useState("All Sources");
  const [remoteType, setRemoteType] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [status, setStatus] = useState("All");
  const [sortBy, setSortBy] = useState("score");
  const [page, setPage] = useState(1);

  const buildQuery = useCallback(() => {
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", "24");
    if (search) params.set("search", search);
    if (source !== "All Sources") params.set("source", source);
    if (remoteType) params.set("remote_type", remoteType);
    if (minScore > 0) params.set("min_score", String(minScore));
    if (status !== "All") params.set("status", status);
    params.set("sort_by", sortBy);
    return params.toString();
  }, [search, source, remoteType, minScore, status, sortBy, page]);

  const fetchJobs = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const res = await api.get<any>(`/jobs?${buildQuery()}`);
      setJobs(res.data?.items || []);
      setTotal(res.data?.total || 0);
      return res.data?.total || 0;
    } catch (e) {
      console.error(e);
      return 0;
    } finally {
      if (!silent) setLoading(false);
    }
  }, [buildQuery]);

  useEffect(() => {
    const timer = setTimeout(fetchJobs, 300);
    return () => clearTimeout(timer);
  }, [fetchJobs]);

  const triggerCrawl = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (globalSearch) {
      setSearch(globalSearch);
      setPage(1);
    }
    setCrawling(true);
    try {
      const crawlRes = await api.post<any>("/jobs/crawl", { search: globalSearch });
      const taskId = crawlRes.data?.data;
      if (!taskId) throw new Error("No task ID");
      
      // Poll the true status of the background task
      const poll = setInterval(async () => {
        try {
          const statusRes = await api.get<any>(`/jobs/crawl/status/${taskId}`);
          const status = statusRes.data?.data;
          
          if (status === "SUCCESS" || status === "FAILURE" || status === "REVOKED") {
            clearInterval(poll);
            await fetchJobs(true);
            setCrawling(false);
          }
        } catch (err) {
          clearInterval(poll);
          setCrawling(false);
        }
      }, 2000);
    } catch (e) {
      setCrawling(false);
    }
  };

  const triggerScore = async () => {
    setScoring(true);
    try {
      await api.post("/jobs/score", {});
      setTimeout(fetchJobs, 4000);
    } finally { setScoring(false); }
  };

  const resetFilters = () => {
    setSearch(""); setSource("All Sources");
    setRemoteType(""); setMinScore(0);
    setStatus("All"); setSortBy("score"); setPage(1);
  };

  const hasActiveFilters = search || source !== "All Sources" || remoteType !== "" || minScore > 0 || status !== "All" || sortBy !== "score";

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400 border-emerald-400/30 bg-emerald-400/10";
    if (score >= 60) return "text-yellow-400 border-yellow-400/30 bg-yellow-400/10";
    if (score > 0) return "text-red-400 border-red-400/30 bg-red-400/10";
    return "text-slate-400 border-slate-700 bg-slate-800/50";
  };

  const getStatusColor = (status: string) => {
    if (status === "MATCHED") return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    if (status === "PARTIAL_MATCHED") return "bg-yellow-500/15 text-yellow-400 border-yellow-500/30";
    if (status === "NEW") return "bg-blue-500/15 text-blue-400 border-blue-500/30";
    return "bg-slate-700 text-slate-400 border-slate-600";
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Job Discovery</h1>
          <p className="text-slate-400 mt-1">
            {total > 0 ? <><span className="text-white font-semibold">{total}</span> jobs found</> : "Discover jobs matched to your profile"}
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setShowFilters(f => !f)}
            className={`flex items-center px-4 py-2 text-sm font-medium rounded-lg border transition-all gap-2 ${showFilters || hasActiveFilters ? "bg-blue-600/20 border-blue-500/50 text-blue-300" : "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700"}`}
          >
            <SlidersHorizontal className="w-4 h-4" />
            Filters
            {hasActiveFilters && <span className="w-2 h-2 rounded-full bg-blue-400" />}
          </button>
          <button
            onClick={triggerCrawl} disabled={crawling}
            className="flex items-center px-4 py-2 text-sm font-medium rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition-all gap-2 disabled:opacity-50"
          >
            {crawling ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCcw className="w-4 h-4" />}
            {crawling ? "Crawling..." : "Crawl New Jobs"}
          </button>
          <button
            onClick={triggerScore} disabled={scoring}
            className="flex items-center px-4 py-2 text-sm font-medium rounded-lg bg-gradient-to-r from-blue-600/80 to-purple-600/80 text-white border border-blue-500/30 hover:shadow-lg transition-all gap-2 disabled:opacity-50"
          >
            {scoring ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            {scoring ? "Scoring..." : "AI Score Jobs"}
          </button>
        </div>
      </div>

      {/* Search bar */}
      <form onSubmit={triggerCrawl} className="relative flex items-center">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          value={globalSearch}
          onChange={e => setGlobalSearch(e.target.value)}
          placeholder="Search the web for jobs by title, company, or keyword (Press Enter)..."
          className="w-full pl-10 pr-32 py-3 rounded-xl bg-slate-800/80 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-sm"
        />
        {globalSearch && (
          <button type="button" onClick={() => { setGlobalSearch(""); setSearch(""); setPage(1); }} className="absolute right-32 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white mr-2">
            <X className="w-4 h-4" />
          </button>
        )}
        <button 
          type="submit" 
          disabled={crawling}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {crawling ? <Loader2 className="w-3 h-3 animate-spin" /> : <Globe className="w-3 h-3" />}
          Search Web
        </button>
      </form>

      {/* Advanced Filters Panel */}
      {showFilters && (
        <Card className="p-5 bg-slate-800/60 border-slate-700 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-semibold text-white">Advanced Filters</span>
            {hasActiveFilters && (
              <button onClick={resetFilters} className="text-xs text-slate-400 hover:text-red-400 transition-colors flex items-center gap-1">
                <X className="w-3 h-3" /> Reset all
              </button>
            )}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Source</label>
              <select
                value={source}
                onChange={e => { setSource(e.target.value); setPage(1); }}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                {SOURCES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Work Type</label>
              <select
                value={remoteType}
                onChange={e => { setRemoteType(e.target.value); setPage(1); }}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                {REMOTE_TYPES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Sort By</label>
              <select
                value={sortBy}
                onChange={e => { setSortBy(e.target.value); setPage(1); }}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                <option value="score">Best Match (AI Score)</option>
                <option value="latest">Latest Published</option>
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Min AI Score</label>
              <select
                value={minScore}
                onChange={e => { setMinScore(Number(e.target.value)); setPage(1); }}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                {SCORE_FILTERS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Status</label>
              <select
                value={status}
                onChange={e => { setStatus(e.target.value); setPage(1); }}
                className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
              >
                {STATUS_FILTERS.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
          </div>
        </Card>
      )}

      {/* Active filter badges */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2">
          {search && <Badge className="bg-blue-500/15 text-blue-300 border-blue-500/30 gap-1">Search: {search} <button onClick={() => { setSearch(""); setGlobalSearch(""); setPage(1); }}><X className="w-3 h-3" /></button></Badge>}
          {source !== "All Sources" && <Badge className="bg-slate-700 text-slate-200 border-slate-600 gap-1">{source} <button onClick={() => setSource("All Sources")}><X className="w-3 h-3" /></button></Badge>}
          {remoteType !== "" && <Badge className="bg-slate-700 text-slate-200 border-slate-600 gap-1">{REMOTE_TYPES.find(r => r.value === remoteType)?.label} <button onClick={() => setRemoteType("")}><X className="w-3 h-3" /></button></Badge>}
          {minScore > 0 && <Badge className="bg-emerald-500/15 text-emerald-300 border-emerald-500/30 gap-1">{minScore}%+ score <button onClick={() => setMinScore(0)}><X className="w-3 h-3" /></button></Badge>}
          {status !== "All" && <Badge className="bg-purple-500/15 text-purple-300 border-purple-500/30 gap-1">{status} <button onClick={() => setStatus("All")}><X className="w-3 h-3" /></button></Badge>}
        </div>
      )}

      {/* Job Grid */}
      {crawling ? (
        <Card className="p-14 flex flex-col items-center text-center border-dashed border-slate-700 bg-slate-900/40">
          <Loader2 className="w-12 h-12 text-blue-500 mb-4 animate-spin" />
          <h3 className="text-xl font-semibold text-white mb-2">Searching the web...</h3>
          <p className="text-slate-400 text-sm max-w-md mb-4">
            Our AI is fetching the latest jobs for your query from LinkedIn and other sources. This usually takes about 5 to 10 seconds.
          </p>
        </Card>
      ) : loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="h-44 animate-pulse bg-slate-800/50 border-slate-700/50" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <Card className="p-14 flex flex-col items-center text-center border-dashed border-slate-700 bg-slate-900/40">
          <Briefcase className="w-12 h-12 text-slate-600 mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No jobs found</h3>
          <p className="text-slate-400 text-sm max-w-md mb-4">
            {hasActiveFilters ? "Try adjusting your filters or reset them." : "Click \"Crawl New Jobs\" to discover jobs, or go to Settings to set your preferences."}
          </p>
          {hasActiveFilters && (
            <button onClick={resetFilters} className="px-4 py-2 rounded-lg bg-slate-700 text-white text-sm hover:bg-slate-600">Reset Filters</button>
          )}
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {jobs.map((job) => (
              <Link key={job.id || job._id} href={`/jobs/${job.id || job._id}`}>
                <Card className="h-full p-5 bg-slate-900/50 border-slate-800 hover:border-slate-500 hover:bg-slate-800/60 transition-all duration-200 cursor-pointer group flex flex-col">
                  <div className="flex justify-between items-start gap-2 mb-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-white text-sm leading-snug group-hover:text-blue-300 transition-colors line-clamp-2">{job.title}</h3>
                      <div className="flex items-center gap-1.5 text-slate-400 text-xs mt-1">
                        <Building className="w-3 h-3 shrink-0" />
                        <span className="truncate">{job.company}</span>
                      </div>
                    </div>
                    {job.score > 0 && (
                      <Badge variant="outline" className={`text-xs font-bold shrink-0 ${getScoreColor(job.score)}`}>
                        {Math.round(job.score)}%
                      </Badge>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {job.location && (
                      <span className="flex items-center gap-1 text-xs text-slate-400">
                        <MapPin className="w-3 h-3" />{job.location}
                      </span>
                    )}
                    <span className="flex items-center gap-1 text-xs text-slate-500">
                      <Globe className="w-3 h-3" />{job.remote_type}
                    </span>
                  </div>

                  <div className="flex items-center justify-between mt-auto pt-3 border-t border-slate-800">
                    <Badge variant="outline" className="text-xs border-slate-700 bg-slate-800/80 text-slate-400">{job.source_name}</Badge>
                    <Badge className={`text-xs ${getStatusColor(job.status)}`}>{job.status?.replace(/_/g, " ")}</Badge>
                  </div>
                </Card>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {total > 24 && (
            <div className="flex items-center justify-center gap-3 pt-4">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-sm disabled:opacity-40 hover:bg-slate-700 transition-colors">Previous</button>
              <span className="text-sm text-slate-400">Page <span className="text-white font-semibold">{page}</span> of <span className="text-white font-semibold">{Math.ceil(total / 24)}</span></span>
              <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / 24)} className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 text-sm disabled:opacity-40 hover:bg-slate-700 transition-colors">Next</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
