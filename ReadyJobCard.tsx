import { useState } from 'react';
import { Job } from '@/types';
import { JobCard } from './JobCard';
import { Button } from '@/components/ui/button';
import { CheckCircle, ExternalLink, Archive, ChevronDown, ChevronUp } from 'lucide-react';
import { jobsApi } from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';

interface ReadyJobCardProps {
  job: Job;
  rawResumeText?: string;
}

export function ReadyJobCard({ job, rawResumeText }: ReadyJobCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const handleMarkAsApplied = async () => {
    setIsApplying(true);
    try {
      await jobsApi.markAsApplied(job.id);
      toast({
        title: 'Marked as Applied!',
        description: `${job.job_title} has been moved to Applied.`,
      });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Could not update job status.',
        variant: 'destructive',
      });
    } finally {
      setIsApplying(false);
    }
  };

  const handleArchive = async () => {
    try {
      await jobsApi.markAsArchived(job.id);
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Could not archive job.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="space-y-2">
      <div className="group relative">
        <JobCard job={job} onClick={() => setShowDetails(!showDetails)} />
        
        {/* Match Score Badge */}
        {job.match_score && (
          <div className="absolute top-2 left-2">
            <span className={`px-2 py-1 text-xs font-bold rounded-full ${
              job.match_score >= 80 ? 'bg-green-500/20 text-green-400' :
              job.match_score >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {job.match_score}% Match
            </span>
          </div>
        )}
        
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-destructive bg-card/80 backdrop-blur-sm"
            onClick={(e) => {
              e.stopPropagation();
              handleArchive();
            }}
            title="Archive"
          >
            <Archive className="w-5 h-5" />
          </Button>
        </div>
      </div>
      
      {/* Expandable Job Details */}
      {showDetails && (
        <div className="p-3 rounded-lg bg-muted/50 border border-border/50 space-y-3 animate-in slide-in-from-top-2">
          {/* Company & Location */}
          <div className="flex justify-between text-sm">
            <span className="font-medium text-foreground">{job.company_name}</span>
            <span className="text-muted-foreground">{job.location || 'Remote'}</span>
          </div>
          
          {/* Job Description */}
          {job.job_description && (
            <div className="text-sm text-muted-foreground">
              <p className="line-clamp-4">{job.job_description}</p>
            </div>
          )}
          
          {/* Source */}
          <div className="text-xs text-muted-foreground">
            Source: <span className="capitalize">{job.source}</span>
          </div>
        </div>
      )}
      
      {/* Toggle Details Button */}
      <Button
        variant="ghost"
        size="sm"
        className="w-full text-xs text-muted-foreground"
        onClick={() => setShowDetails(!showDetails)}
      >
        {showDetails ? (
          <>
            <ChevronUp className="w-3 h-3 mr-1" />
            Hide Details
          </>
        ) : (
          <>
            <ChevronDown className="w-3 h-3 mr-1" />
            Show Details
          </>
        )}
      </Button>
      
      {/* Action Buttons */}
      <div className="px-1 flex gap-2">
        <Button 
          variant="default" 
          size="sm" 
          className="flex-1 gap-2 text-xs"
          onClick={() => window.open(job.source_url, '_blank')}
        >
          <ExternalLink className="w-3.5 h-3.5" />
          Apply Now
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          className="gap-2 text-xs"
          onClick={handleMarkAsApplied}
          disabled={isApplying}
        >
          <CheckCircle className="w-3.5 h-3.5" />
          {isApplying ? '...' : 'Applied'}
        </Button>
      </div>
    </div>
  );
}
