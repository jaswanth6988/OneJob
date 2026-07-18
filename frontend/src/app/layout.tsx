import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import QueryProvider from "@/components/providers/QueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Job Apply Portal",
  description: "Automate your job search with AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen flex antialiased selection:bg-blue-500/30`}>
        <QueryProvider>
          <Sidebar />
          <main className="flex-1 overflow-x-hidden overflow-y-auto pl-64">
            <div className="container mx-auto p-8 max-w-7xl">
              {children}
            </div>
          </main>
        </QueryProvider>
      </body>
    </html>
  );
}
