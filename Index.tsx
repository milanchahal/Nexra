import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Briefcase,
  ArrowRight,
  Upload,
  FileText,
  Target,
  Zap,
  CheckCircle,
} from 'lucide-react';

const features = [
  {
    icon: Upload,
    title: 'Upload Once',
    description: 'Upload your resume once and build a permanent profile.',
  },
  {
    icon: Target,
    title: 'Smart Matching',
    description: 'AI finds jobs that match your skills and preferences.',
  },
  {
    icon: FileText,
    title: 'Tailored Resumes',
    description: 'Generate ATS-optimized 1-page resumes for each job.',
  },
  {
    icon: Zap,
    title: 'One-Click Apply',
    description: 'Review and apply with a single click.',
  },
];

const benefits = [
  'Save 10+ hours per week on applications',
  'Increase interview rate by 3x',
  'ATS-optimized resume formatting',
  'Real-time application tracking',
  'Interview preparation assistance',
];

export default function Index() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <img src="/logo.jpg" alt="Nexara AI" className="w-9 h-9 rounded-lg object-contain" />
            <span className="font-semibold text-foreground">Nexara AI</span>
          </Link>
          
          <div className="flex items-center gap-4">
            <Link to="/login">
              <Button variant="ghost">Log in</Button>
            </Link>
            <Link to="/signup">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 lg:py-32">
        <div className="container mx-auto px-4 text-center">
          <Badge className="mb-6 bg-primary/10 text-primary border-primary/20">
            AI-Powered Job Applications
          </Badge>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground max-w-4xl mx-auto leading-tight mb-6">
            Land your dream job with{' '}
            <span className="gradient-text">AI-powered</span> applications
          </h1>
          
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10">
            Upload your resume once. Our AI finds matching jobs, creates tailored resumes,
            and prepares applications. You just review and click apply.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/signup">
              <Button size="lg" className="px-8">
                Start Free Trial
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline">
                Watch Demo
              </Button>
            </Link>
          </div>

          <p className="mt-6 text-sm text-muted-foreground">
            No credit card required • Free for 14 days
          </p>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 border-t border-border">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              How it works
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Four simple steps to automate your job search
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="w-7 h-7 text-primary" />
                </div>
                <div className="text-sm text-primary font-medium mb-2">
                  Step {index + 1}
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-20 border-t border-border bg-card/30">
        <div className="container mx-auto px-4">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-foreground mb-6">
                Stop wasting hours on each application
              </h2>
              <p className="text-muted-foreground mb-8">
                The average job seeker spends 30+ minutes per application.
                JobCopilot automates the tedious parts so you can focus on
                what matters — preparing for interviews and landing offers.
              </p>
              <ul className="space-y-3">
                {benefits.map((benefit, index) => (
                  <li key={index} className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-success flex-shrink-0" />
                    <span className="text-foreground">{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative">
              <div className="aspect-video rounded-xl bg-muted border border-border flex items-center justify-center">
                <span className="text-muted-foreground">Dashboard Preview</span>
              </div>
              <div className="absolute -bottom-4 -right-4 w-32 h-20 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center">
                <div className="text-center">
                  <span className="text-2xl font-bold text-primary">92%</span>
                  <p className="text-xs text-muted-foreground">Avg Match</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 border-t border-border">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">
            Ready to accelerate your job search?
          </h2>
          <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
            Join thousands of job seekers who have landed their dream jobs with JobCopilot.
          </p>
          <Link to="/signup">
            <Button size="lg" className="px-8">
              Get Started for Free
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <img src="/logo.jpg" alt="Nexara AI" className="w-7 h-7 rounded-md object-contain" />
            <span className="text-sm text-muted-foreground">
              © 2026 Nexara AI. All rights reserved.
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <Link to="/privacy" className="hover:text-foreground transition-colors">
              Privacy
            </Link>
            <Link to="/terms" className="hover:text-foreground transition-colors">
              Terms
            </Link>
            <Link to="/contact" className="hover:text-foreground transition-colors">
              Contact
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
