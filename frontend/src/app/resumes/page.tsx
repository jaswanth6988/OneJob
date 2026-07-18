'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { UploadCloud, FileText, Trash2, Eye } from 'lucide-react';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function ResumesPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [resumes, setResumes] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);

  // Fetch real resumes from backend
  const fetchResumes = async () => {
    try {
      const res = await api.resumes.getResumes();
      if (res.success) {
        setResumes(res.data);
      }
    } catch (e) {
      console.error('Failed to fetch resumes:', e);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, []);

  const handleFileUpload = async (file: File) => {
    if (!file) return;
    setUploading(true);
    try {
      // Send file to the backend parsing endpoint
      await api.resumes.uploadResume(file, file.name.split('.')[0] || 'My Resume', 'v1', 'General');
      // Refresh list
      await fetchResumes();
    } catch (e) {
      console.error('Upload failed:', e);
      alert('Failed to upload resume. Make sure it is a PDF or DOCX.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1 text-white">Resume Manager</h1>
          <p className="text-slate-400">Upload and manage your resumes for AI parsing.</p>
        </div>
      </div>

      <Card 
        className={`p-10 border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center text-center relative ${
          isDragging ? 'border-blue-500 bg-blue-500/5' : 'border-slate-700 bg-slate-900/50 hover:border-slate-500'
        }`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => { 
          e.preventDefault(); 
          setIsDragging(false);
          if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
          }
        }}
      >
        <input 
          type="file" 
          accept=".pdf,.docx"
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              handleFileUpload(e.target.files[0]);
            }
          }}
          disabled={uploading}
        />
        <div className="h-16 w-16 rounded-full bg-slate-800 flex items-center justify-center mb-4 shadow-inner">
          <UploadCloud className={`h-8 w-8 ${uploading ? 'text-slate-500 animate-pulse' : 'text-blue-400'}`} />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">
          {uploading ? 'Uploading and parsing with AI...' : 'Click to upload or drag and drop'}
        </h3>
        <p className="text-slate-400 text-sm max-w-sm mb-6">
          PDF, DOCX up to 5MB. Our AI will automatically extract your experience and skills.
        </p>
        <Button disabled={uploading}>
          {uploading ? 'Processing...' : 'Select File'}
        </Button>
      </Card>

      {resumes.length === 0 ? (
        <div className="text-center p-8 text-slate-500">No resumes uploaded yet.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resumes.map((resume) => (
            <Card key={resume.id} className="flex flex-col bg-slate-900/50 border-slate-800 hover:border-slate-600 transition-colors">
              <div className="p-5 flex-1">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 bg-blue-500/10 rounded-lg">
                    <FileText className="h-6 w-6 text-blue-400" />
                  </div>
                  <Badge variant="outline" className="text-emerald-400 border-emerald-400/20 bg-emerald-400/10">
                    Parsed
                  </Badge>
                </div>
                <h3 className="font-semibold text-lg text-white truncate mb-1">{resume.title}</h3>
                <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
                  <span>{resume.version_name}</span>
                  <span>•</span>
                  <span>{new Date(resume.created_at).toLocaleDateString()}</span>
                </div>
                <Badge variant="secondary" className="bg-slate-800 text-slate-300">
                  {resume.role_label}
                </Badge>
              </div>
              
              <div className="border-t border-slate-800 p-3 bg-slate-900/80 flex justify-between items-center">
                <Button variant="ghost" size="sm" className="h-8 gap-1.5 text-xs text-slate-300 hover:text-white" onClick={() => alert("Resume Viewer coming soon!")}>
                  <Eye className="h-3.5 w-3.5" />
                  View
                </Button>
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-red-400 hover:text-red-300 hover:bg-red-400/10">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
