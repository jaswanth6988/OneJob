'use client';

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export default function ProfilePage() {
  return (
    <div className="space-y-8 animate-in fade-in max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Profile & Preferences</h1>
        <p className="text-slate-400">Manage your personal information and job search criteria.</p>
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-6 border-b border-slate-800 pb-2">Personal Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input label="Full Name" defaultValue="John Smith" />
          <Input label="Email Address" defaultValue="john@example.com" type="email" />
          <Input label="Phone Number" defaultValue="+1 (555) 123-4567" />
          <Input label="Location" defaultValue="San Francisco, CA" />
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-6 border-b border-slate-800 pb-2">Job Preferences</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input label="Expected Salary" defaultValue="$130,000" />
          <Input label="Notice Period" defaultValue="2 weeks" />
          <div className="md:col-span-2">
            <Input label="Preferred Roles (Comma separated)" defaultValue="Frontend Engineer, React Developer, Full Stack" />
          </div>
        </div>
      </Card>
      
      <div className="flex justify-end gap-4">
        <Button variant="secondary">Cancel</Button>
        <Button>Save Changes</Button>
      </div>
    </div>
  );
}
