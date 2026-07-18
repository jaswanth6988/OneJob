'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, FileText, Briefcase, Send, Bot, Settings, LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Resumes', href: '/resumes', icon: FileText },
  { name: 'Jobs', href: '/jobs', icon: Briefcase },
  { name: 'Applications', href: '/applications', icon: Send },
  { name: 'AI Assistant', href: '/assistant', icon: Bot },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-slate-900/80 backdrop-blur-xl border-r border-slate-800/50 flex flex-col transition-all duration-300">
      <div className="flex h-16 items-center px-6 py-8 border-b border-slate-800/30">
        <h1 className="text-xl font-bold tracking-tight text-gradient">
          AI Job Portal
        </h1>
      </div>

      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                isActive 
                  ? "bg-gradient-to-r from-blue-500/10 to-purple-500/10 text-blue-400 shadow-[inset_0_1px_0_0_rgba(148,163,184,0.1)] border border-slate-700/50" 
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
              )}
            >
              <item.icon 
                className={cn(
                  "mr-3 h-5 w-5 transition-colors duration-200",
                  isActive ? "text-blue-400" : "text-slate-500 group-hover:text-slate-300"
                )} 
              />
              {item.name}
            </Link>
          );
        })}
      </div>

      <div className="p-4 border-t border-slate-800/30">
        <Link href="/profile" className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-800/50 transition-colors">
          <div className="h-9 w-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium">
            JS
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-sm font-medium text-slate-200 truncate">John Smith</p>
            <p className="text-xs text-slate-500 truncate">Software Engineer</p>
          </div>
        </Link>
      </div>
    </aside>
  );
}
