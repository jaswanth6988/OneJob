import React from 'react';
import { Card } from '@/components/ui/Card';
import { Bot } from 'lucide-react';

export default function AssistantPage() {
  return (
    <div className="space-y-8 animate-in fade-in h-[calc(100vh-8rem)] flex flex-col">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">AI Assistant</h1>
        <p className="text-slate-400">Chat with your personal career agent.</p>
      </div>

      <Card className="flex-1 flex flex-col items-center justify-center text-center p-8">
        <div className="h-24 w-24 bg-purple-500/10 rounded-full flex items-center justify-center mb-6">
          <Bot className="h-12 w-12 text-purple-400" />
        </div>
        <h2 className="text-2xl font-bold mb-4">Coming in Phase 2</h2>
        <p className="text-slate-400 max-w-md mx-auto">
          Your personal AI career agent is currently in training. Soon, you'll be able to ask for resume feedback, interview prep, and strategy advice.
        </p>
      </Card>
    </div>
  );
}
