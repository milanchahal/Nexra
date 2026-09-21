import { useState } from 'react';
import type { Job, TailoredResume } from '@/types';
import { jobsApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ResumePreviewModal } from '@/components/dashboard/ResumePreviewModal';
import {
  X,
  MapPin,
  Building2,
  DollarSign,
  FileText,
  Send,
  Loader2,
  Sparkles,
  CheckCircle,
  ExternalLink,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface JobDetailPanelProps {
  job: Job | null;
  onClose: () => void;
  onJobUpdate: (job: Job) => void;
}

const statusConfig = {
  new: { label: 'New', className: 'badge-new' },
  resume_ready: { label: 'Resume Ready', className: 'badge-ready' },
  applied: { label: 'Applied', className: 'badge-applied' },
  interview: { label: 'Interview', className: 'badge-interview' },
  rejected: { label: 'Rejected', className: 'badge-rejected' },
};

export function JobDetailPanel({ job, onClose, onJobUpdate }: JobDetailPanelProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResume, setGeneratedResume] = useState<TailoredResume | null>(null);
  const [showResumeModal, setShowResumeModal] = useState(false);
  const { toast } = useToast();

  if (!job) return null;

  const status = statusConfig[job.status];
  const scoreClass =
    job.fitScore >= 85
      ? 'score-high'
      : job.fitScore >= 70
      ? 'score-medium'
      : 'score-low';

  const handleGenerateResume = async () => {
    setIsGenerating(true);
    try {
      const result = await jobsApi.generateResume(job.id);
      if (result.success) {
        setGeneratedResume(result.data);
        onJobUpdate({ ...job, status: 'resume_ready', tailoredResumeId: result.data.id });
        toast({
          title: 'Resume generated!',
          description: 'Your tailored resume is ready for review.',
        });
        setShowResumeModal(true);
      }
    } catch (error) {
      toast({
        title: 'Generation failed',
        description: 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleApproveResume = async () => {
    if (!generatedResume) return;
    
    try {
      await jobsApi.approveResume(generatedResume.id);
      onJobUpdate({ ...job, status: 'applied', appliedAt: new Date().toISOString() });
      setShowResumeModal(false);
      toast({
        title: 'Application submitted!',
        description: `Your application to ${job.company} has been submitted.`,
      });
    } catch (error) {
      toast({
        title: 'Failed to submit',
        description: 'Please try again.',
        variant: 'destructive',
      });
    }
  };

  return (
    <>
      <div
        className={cn(
          'fixed inset-y-0 right-0 z-50 w-full max-w-lg bg-card border-l border-border shadow-xl transform transition-transform duration-300',
          job ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            <h2 className="text-lg font-semibold text-foreground">Job Details</h2>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Company info */}
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 rounded-xl bg-muted flex items-center justify-center overflow-hidden">
                {job.companyLogo ? (
                  <img
                    src={job.companyLogo}
                    alt={job.company}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <Building2 className="w-7 h-7 text-muted-foreground" />
                )}
              </div>
              <div>
                <h3 className="text-xl font-semibold text-foreground">{job.role}</h3>
                <p className="text-muted-foreground">{job.company}</p>
                <Badge className={cn('mt-2', status.className)}>{status.label}</Badge>
              </div>
            </div>

            {/* Meta info */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="w-4 h-4" />
                <span>{job.location}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Building2 className="w-4 h-4" />
                <span className="capitalize">{job.locationType}</span>
              </div>
              {job.salary && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground col-span-2">
                  <DollarSign className="w-4 h-4" />
                  <span>{job.salary}</span>
                </div>
              )}
            </div>

            {/* Fit score */}
            <div className="p-4 rounded-lg bg-muted/30 border border-border">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Job Fit Score</span>
                <span className={cn('text-2xl font-bold', scoreClass)}>
                  {job.fitScore}%
                </span>
              </div>
              <div className="mt-2 h-2 rounded-full bg-muted overflow-hidden">
                <div
                  className={cn(
                    'h-full rounded-full transition-all',
                    job.fitScore >= 85
                      ? 'bg-success'
                      : job.fitScore >= 70
                      ? 'bg-warning'
                      : 'bg-muted-foreground'
                  )}
                  style={{ width: `${job.fitScore}%` }}
                />
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <h4 className="font-medium text-foreground">About this role</h4>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {job.description}
              </p>
            </div>

            {/* Requirements */}
            <div className="space-y-2">
              <h4 className="font-medium text-foreground">Requirements</h4>
              <ul className="space-y-2">
                {job.requirements.map((req, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <CheckCircle className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Actions */}
          <div className="p-6 border-t border-border space-y-3">
            {job.status === 'new' && (
              <Button
                className="w-full"
                onClick={handleGenerateResume}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Resume...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Generate Tailored Resume
                  </>
                )}
              </Button>
            )}

            {job.status === 'resume_ready' && (
              <>
                <Button
                  className="w-full"
                  onClick={() => setShowResumeModal(true)}
                >
                  <FileText className="mr-2 h-4 w-4" />
                  View Resume
                </Button>
                <Button variant="outline" className="w-full">
                  <Send className="mr-2 h-4 w-4" />
                  Prepare Application
                </Button>
              </>
            )}

            {job.status === 'applied' && (
              <Button variant="outline" className="w-full" disabled>
                <CheckCircle className="mr-2 h-4 w-4 text-success" />
                Applied on {new Date(job.appliedAt!).toLocaleDateString()}
              </Button>
            )}

            {job.status === 'interview' && (
              <Button variant="outline" className="w-full">
                <ExternalLink className="mr-2 h-4 w-4" />
                View Interview Details
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Backdrop */}
      {job && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Resume Preview Modal */}
      <ResumePreviewModal
        isOpen={showResumeModal}
        resume={generatedResume}
        jobTitle={job.role}
        company={job.company}
        onClose={() => setShowResumeModal(false)}
        onApprove={handleApproveResume}
      />
    </>
  );
}
