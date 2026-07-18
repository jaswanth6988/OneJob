import React from 'react';
import { Card } from '@/components/ui/Card';
import { Briefcase } from 'lucide-react';

export default function JobsPage() {
  return (
    <div className="space-y-8 animate-in fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Job Discovery</h1>
        <p className="text-slate-400">Browse jobs perfectly matched to your profile.</p>
      </div>

      <Card className="p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
        <div className="h-20 w-20 bg-blue-500/10 rounded-full flex items-center justify-center mb-6">
          <Briefcase className="h-10 w-10 text-blue-400" />
        </div>
        <h2 className="text-2xl font-bold mb-4">Coming in Phase 2</h2>
        <p className="text-slate-400 max-w-md mx-auto">
          We're building an advanced AI matching engine that will automatically discover and rank the best jobs for your unique profile. Check back soon!
        </p>
      </Card>
    </div>
  );
}
