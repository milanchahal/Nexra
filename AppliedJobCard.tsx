import { useState } from 'react';
import { Job } from '@/types';
import { JobCard } from './JobCard';
import { Button } from '@/components/ui/button';
import { Archive, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { jobsApi } from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';

interface AppliedJobCardProps {
  job: Job;
}

export function AppliedJobCard({ job }: AppliedJobCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const queryClient = useQueryClient();

  const handleArchive = async () => {
    try {
      await jobsApi.markAsArchived(job.id);
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    } catch (error) {
      console.error('Failed to archive:', error);
    }
  };

  return (
    <div className="space-y-2">
      <div className="group relative">
        <div className="absolute inset-0 bg-green-500/10 rounded-lg pointer-events-none" />
        <JobCard job={job} onClick={() => setShowDetails(!showDetails)} />
        <div className="absolute top-2 left-2">
          <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs font-medium rounded-full">
            Applied ✓
          </span>
        </div>
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
          
          {/* Applied Date */}
          {job.applied_at && (
            <div className="text-xs text-muted-foreground">
              Applied: {new Date(job.applied_at).toLocaleDateString()}
            </div>
          )}
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
      
      {/* Track Button */}
      <div className="px-1">
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full gap-2 text-xs"
          onClick={() => window.open(job.source_url, '_blank')}
        >
          <ExternalLink className="w-3.5 h-3.5" />
          View on {job.source || 'Website'}
        </Button>
      </div>
    </div>
  );
}
