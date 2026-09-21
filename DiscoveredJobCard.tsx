import { useState } from 'react';
import { Job } from '@/types';
import { JobCard } from './JobCard';
import { Button } from '@/components/ui/button';
import { XCircle, Eye, Loader2, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { jobsApi } from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';

interface DiscoveredJobCardProps {
  job: Job;
  onIgnore: (jobId: string) => void;
}

export function DiscoveredJobCard({ job, onIgnore }: DiscoveredJobCardProps) {
  const [isPreparing, setIsPreparing] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const handleReview = async () => {
    setIsPreparing(true);
    try {
      await jobsApi.optimizeResume(job.id);
      toast({
        title: 'Resume Prepared',
        description: `Your resume has been optimized for ${job.job_title || job.role}. Check "Resume Ready" column.`,
      });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    } catch (error) {
      toast({
        title: 'Preparation Failed',
        description: 'Could not prepare resume for this job.',
        variant: 'destructive',
      });
    } finally {
      setIsPreparing(false);
    }
  };

  return (
    <div className="space-y-2">
      <div className="group relative">
        <JobCard
          job={job}
          onClick={() => setShowDetails(!showDetails)}
        />
        
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
              onIgnore(job.id);
            }}
            title="Ignore / Archive"
          >
            <XCircle className="w-5 h-5" />
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
              <p className="line-clamp-6">{job.job_description}</p>
            </div>
          )}
          
          {/* Source & Link */}
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Source: <span className="capitalize">{job.source}</span></span>
            {job.source_url && (
              <a 
                href={job.source_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-primary hover:underline"
              >
                View Original <ExternalLink className="w-3 h-3" />
              </a>
            )}
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
      
      {/* Action Button */}
      <div className="px-1">
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full gap-2 text-xs"
          onClick={handleReview}
          disabled={isPreparing}
        >
          {isPreparing ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Eye className="w-3.5 h-3.5" />
          )}
          {isPreparing ? 'Preparing...' : 'Review & Prepare Resume'}
        </Button>
      </div>
    </div>
  );
}
