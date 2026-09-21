import { useState } from 'react';
import { Job } from '@/types';
import { JobCard } from './JobCard';
import { Button } from '@/components/ui/button';
import { Undo2, ChevronDown, ChevronUp } from 'lucide-react';
import { jobsApi } from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';

interface ArchivedJobCardProps {
  job: Job;
}

export function ArchivedJobCard({ job }: ArchivedJobCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const handleRestore = async () => {
    try {
      // Restore to discovered state
      await jobsApi.markAsDiscovered?.(job.id) || 
             fetch(`/api/jobs/${job.id}/status`, {
               method: 'PATCH',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({ status: 'discovered' })
             });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      toast({
        title: 'Job Restored',
        description: `${job.job_title} moved back to New Jobs.`,
      });
    } catch (error) {
      console.error('Failed to restore:', error);
    }
  };

  return (
    <div className="space-y-2 opacity-60 hover:opacity-100 transition-opacity">
      <div className="group relative">
        <div className="absolute inset-0 bg-muted/50 rounded-lg pointer-events-none" />
        <JobCard job={job} onClick={() => setShowDetails(!showDetails)} />
        <div className="absolute top-2 left-2">
          <span className="px-2 py-1 bg-muted text-muted-foreground text-xs font-medium rounded-full">
            Archived
          </span>
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
      
      {/* Restore Button */}
      <div className="px-1">
        <Button 
          variant="ghost" 
          size="sm" 
          className="w-full gap-2 text-xs text-muted-foreground hover:text-foreground"
          onClick={handleRestore}
        >
          <Undo2 className="w-3.5 h-3.5" />
          Restore
        </Button>
      </div>
    </div>
  );
}
