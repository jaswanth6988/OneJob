'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { UploadCloud, FileText, MoreVertical, Edit2, Trash2, Eye } from 'lucide-react';
import Link from 'next/link';

export default function ResumesPage() {
  const [isDragging, setIsDragging] = useState(false);

  const mockResumes = [
    { id: '1', title: 'Software Engineer CV', version: 'v2.1', role: 'Frontend', score: 92, date: 'Oct 24, 2024' },
    { id: '2', title: 'Full Stack Dev', version: 'v1.0', role: 'Full Stack', score: 78, date: 'Oct 15, 2024' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Resume Manager</h1>
          <p className="text-slate-400">Upload and manage your resumes for AI parsing.</p>
        </div>
      </div>

      <Card 
        className={`p-10 border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center text-center ${
          isDragging ? 'border-blue-500 bg-blue-500/5' : 'border-slate-700 hover:border-slate-500'
        }`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => { e.preventDefault(); setIsDragging(false); /* Handle file */ }}
      >
        <div className="h-16 w-16 rounded-full bg-slate-800 flex items-center justify-center mb-4 shadow-inner">
          <UploadCloud className="h-8 w-8 text-blue-400" />
        </div>
        <h3 className="text-lg font-semibold mb-2">Click to upload or drag and drop</h3>
        <p className="text-slate-400 text-sm max-w-sm mb-6">
          PDF, DOCX up to 5MB. Our AI will automatically extract your experience and skills.
        </p>
        <Button>Select File</Button>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockResumes.map((resume) => (
          <Card key={resume.id} hover className="flex flex-col">
            <div className="p-5 flex-1">
              <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <FileText className="h-6 w-6 text-blue-400" />
                </div>
                <Badge variant={resume.score > 85 ? 'success' : resume.score > 70 ? 'warning' : 'danger'}>
                  ATS: {resume.score}%
                </Badge>
              </div>
              <h3 className="font-semibold text-lg truncate mb-1">{resume.title}</h3>
              <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
                <span>{resume.version}</span>
                <span>•</span>
                <span>{resume.date}</span>
              </div>
              <Badge variant="primary" size="sm">{resume.role}</Badge>
            </div>
            
            <div className="border-t border-slate-800/50 p-3 bg-slate-900/30 flex justify-between items-center">
              <Link href={`/resumes/${resume.id}`}>
                <Button variant="ghost" size="sm" className="h-8 gap-1.5 text-xs">
                  <Eye className="h-3.5 w-3.5" />
                  View
                </Button>
              </Link>
              <div className="flex gap-1">
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Edit2 className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-red-400 hover:text-red-300">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
