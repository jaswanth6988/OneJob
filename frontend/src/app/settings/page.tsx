"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge } from "@/components/ui/Badge";
import {
  Settings, User, Target, Briefcase, MapPin, DollarSign,
  Building, Github, Linkedin, Globe, Plus, X, Save,
  CheckCircle, Loader2, RefreshCw, Zap
} from "lucide-react";
import { api } from "@/lib/api";

type Tab = "profile" | "jobprefs" | "crawl";

function TagInput({
  label, values, onChange, placeholder
}: { label: string; values: string[]; onChange: (v: string[]) => void; placeholder: string }) {
  const [input, setInput] = useState("");
  const add = () => {
    const trimmed = input.trim();
    if (trimmed && !values.includes(trimmed)) {
      onChange([...values, trimmed]);
    }
    setInput("");
  };
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-slate-300">{label}</label>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && (e.preventDefault(), add())}
          placeholder={placeholder}
          className="flex-1 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-blue-500"
        />
        <button onClick={add} className="px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm transition-colors">
          <Plus className="w-4 h-4" />
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {values.map((v, i) => (
          <Badge key={i} className="bg-slate-700 text-slate-200 border-slate-600 gap-1.5 pr-1">
            {v}
            <button onClick={() => onChange(values.filter((_, idx) => idx !== i))} className="hover:text-red-400 transition-colors">
              <X className="w-3 h-3" />
            </button>
          </Badge>
        ))}
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const [tab, setTab] = useState<Tab>("profile");
  const [prefs, setPrefs] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [crawling, setCrawling] = useState(false);
  const [crawlMsg, setCrawlMsg] = useState("");

  useEffect(() => {
    api.get<any>("/preferences").then(r => {
      setPrefs(r.data || {});
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const set = (key: string, val: any) => setPrefs((p: any) => ({ ...p, [key]: val }));

  const save = async () => {
    setSaving(true); setSaved(false); setError("");
    try {
      await api.put("/preferences", prefs);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) { setError(e instanceof Error ? e.message : "Could not save changes"); }
    finally { setSaving(false); }
  };

  const triggerCrawl = async () => {
    setCrawling(true); setCrawlMsg("");
    try {
      await save(); // Save prefs first so crawler picks them up
      await api.post("/jobs/crawl", {});
      setCrawlMsg("Discovery queued. Results depend on worker availability and source responses.");
    } catch (e) { setCrawlMsg("Failed to start crawl. Is Celery worker running?"); }
    finally { setCrawling(false); }
  };

  const tabs = [
    { id: "profile" as Tab, label: "Profile", icon: User },
    { id: "jobprefs" as Tab, label: "Job Preferences", icon: Target },
    { id: "crawl" as Tab, label: "Discover Jobs", icon: Zap },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Settings className="w-8 h-8 text-slate-400" />
            Settings & Preferences
          </h1>
          <p className="text-slate-400 mt-1">Configure your profile, job preferences, and discovery settings.</p>
        </div>
        <button
          onClick={save}
          disabled={saving}
          className="flex items-center px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition-all disabled:opacity-50 gap-2"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : saved ? <CheckCircle className="w-4 h-4 text-emerald-300" /> : <Save className="w-4 h-4" />}
          {saved ? "Saved!" : saving ? "Saving..." : "Save Changes"}
        </button>
      </div>

      {error && <div className="notice error" role="alert">{error}</div>}
      {/* Tab Selector */}
      <div className="flex gap-2 border-b border-slate-800 pb-0">
        {tabs.map(t => {
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-t-lg border-b-2 transition-all ${
                tab === t.id
                  ? "border-blue-500 text-blue-400 bg-blue-500/10"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="w-4 h-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Profile Tab */}
      {tab === "profile" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <Card className="p-6 bg-slate-900/50 border-slate-700 space-y-5 md:col-span-2">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2"><User className="w-5 h-5 text-blue-400" />Personal Info</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: "name", label: "Full Name", placeholder: "Alex Mercer" },
                { key: "phone", label: "Phone / Mobile", placeholder: "+1 (555) 000-0000" },
                { key: "location", label: "Current City", placeholder: "Bangalore, India" },
                { key: "work_authorization", label: "Work Authorization", placeholder: "Authorized to work in US" },
                { key: "notice_period", label: "Notice Period", placeholder: "30 days / Immediate" },
                { key: "expected_salary", label: "Expected Salary / CTC", placeholder: "₹25 LPA or $120K" },
              ].map(f => (
                <div key={f.key} className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-300">{f.label}</label>
                  <input
                    value={prefs[f.key] || ""}
                    onChange={e => set(f.key, e.target.value)}
                    placeholder={f.placeholder}
                    className="w-full px-3 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6 bg-slate-900/50 border-slate-700 space-y-5 md:col-span-2">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2"><Globe className="w-5 h-5 text-purple-400" />Online Presence</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { key: "linkedin_link", label: "LinkedIn URL", icon: Linkedin, placeholder: "https://linkedin.com/in/yourprofile" },
                { key: "github_link", label: "GitHub URL", icon: Github, placeholder: "https://github.com/yourhandle" },
              ].map(f => (
                <div key={f.key} className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-300 flex items-center gap-2"><f.icon className="w-3.5 h-3.5" />{f.label}</label>
                  <input
                    value={prefs[f.key] || ""}
                    onChange={e => set(f.key, e.target.value)}
                    placeholder={f.placeholder}
                    className="w-full px-3 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
              ))}
            </div>
            <TagInput
              label="Portfolio / Project Links"
              values={prefs.portfolio_links || []}
              onChange={v => set("portfolio_links", v)}
              placeholder="https://yourproject.com — press Enter"
            />
          </Card>
        </div>
      )}

      {/* Job Preferences Tab */}
      {tab === "jobprefs" && (
        <div className="space-y-5">
          <Card className="p-6 bg-slate-900/50 border-slate-700 space-y-6">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2"><Target className="w-5 h-5 text-emerald-400" />What Jobs Are You Looking For?</h2>
            <p className="text-slate-400 text-sm -mt-2">These are used to personalize job discovery crawls and AI scoring.</p>

            <TagInput
              label="Target Job Titles / Roles"
              values={prefs.preferred_roles || []}
              onChange={v => set("preferred_roles", v)}
              placeholder="e.g. Senior Python Engineer — press Enter"
            />
            <TagInput
              label="Preferred Locations"
              values={prefs.preferred_locations || []}
              onChange={v => set("preferred_locations", v)}
              placeholder="e.g. Remote, Bangalore, London — press Enter"
            />
            <TagInput
              label="Priority Companies (Dream Employers)"
              values={prefs.priority_companies || []}
              onChange={v => set("priority_companies", v)}
              placeholder="e.g. Google, Stripe, Notion — press Enter"
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300 flex items-center gap-2"><DollarSign className="w-3.5 h-3.5 text-emerald-400" />Expected Salary / CTC</label>
                <input
                  value={prefs.expected_salary || ""}
                  onChange={e => set("expected_salary", e.target.value)}
                  placeholder="e.g. $120,000+ or ₹25 LPA"
                  className="w-full px-3 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300 flex items-center gap-2"><Briefcase className="w-3.5 h-3.5 text-blue-400" />Notice Period</label>
                <select
                  value={prefs.notice_period || ""}
                  onChange={e => set("notice_period", e.target.value)}
                  className="w-full px-3 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select notice period...</option>
                  <option value="Immediate">Immediate / Available now</option>
                  <option value="2 weeks">2 weeks</option>
                  <option value="1 month">1 month</option>
                  <option value="2 months">2 months</option>
                  <option value="3 months">3 months</option>
                </select>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Discover Jobs Tab */}
      {tab === "crawl" && (
        <div className="space-y-5">
          <Card className="p-6 bg-slate-900/50 border-slate-700 space-y-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2"><Zap className="w-5 h-5 text-yellow-400" />Job Discovery Sources</h2>
            <p className="text-slate-400 text-sm">These job boards are crawled automatically every hour. You can also trigger a manual crawl below.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { name: "RemoteOK", url: "remoteok.com", status: "Active", color: "emerald" },
                { name: "Remotive", url: "remotive.com", status: "Active — New!", color: "blue" },
                { name: "Adzuna", url: "adzuna.com", status: "Needs API key", color: "amber" },
              ].map(s => (
                <div key={s.name} className={`p-4 rounded-xl border ${
                  s.color === "emerald" ? "bg-emerald-500/5 border-emerald-500/20" :
                  s.color === "blue" ? "bg-blue-500/5 border-blue-500/20" :
                  "bg-amber-500/5 border-amber-500/20"
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold text-white">{s.name}</span>
                    <Badge className={`text-xs ${
                      s.color === "emerald" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" :
                      s.color === "blue" ? "bg-blue-500/20 text-blue-400 border-blue-500/30" :
                      "bg-amber-500/20 text-amber-400 border-amber-500/30"
                    }`}>{s.status}</Badge>
                  </div>
                  <p className="text-xs text-slate-500">{s.url}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6 bg-slate-900/50 border-slate-700 space-y-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2"><RefreshCw className="w-5 h-5 text-blue-400" />Manual Crawl</h2>
            <p className="text-slate-400 text-sm">
              Triggers an immediate crawl using your saved <strong className="text-white">preferred roles</strong> and active resume skills as search keywords. 
              Make sure Celery worker is running in Terminal 2.
            </p>

            {prefs.preferred_roles?.length > 0 && (
              <div className="p-3 rounded-lg bg-slate-800/60 border border-slate-700">
                <p className="text-xs text-slate-400 mb-2">Will crawl using these keywords:</p>
                <div className="flex flex-wrap gap-2">
                  {prefs.preferred_roles.map((r: string, i: number) => (
                    <Badge key={i} className="bg-blue-500/15 text-blue-300 border-blue-500/30 text-xs">{r}</Badge>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={triggerCrawl}
              disabled={crawling}
              className="flex items-center px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold hover:shadow-lg hover:shadow-blue-500/25 transition-all disabled:opacity-50 gap-2"
            >
              {crawling ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
              {crawling ? "Starting crawl..." : "Discover New Jobs Now"}
            </button>

            {crawlMsg && (
              <div className={`p-3 rounded-lg text-sm font-medium ${crawlMsg.includes("Failed") ? "bg-red-500/10 border border-red-500/20 text-red-400" : "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"}`}>
                {crawlMsg}
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}
