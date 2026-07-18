import React from 'react';
import { Card } from '@/components/ui/Card';
import { Settings as SettingsIcon } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="space-y-8 animate-in fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Settings</h1>
        <p className="text-slate-400">Manage your account and application preferences.</p>
      </div>

      <Card className="p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
        <div className="h-20 w-20 bg-slate-500/10 rounded-full flex items-center justify-center mb-6">
          <SettingsIcon className="h-10 w-10 text-slate-400" />
        </div>
        <h2 className="text-2xl font-bold mb-4">Under Construction</h2>
        <p className="text-slate-400 max-w-md mx-auto">
          Settings configuration is coming soon.
        </p>
      </Card>
    </div>
  );
}
