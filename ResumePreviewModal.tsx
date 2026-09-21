import type { TailoredResume } from '@/types';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Download, Eye } from 'lucide-react';

interface ResumePreviewModalProps {
  isOpen: boolean;
  resume: TailoredResume | null;
  jobTitle: string;
  company: string;
  onClose: () => void;
  onApprove: () => void;
}

export function ResumePreviewModal({
  isOpen,
  resume,
  jobTitle,
  company,
  onClose,
  onApprove,
}: ResumePreviewModalProps) {
  if (!resume) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Tailored Resume Preview</span>
            <div className="flex items-center gap-2">
              <span className="text-sm font-normal text-muted-foreground">
                Match Score
              </span>
              <Badge variant="secondary" className="badge-ready">
                {resume.matchScore}%
              </Badge>
            </div>
          </DialogTitle>
          <p className="text-sm text-muted-foreground">
            Tailored for {jobTitle} at {company}
          </p>
        </DialogHeader>

        {/* Keywords */}
        <div className="flex flex-wrap gap-2 py-4 border-b border-border">
          <span className="text-sm text-muted-foreground">Keywords matched:</span>
          {resume.highlightedKeywords.map((keyword) => (
            <Badge key={keyword} variant="outline" className="bg-primary/10 text-primary border-primary/30">
              {keyword}
            </Badge>
          ))}
        </div>

        {/* Resume preview */}
        <div className="flex-1 overflow-y-auto">
          <div className="bg-white text-gray-900 p-8 rounded-lg shadow-inner min-h-[500px]">
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
              {resume.content}
            </pre>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-border">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Download PDF
          </Button>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose}>
              <Eye className="mr-2 h-4 w-4" />
              Continue Editing
            </Button>
            <Button onClick={onApprove}>
              <CheckCircle className="mr-2 h-4 w-4" />
              Approve & Apply
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
