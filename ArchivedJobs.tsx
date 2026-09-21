// pages/ArchivedJobs.tsx - Archived Jobs Page
import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { jobsApi } from '@/lib/api';
import { Job } from '@/types';
import { Loader2, MapPin, Building2, RotateCcw, Trash2, Archive } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';

export default function ArchivedJobs() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: jobs = [], isLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: jobsApi.getJobs,
  });

  // Filter archived jobs
  const archivedJobs = jobs.filter(job => job.status === 'archived');

  const handleRestore = async (jobId: string) => {
    try {
      // Restore to discovered status
      await jobsApi.updateJobStatus(jobId, 'discovered');
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      toast({ title: 'Job restored to New Jobs' });
    } catch (error) {
      toast({ title: 'Error', variant: 'destructive' });
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div>
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Archived Jobs</h1>
          <p className="text-muted-foreground">{archivedJobs.length} archived jobs</p>
        </div>

        {/* Empty State */}
        {archivedJobs.length === 0 && (
          <div className="text-center py-16 border border-dashed border-border rounded-xl">
            <Archive className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">No archived jobs</h2>
            <p className="text-muted-foreground">Archived jobs will appear here</p>
          </div>
        )}

        {/* Archived List */}
        <div className="space-y-2">
          {archivedJobs.map(job => (
            <div
              key={job.id}
              className="bg-card/50 border border-border rounded-lg p-3 flex items-center gap-4 opacity-70 hover:opacity-100 transition-opacity"
            >
              {/* Job Info */}
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-foreground text-sm">
                  {job.job_title}
                </h3>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Building2 className="w-3 h-3" />
                    {job.company_name}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {job.location || 'Remote'}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => handleRestore(job.id)}
                className="text-xs"
              >
                <RotateCcw className="w-3 h-3 mr-1" /> Restore
              </Button>
            </div>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
