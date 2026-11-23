'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BriefcaseBusiness, LayoutDashboard, FileText, Send, Bot, Settings, UserRound, Sun, Moon, Monitor, LogOut } from 'lucide-react';
import { useEffect, useState } from 'react';
const links = [['/', 'Overview', LayoutDashboard], ['/jobs', 'Find jobs', BriefcaseBusiness], ['/applications', 'Applications', Send], ['/resumes', 'My resumes', FileText], ['/assistant', 'Career assistant', Bot], ['/profile', 'My profile', UserRound], ['/settings', 'Preferences', Settings]] as const;
export function Sidebar() {
 const pathname=usePathname(); const [theme,setTheme]=useState('system');
 useEffect(()=>{setTheme(localStorage.getItem('onejob-theme')||'system')},[]);
 useEffect(()=>{const media=matchMedia('(prefers-color-scheme: dark)'); const apply=()=>{document.documentElement.dataset.theme=theme==='system'?(media.matches?'dark':'light'):theme}; apply(); localStorage.setItem('onejob-theme',theme); media.addEventListener('change',apply);return()=>media.removeEventListener('change',apply)},[theme]);
 return <aside className="sidebar"><Link href="/" className="brand"><span className="brand-icon"><BriefcaseBusiness size={23}/></span>OneJob<span className="brand-dot">.</span></Link><p className="nav-caption">YOUR NEXT CHAPTER</p><nav aria-label="Main navigation">{links.map(([href,label,Icon])=><Link key={href} href={href} aria-current={(pathname===href || href!=='/'&&pathname.startsWith(href))?'page':undefined}><Icon size={19}/><span>{label}</span></Link>)}</nav><div className="sidebar-bottom"><div className="career-note"><strong>A little progress, every day.</strong><p>Find the right role. Make your next move count.</p></div><div className="theme-switch" aria-label="Appearance">{[['light',Sun],['dark',Moon],['system',Monitor]].map(([value,Icon]:any)=><button key={value} title={`${value} theme`} aria-label={`${value} theme`} aria-pressed={theme===value} onClick={()=>setTheme(value)}><Icon size={17}/></button>)}</div><button className="logout" onClick={()=>{localStorage.removeItem('token');localStorage.removeItem('refresh_token');window.dispatchEvent(new Event('auth-expired'))}}><LogOut size={16}/>Sign out</button></div></aside>
}
