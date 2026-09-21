// components/AppliedConfirmModal.tsx
// Modal asking user if they have applied for this job
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Send, Clock, X } from 'lucide-react';

interface AppliedConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirmApplied: () => void;
  jobTitle: string;
  companyName: string;
}

export function AppliedConfirmModal({
  isOpen,
  onClose,
  onConfirmApplied,
  jobTitle,
  companyName,
}: AppliedConfirmModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Send className="w-5 h-5 text-green-500" />
            Did you apply for this job?
          </DialogTitle>
          <DialogDescription className="text-left">
            <span className="font-semibold text-foreground">{jobTitle}</span>
            <br />
            at {companyName}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <p className="text-sm text-muted-foreground">
            If you've already applied externally, let us know to track your application and avoid showing this job again.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <Button
            onClick={onConfirmApplied}
            className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
          >
            <Send className="w-4 h-4 mr-2" />
            Yes, I Applied!
          </Button>
          
          <Button
            variant="outline"
            onClick={onClose}
            className="w-full"
          >
            <Clock className="w-4 h-4 mr-2" />
            Not Yet / Later
          </Button>
          
          <button
            onClick={onClose}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Don't ask again for this job
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
