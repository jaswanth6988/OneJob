"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";

// Profile page now redirects to Settings which has the full implementation
export default function ProfilePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to Settings page which has the full profile + preferences editor
    router.replace("/settings");
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <p className="text-slate-400">Redirecting to Settings...</p>
    </div>
  );
}
