import { Link } from 'react-router-dom';
import { Briefcase } from 'lucide-react';

export function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 xl:w-2/5 bg-card border-r border-border relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent" />
        <div className="absolute top-1/4 -left-20 w-96 h-96 bg-primary/20 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
        
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          <Link to="/" className="flex items-center gap-3">
            <img src="/logo.jpg" alt="Nexara AI" className="w-10 h-10 rounded-xl object-contain" />
            <span className="text-xl font-semibold text-foreground">Nexara AI</span>
          </Link>
          
          <div className="space-y-6">
            <h1 className="text-4xl xl:text-5xl font-bold text-foreground leading-tight">
              Your AI-powered<br />
              <span className="gradient-text">job application</span><br />
              assistant
            </h1>
            <p className="text-lg text-muted-foreground max-w-md">
              Upload your resume once. Get tailored applications for every job. Land more interviews with less effort.
            </p>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Trusted by 10,000+ job seekers</span>
            <span className="w-1 h-1 rounded-full bg-muted-foreground" />
            <span>500+ companies</span>
          </div>
        </div>
      </div>
      
      {/* Right side - Auth form */}
      <div className="flex-1 flex flex-col">
        {/* Mobile header */}
        <div className="lg:hidden p-6 border-b border-border">
          <Link to="/" className="flex items-center gap-3">
            <img src="/logo.jpg" alt="Nexara AI" className="w-10 h-10 rounded-xl object-contain" />
            <span className="text-xl font-semibold text-foreground">Nexara AI</span>
          </Link>
        </div>
        
        <div className="flex-1 flex items-center justify-center p-6 sm:p-12">
          <div className="w-full max-w-md animate-fade-in">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
