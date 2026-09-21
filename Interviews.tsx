import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { EmptyState } from '@/components/dashboard/EmptyState';
import { interviewsApi } from '@/lib/api';
import type { Interview } from '@/types';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import {
  Calendar,
  Loader2,
  Building2,
  Clock,
  Video,
  User,
  Save,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const stageConfig = {
  phone_screen: { label: 'Phone Screen', color: 'badge-new' },
  technical: { label: 'Technical', color: 'badge-interview' },
  behavioral: { label: 'Behavioral', color: 'badge-applied' },
  onsite: { label: 'On-site', color: 'badge-ready' },
  final: { label: 'Final Round', color: 'badge-ready' },
};

export default function Interviews() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingNotes, setEditingNotes] = useState<string | null>(null);
  const [notesValue, setNotesValue] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    loadInterviews();
  }, []);

  async function loadInterviews() {
    setIsLoading(true);
    try {
      const response = await interviewsApi.getInterviews();
      setInterviews(response.data);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSaveNotes(interviewId: string) {
    try {
      await interviewsApi.updateInterviewNotes(interviewId, notesValue);
      setInterviews((prev) =>
        prev.map((i) =>
          i.id === interviewId ? { ...i, notes: notesValue } : i
        )
      );
      setEditingNotes(null);
      toast({
        title: 'Notes saved',
        description: 'Your interview notes have been updated.',
      });
    } catch (error) {
      toast({
        title: 'Failed to save',
        description: 'Please try again.',
        variant: 'destructive',
      });
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Interviews</h1>
          <p className="text-muted-foreground">
            Manage your upcoming interviews and prep notes
          </p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : interviews.length === 0 ? (
          <EmptyState
            icon={Calendar}
            title="No interviews scheduled"
            description="When you receive interview invites, they'll appear here with all the details you need."
          />
        ) : (
          <div className="space-y-4">
            {interviews.map((interview) => {
              const stage = stageConfig[interview.stage];
              const interviewDate = new Date(interview.scheduledAt);
              const isEditing = editingNotes === interview.id;

              return (
                <div
                  key={interview.id}
                  className="border border-border rounded-xl bg-card p-6 space-y-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-lg bg-muted flex items-center justify-center overflow-hidden">
                        {interview.application.job.companyLogo ? (
                          <img
                            src={interview.application.job.companyLogo}
                            alt={interview.application.job.company}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <Building2 className="w-6 h-6 text-muted-foreground" />
                        )}
                      </div>
                      <div>
                        <h3 className="font-medium text-foreground">
                          {interview.application.job.role}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {interview.application.job.company}
                        </p>
                        <Badge className={cn('mt-2', stage.color)}>
                          {stage.label}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-foreground">
                        {interviewDate.toLocaleDateString(undefined, {
                          weekday: 'short',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {interviewDate.toLocaleTimeString(undefined, {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1.5">
                      <Clock className="w-4 h-4" />
                      {interview.duration} min
                    </span>
                    {interview.interviewerName && (
                      <span className="flex items-center gap-1.5">
                        <User className="w-4 h-4" />
                        {interview.interviewerName}
                      </span>
                    )}
                    {interview.meetingLink && (
                      <a
                        href={interview.meetingLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 text-primary hover:underline"
                      >
                        <Video className="w-4 h-4" />
                        Join Meeting
                      </a>
                    )}
                  </div>

                  <div className="pt-4 border-t border-border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-foreground">
                        Prep Notes
                      </span>
                      {isEditing ? (
                        <Button
                          size="sm"
                          onClick={() => handleSaveNotes(interview.id)}
                        >
                          <Save className="w-3.5 h-3.5 mr-1.5" />
                          Save
                        </Button>
                      ) : (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setEditingNotes(interview.id);
                            setNotesValue(interview.notes);
                          }}
                        >
                          Edit
                        </Button>
                      )}
                    </div>
                    {isEditing ? (
                      <Textarea
                        value={notesValue}
                        onChange={(e) => setNotesValue(e.target.value)}
                        placeholder="Add your interview prep notes..."
                        rows={4}
                      />
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        {interview.notes || 'No notes added yet.'}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
