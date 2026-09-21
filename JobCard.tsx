import type { Job } from '@/types';
import { Badge } from '@/components/ui/badge';
import { MapPin, Building2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface JobCardProps {
  job: Job;
  onClick: () => void;
  isSelected?: boolean;
}

const statusConfig: Record<string, { label: string; className: string }> = {
  discovered: { label: 'New', className: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' },
  resume_ready: { label: 'Resume Ready', className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' },
  optimized: { label: 'Optimized', className: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' },
  applied: { label: 'Applied', className: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' },
  archived: { label: 'Archived', className: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200' },
};

export function JobCard({ job, onClick, isSelected }: JobCardProps) {
  const status = statusConfig[job.status] || statusConfig.discovered;
  
  // Use match_score from backend, with fallback to fitScore for compatibility
  const score = job.match_score ?? job.fitScore ?? 0;
  const scoreClass =
    score >= 85
      ? 'text-green-600'
      : score >= 70
      ? 'text-yellow-600'
      : 'text-red-500';

  // Get display values - backend uses snake_case, frontend used camelCase
  const companyName = job.company_name || job.company || 'Unknown Company';
  const jobTitle = job.job_title || job.role || 'Unknown Role';
  const location = job.location || 'Remote';
  const postedAt = job.discovered_at || job.created_at;

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left p-4 rounded-xl border bg-card transition-all',
        'hover:shadow-md hover:border-primary/50',
        isSelected
          ? 'border-primary ring-2 ring-primary/20'
          : 'border-border'
      )}
    >
      <div className="flex items-start gap-3">
        {/* Company logo placeholder */}
        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
          <Building2 className="w-5 h-5 text-muted-foreground" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h3 className="font-medium text-foreground truncate text-sm">{jobTitle}</h3>
              <p className="text-xs text-muted-foreground truncate">{companyName}</p>
            </div>
            <Badge className={cn('flex-shrink-0 text-xs', status.className)}>
              {status.label}
            </Badge>
          </div>

          <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              {location}
            </span>
            {job.source && (
              <span className="px-1.5 py-0.5 rounded bg-muted text-xs capitalize">
                {job.source}
              </span>
            )}
          </div>

          <div className="flex items-center justify-between mt-3">
            <span className="text-xs text-muted-foreground">
              {postedAt && new Date(postedAt).toLocaleDateString()}
            </span>
            <div className="flex items-center gap-1">
              <span className="text-xs text-muted-foreground">Match</span>
              <span className={cn('text-sm font-semibold', scoreClass)}>
                {score}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </button>
  );
}
