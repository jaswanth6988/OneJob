import React from 'react';
import { Card } from '@/components/ui/Card';
import { Send } from 'lucide-react';

export default function ApplicationsPage() {
  return (
    <div className="space-y-8 animate-in fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Application Tracker</h1>
        <p className="text-slate-400">Monitor all your automated applications.</p>
      </div>

      <Card className="p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
        <div className="h-20 w-20 bg-teal-500/10 rounded-full flex items-center justify-center mb-6">
          <Send className="h-10 w-10 text-teal-400" />
        </div>
        <h2 className="text-2xl font-bold mb-4">Coming in Phase 2</h2>
        <p className="text-slate-400 max-w-md mx-auto">
          Soon you'll be able to track every application sent by the AI, monitor interview requests, and manage manual reviews all in one place.
        </p>
      </Card>
    </div>
  );
}
