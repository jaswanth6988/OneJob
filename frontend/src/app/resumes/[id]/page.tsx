'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ArrowLeft, Download, Edit2, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';

export default function ResumeDetailPage({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState('overview');
  
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'experience', label: 'Experience' },
    { id: 'education', label: 'Education' },
    { id: 'skills', label: 'Skills' },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <Link href="/resumes" className="inline-flex items-center text-sm text-slate-400 hover:text-slate-200 transition-colors">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Resumes
      </Link>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold tracking-tight">Software Engineer CV</h1>
            <Badge variant="success">Active</Badge>
          </div>
          <p className="text-slate-400">Parsed on October 24, 2024</p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="secondary" className="gap-2">
            <Download className="h-4 w-4" />
            Export PDF
          </Button>
          <Button className="gap-2">
            <Edit2 className="h-4 w-4" />
            Edit Content
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="flex gap-2 border-b border-slate-800 pb-px overflow-x-auto">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.id 
                    ? 'border-blue-500 text-blue-400' 
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <Card className="p-6 min-h-[400px]">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-2">Professional Summary</h3>
                  <p className="text-slate-300 leading-relaxed">
                    Results-oriented Software Engineer with 5+ years of experience building scalable web applications. 
                    Proficient in React, Node.js, and Cloud architectures. Proven track record of improving application performance and leading agile teams.
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-3">Contact Info Extracted</h3>
                  <ul className="space-y-2 text-slate-300">
                    <li>Email: john.smith@example.com</li>
                    <li>Phone: (555) 123-4567</li>
                    <li>Location: San Francisco, CA</li>
                    <li>LinkedIn: linkedin.com/in/johnsmith</li>
                  </ul>
                </div>
              </div>
            )}
            {activeTab !== 'overview' && (
              <div className="flex h-full items-center justify-center text-slate-500">
                Content for {activeTab} tab
              </div>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="font-semibold mb-4 text-center">ATS Compatibility Score</h3>
            <div className="flex flex-col items-center justify-center relative py-4">
              <div className="w-32 h-32 rounded-full border-8 border-slate-800 flex items-center justify-center relative z-10">
                <div className="absolute inset-0 rounded-full border-8 border-emerald-500 border-t-transparent border-r-transparent transform -rotate-45"></div>
                <span className="text-3xl font-bold">92</span>
              </div>
              <p className="text-emerald-400 font-medium mt-4">Excellent</p>
            </div>
            
            <div className="mt-6 space-y-3 text-sm">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                <span className="text-slate-300">Standard section headers detected</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                <span className="text-slate-300">Action verbs used in experience</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                <span className="text-slate-300">Quantifiable metrics included</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
