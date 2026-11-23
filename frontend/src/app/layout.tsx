import type { Metadata } from "next";
import AuthGate from "@/components/providers/AuthGate";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import QueryProvider from "@/components/providers/QueryProvider";



export const metadata: Metadata = {
  title: "OneJob · Your next chapter",
  description: "Automate your job search with AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body><script dangerouslySetInnerHTML={{__html:`try{var t=localStorage.getItem("onejob-theme")||"system";document.documentElement.dataset.theme=t==="system"?(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"):t}catch(e){}`}}/>
        <QueryProvider>
          <AuthGate><Sidebar />
          <main className="app-main">
            <div className="app-content">
              {children}
            </div>
          </main></AuthGate>
        </QueryProvider>
      </body>
    </html>
  );
}
