import React from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FileText, Briefcase, Send, Target, ChevronRight, Activity } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const stats = [
    { label: 'Total Resumes', value: '3', icon: FileText, color: 'text-blue-400', bg: 'bg-blue-400/10' },
    { label: 'Jobs Discovered', value: '142', icon: Briefcase, color: 'text-purple-400', bg: 'bg-purple-400/10' },
    { label: 'Applications Sent', value: '28', icon: Send, color: 'text-teal-400', bg: 'bg-teal-400/10' },
    { label: 'Success Rate', value: '18%', icon: Target, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
  ];

  const recentActivity = [
    { id: 1, action: 'Applied to Senior Frontend Engineer at TechCorp', time: '2 hours ago', type: 'application' },
    { id: 2, action: 'AI parsed updated resume "React Developer 2024"', time: '5 hours ago', type: 'resume' },
    { id: 3, action: 'Found 12 new matching jobs', time: '1 day ago', type: 'job' },
    { id: 4, action: 'Interview scheduled with StartUp Inc', time: '2 days ago', type: 'interview' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">
          Welcome back, <span className="text-gradient">John</span>
        </h1>
        <p className="text-slate-400">Here's what's happening with your job search today.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label} hover className="p-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${stat.bg}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-400">{stat.label}</p>
                <p className="text-2xl font-bold text-slate-100">{stat.value}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card variant="gradient" className="lg:col-span-2 p-6 flex flex-col justify-center border-t border-slate-700/50">
          <h2 className="text-xl font-semibold mb-2">Ready to accelerate your search?</h2>
          <p className="text-slate-400 mb-6 max-w-lg">
            Let our AI analyze your resume and automatically find and apply to the best matching jobs while you sleep.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link href="/resumes">
              <Button size="lg" className="gap-2">
                Upload New Resume
                <ChevronRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/jobs">
              <Button variant="secondary" size="lg">
                Browse Matches
              </Button>
            </Link>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-400" />
              Recent Activity
            </h3>
            <Button variant="ghost" size="sm" className="h-8 px-2 text-xs">View all</Button>
          </div>
          <div className="space-y-4">
            {recentActivity.map((item) => (
              <div key={item.id} className="flex gap-3">
                <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)] flex-shrink-0" />
                <div>
                  <p className="text-sm text-slate-200 line-clamp-2">{item.action}</p>
                  <p className="text-xs text-slate-500 mt-1">{item.time}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
