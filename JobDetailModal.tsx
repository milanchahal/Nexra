import { useState } from 'react';
import { Job } from '@/types';
import { Button } from '@/components/ui/button';
import { 
  X, ExternalLink, Share2, Flag, FileText, Building2, 
  MapPin, Clock, DollarSign, Users, Globe, Linkedin,
  CheckCircle, XCircle, Sparkles, ArrowRight
} from 'lucide-react';
import { MatchScoreRing } from './MatchScoreRing';
import { jobsApi } from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';

interface JobDetailModalProps {
  job: Job;
  isOpen: boolean;
  onClose: () => void;
  onChatAboutJob?: (job: Job) => void;
}

export function JobDetailModal({ job, isOpen, onClose, onChatAboutJob }: JobDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'company'>('overview');
  const queryClient = useQueryClient();
  const { toast } = useToast();

  if (!isOpen) return null;

  // Parse skills from description (simple extraction)
  const extractedSkills = extractSkillsFromDescription(job.job_description || '');

  // Parse responsibilities from description
  const responsibilities = extractResponsibilities(job.job_description || '');

  const handleApply = () => {
    if (job.source_url) {
      window.open(job.source_url, '_blank');
    }
  };

  const handleMarkApplied = async () => {
    try {
      await jobsApi.markAsApplied(job.id);
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      toast({ title: 'Marked as Applied!' });
    } catch (error) {
      toast({ title: 'Error', variant: 'destructive' });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative ml-auto h-full w-full max-w-3xl bg-card shadow-2xl overflow-hidden flex flex-col animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-gradient-to-r from-card to-muted/30">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
            <span className="text-sm text-muted-foreground">
              {job.applicants || '200+' } applicants
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon">
              <Share2 className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon">
              <Flag className="w-4 h-4" />
            </Button>
            <Button 
              className="bg-emerald-500 hover:bg-emerald-600 text-white gap-2"
              onClick={handleApply}
            >
              APPLY NOW <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border">
          <button
            className={`px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === 'overview' 
                ? 'text-foreground border-b-2 border-emerald-500' 
                : 'text-muted-foreground hover:text-foreground'
            }`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={`px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === 'company' 
                ? 'text-foreground border-b-2 border-emerald-500' 
                : 'text-muted-foreground hover:text-foreground'
            }`}
            onClick={() => setActiveTab('company')}
          >
            Company
          </button>
          <div className="ml-auto flex items-center gap-4 pr-4 text-muted-foreground text-sm">
            <button className="hover:text-foreground flex items-center gap-1">
              <Share2 className="w-4 h-4" /> Share
            </button>
            <button className="hover:text-foreground flex items-center gap-1">
              <Flag className="w-4 h-4" /> Report Issue
            </button>
            <a 
              href={job.source_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-foreground flex items-center gap-1"
            >
              <FileText className="w-4 h-4" /> Original Job Post
            </a>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'overview' && (
            <OverviewTab 
              job={job} 
              extractedSkills={extractedSkills}
              responsibilities={responsibilities}
              onChatAboutJob={onChatAboutJob}
            />
          )}
          {activeTab === 'company' && (
            <CompanyTab job={job} />
          )}
        </div>
      </div>
    </div>
  );
}

// Overview Tab Component
function OverviewTab({ 
  job, 
  extractedSkills, 
  responsibilities,
  onChatAboutJob 
}: { 
  job: Job; 
  extractedSkills: string[];
  responsibilities: string[];
  onChatAboutJob?: (job: Job) => void;
}) {
  return (
    <div className="p-6 space-y-6">
      {/* Job Header */}
      <div className="flex gap-6">
        <div className="flex-1">
          {/* Company & Time */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center text-white font-bold">
              {job.company_name?.charAt(0) || 'C'}
            </div>
            <span className="font-medium text-foreground">{job.company_name}</span>
            <span>•</span>
            <span>{job.posted_date || '18 hours ago'}</span>
          </div>
          
          {/* Title */}
          <h1 className="text-2xl font-bold text-foreground mb-4">
            {job.job_title}
          </h1>
          
          {/* Meta Info */}
          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              {job.location || 'Remote'}
            </div>
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {job.job_type || 'Full-time'}
            </div>
            <div className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              {job.experience_level || 'Entry Level'}
            </div>
            {job.salary_range && (
              <div className="flex items-center gap-1">
                <DollarSign className="w-4 h-4" />
                {job.salary_range}
              </div>
            )}
          </div>
        </div>
        
        {/* Match Score */}
        <MatchScoreRing score={job.match_score || 85} />
      </div>

      {/* Generate Resume CTA */}
      <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20">
        <div className="flex items-center gap-3">
          <Sparkles className="w-5 h-5 text-emerald-500" />
          <span className="font-medium">Maximize your interview chances</span>
        </div>
        <Button 
          className="bg-emerald-500 hover:bg-emerald-600 gap-2"
          onClick={() => onChatAboutJob?.(job)}
        >
          <Sparkles className="w-4 h-4" />
          Generate Custom Resume
        </Button>
      </div>

      {/* Company Description */}
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground leading-relaxed">
          {job.job_description?.slice(0, 300)}...
        </p>
        
        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {['Electronics', 'Logistics', 'Manufacturing'].map(tag => (
            <span key={tag} className="px-3 py-1 bg-muted rounded-full text-xs text-muted-foreground">
              {tag}
            </span>
          ))}
          <span className="px-3 py-1 bg-muted rounded-full text-xs text-muted-foreground flex items-center gap-1">
            <XCircle className="w-3 h-3" /> No H1B
          </span>
        </div>
      </div>

      {/* Skills Section */}
      <div className="space-y-3">
        <h3 className="font-semibold flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-emerald-500" />
          Skills Match
        </h3>
        <p className="text-sm text-muted-foreground">
          Find out how your skills align with this job's requirements.
        </p>
        <div className="flex flex-wrap gap-2">
          {extractedSkills.map((skill, i) => (
            <span 
              key={i}
              className="px-3 py-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-sm flex items-center gap-1"
            >
              <CheckCircle className="w-3 h-3" />
              {skill}
            </span>
          ))}
        </div>
      </div>

      {/* Responsibilities */}
      {responsibilities.length > 0 && (
        <div className="space-y-3">
          <h3 className="font-semibold text-lg">Responsibilities</h3>
          <ul className="space-y-2">
            {responsibilities.map((resp, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                <span className="mt-1.5 w-1.5 h-1.5 bg-emerald-500 rounded-full flex-shrink-0" />
                {resp}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Full Description */}
      <div className="space-y-3">
        <h3 className="font-semibold text-lg">Full Description</h3>
        <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
          {job.job_description}
        </p>
      </div>
    </div>
  );
}

// Company Tab Component
function CompanyTab({ job }: { job: Job }) {
  return (
    <div className="p-6 space-y-6">
      {/* Company Header */}
      <div className="flex items-start gap-4">
        <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold">
          {job.company_name?.charAt(0) || 'C'}
        </div>
        <div>
          <h2 className="text-xl font-bold">{job.company_name}</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {job.company_info?.industry || 'Technology'}
          </p>
        </div>
      </div>

      {/* Company Details */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 rounded-lg bg-muted/50">
          <div className="text-xs text-muted-foreground mb-1">Founded</div>
          <div className="font-medium">{job.company_info?.founded || 'N/A'}</div>
        </div>
        <div className="p-4 rounded-lg bg-muted/50">
          <div className="text-xs text-muted-foreground mb-1">Company Size</div>
          <div className="font-medium">{job.company_info?.size || '10,001+ employees'}</div>
        </div>
        <div className="p-4 rounded-lg bg-muted/50">
          <div className="text-xs text-muted-foreground mb-1">Location</div>
          <div className="font-medium">{job.location || 'N/A'}</div>
        </div>
        <div className="p-4 rounded-lg bg-muted/50">
          <div className="text-xs text-muted-foreground mb-1">Website</div>
          <a 
            href={job.company_info?.website || '#'} 
            target="_blank" 
            rel="noopener noreferrer"
            className="font-medium text-emerald-500 hover:underline flex items-center gap-1"
          >
            <Globe className="w-4 h-4" />
            Visit Website
          </a>
        </div>
      </div>

      {/* Leadership (Placeholder) */}
      <div className="space-y-3">
        <h3 className="font-semibold text-lg">Leadership Team</h3>
        <div className="flex gap-4">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
            <div className="w-10 h-10 bg-muted rounded-full flex items-center justify-center">
              <Users className="w-5 h-5 text-muted-foreground" />
            </div>
            <div>
              <div className="font-medium text-sm">CEO</div>
              <a href="#" className="text-xs text-emerald-500 flex items-center gap-1">
                <Linkedin className="w-3 h-3" /> View LinkedIn
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* About */}
      <div className="space-y-3">
        <h3 className="font-semibold text-lg">About {job.company_name}</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {job.company_info?.description || 
           `${job.company_name} is a leading company in the ${job.company_info?.industry || 'technology'} sector.`}
        </p>
      </div>
    </div>
  );
}

// Helper functions
function extractSkillsFromDescription(description: string): string[] {
  const techSkills = [
    'Python', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'Java', 'C++', 
    'AWS', 'Docker', 'Kubernetes', 'SQL', 'MongoDB', 'PostgreSQL', 'Git',
    'HTML', 'CSS', 'REST API', 'GraphQL', 'Machine Learning', 'AI', 'Data Science',
    'Full Stack', 'Frontend', 'Backend', 'DevOps', 'Cloud', 'CI/CD'
  ];
  
  const found = techSkills.filter(skill => 
    description.toLowerCase().includes(skill.toLowerCase())
  );
  
  return found.slice(0, 10);
}

function extractResponsibilities(description: string): string[] {
  // Simple extraction - look for bullet points or numbered lists
  const lines = description.split(/[\n\r]+/);
  const responsibilities: string[] = [];
  
  for (const line of lines) {
    const cleaned = line.replace(/^[-•*\d.]+\s*/, '').trim();
    if (cleaned.length > 30 && cleaned.length < 200) {
      responsibilities.push(cleaned);
    }
  }
  
  return responsibilities.slice(0, 8);
}
