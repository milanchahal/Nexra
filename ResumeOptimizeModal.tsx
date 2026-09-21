// components/ResumeOptimizeModal.tsx
// Jobright-style Resume Optimization Modal with Step-by-Step Workflow
import { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogDescription 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { atsApi, ReplacementItem, SuggestReplacementsResponse, ApplyReplacementsResponse } from '@/lib/api';
import {
  Sparkles,
  Loader2,
  CheckCircle,
  ArrowRight,
  Download,
  Eye,
  FileText,
  Zap,
  Target,
  TrendingUp,
  X,
  RefreshCw,
  ChevronRight,
  AlertCircle,
} from 'lucide-react';

interface ResumeOptimizeModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobId: string;
  jobTitle: string;
  companyName: string;
  onOptimized?: (resumeId: string) => void;
}

type Step = 'analyzing' | 'review' | 'applying' | 'complete';

export function ResumeOptimizeModal({
  isOpen,
  onClose,
  jobId,
  jobTitle,
  companyName,
  onOptimized
}: ResumeOptimizeModalProps) {
  const [step, setStep] = useState<Step>('analyzing');
  const [suggestions, setSuggestions] = useState<SuggestReplacementsResponse | null>(null);
  const [replacements, setReplacements] = useState<ReplacementItem[]>([]);
  const [result, setResult] = useState<ApplyReplacementsResponse | null>(null);
  const [showDiff, setShowDiff] = useState(false);
  const [diffData, setDiffData] = useState<{ original: string; modified: string } | null>(null);
  const { toast } = useToast();

  // Step 1: Get suggestions
  const suggestMutation = useMutation({
    mutationFn: () => atsApi.suggestReplacements(jobId),
    onSuccess: (data) => {
      setSuggestions(data);
      // Initialize replacements with approved=true by default
      setReplacements(data.replacements.map(r => ({ ...r, approved: true })));
      setStep('review');
    },
    onError: (error: Error) => {
      toast({ 
        title: 'Analysis failed', 
        description: error.message,
        variant: 'destructive' 
      });
      onClose();
    }
  });

  // Step 2: Preview diff
  const previewMutation = useMutation({
    mutationFn: () => atsApi.previewDiff(jobId, replacements),
    onSuccess: (data) => {
      setDiffData({ original: data.original_text, modified: data.modified_text });
      setShowDiff(true);
    }
  });

  // Step 3: Apply replacements
  const applyMutation = useMutation({
    mutationFn: () => atsApi.applyReplacements(jobId, replacements.filter(r => r.approved)),
    onSuccess: (data) => {
      setResult(data);
      setStep('complete');
      onOptimized?.(data.optimized_resume_id);
    },
    onError: (error: Error) => {
      toast({ 
        title: 'Optimization failed', 
        description: error.message,
        variant: 'destructive' 
      });
      setStep('review');
    }
  });

  // Start analysis when modal opens
  useEffect(() => {
    if (isOpen && step === 'analyzing') {
      suggestMutation.mutate();
    }
  }, [isOpen]);

  // Reset on close
  const handleClose = () => {
    setStep('analyzing');
    setSuggestions(null);
    setReplacements([]);
    setResult(null);
    setShowDiff(false);
    setDiffData(null);
    onClose();
  };

  // Toggle replacement approval
  const toggleReplacement = (index: number) => {
    setReplacements(prev => 
      prev.map((r, i) => i === index ? { ...r, approved: !r.approved } : r)
    );
  };

  // Select/Deselect all
  const toggleAll = (approved: boolean) => {
    setReplacements(prev => prev.map(r => ({ ...r, approved })));
  };

  // Apply changes
  const handleApply = () => {
    const approvedCount = replacements.filter(r => r.approved).length;
    if (approvedCount === 0) {
      toast({ title: 'Select at least one change', variant: 'destructive' });
      return;
    }
    setStep('applying');
    applyMutation.mutate();
  };

  // Download PDF
  const handleDownload = async () => {
    if (!result?.optimized_resume_id) return;
    
    try {
      const blob = await atsApi.downloadPdf(result.optimized_resume_id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Resume_${jobTitle.replace(/\s+/g, '_')}_${companyName.replace(/\s+/g, '_')}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      toast({ title: '✅ PDF Downloaded!' });
    } catch (error) {
      toast({ title: 'Download failed', variant: 'destructive' });
    }
  };

  const approvedCount = replacements.filter(r => r.approved).length;
  const totalCount = replacements.length;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-500" />
            ATS Resume Optimization
          </DialogTitle>
          <DialogDescription>
            {jobTitle} at {companyName}
          </DialogDescription>
        </DialogHeader>

        {/* Step Progress */}
        <div className="flex items-center justify-between px-2 py-3 bg-muted/30 rounded-lg mb-4">
          <StepIndicator 
            number={1} 
            label="Analyze" 
            active={step === 'analyzing'} 
            complete={['review', 'applying', 'complete'].includes(step)} 
          />
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
          <StepIndicator 
            number={2} 
            label="Review Changes" 
            active={step === 'review'} 
            complete={['applying', 'complete'].includes(step)} 
          />
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
          <StepIndicator 
            number={3} 
            label="Apply" 
            active={step === 'applying'} 
            complete={step === 'complete'} 
          />
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
          <StepIndicator 
            number={4} 
            label="Download" 
            active={step === 'complete'} 
            complete={false} 
          />
        </div>

        {/* Step Content */}
        <div className="flex-1 overflow-y-auto">
          {/* Step 1: Analyzing */}
          {step === 'analyzing' && (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-12 h-12 animate-spin text-purple-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Analyzing Job Requirements...</h3>
              <p className="text-muted-foreground text-center max-w-md">
                Extracting ATS keywords and finding optimization opportunities in your resume.
              </p>
              <div className="mt-6 space-y-2 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-yellow-500" />
                  <span>Parsing job description keywords...</span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-blue-500" />
                  <span>Comparing with your resume...</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-green-500" />
                  <span>Generating smart replacements...</span>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Review */}
          {step === 'review' && suggestions && (
            <div className="space-y-4">
              {/* Score Banner */}
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-xl border border-purple-500/20">
                <div>
                  <p className="text-sm text-muted-foreground">Current ATS Score</p>
                  <p className="text-3xl font-bold text-purple-500">{(suggestions.current_score / 10).toFixed(1)}<span className="text-lg text-muted-foreground">/10</span></p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {suggestions.current_score >= 80 ? '🔥 Strong Match' : 
                     suggestions.current_score >= 60 ? '✨ Good Match' : 
                     suggestions.current_score >= 40 ? '⚡ Fair Match' : '⚠️ Needs Work'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Keywords Found</p>
                  <div className="flex flex-wrap gap-1 justify-end max-w-[200px]">
                    {suggestions.keywords_found.slice(0, 5).map((kw, i) => (
                      <Badge key={i} variant="outline" className="text-xs">{kw}</Badge>
                    ))}
                    {suggestions.keywords_found.length > 5 && (
                      <Badge variant="secondary" className="text-xs">+{suggestions.keywords_found.length - 5}</Badge>
                    )}
                  </div>
                </div>
              </div>

              {/* Replacements List */}
              <div className="border rounded-xl overflow-hidden">
                <div className="flex items-center justify-between p-3 bg-muted/50 border-b">
                  <h4 className="font-medium">Suggested Changes ({totalCount})</h4>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm" onClick={() => toggleAll(true)}>
                      Select All
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => toggleAll(false)}>
                      Deselect All
                    </Button>
                  </div>
                </div>
                
                {replacements.length === 0 ? (
                  <div className="p-8 text-center text-muted-foreground">
                    <AlertCircle className="w-10 h-10 mx-auto mb-2 opacity-50" />
                    <p>No optimization suggestions found. Your resume is already well-optimized for this job!</p>
                  </div>
                ) : (
                  <div className="divide-y max-h-[300px] overflow-y-auto">
                    {replacements.map((r, index) => (
                      <div 
                        key={index} 
                        className={`p-3 flex items-start gap-3 hover:bg-muted/30 transition-colors ${
                          r.approved ? '' : 'opacity-50'
                        }`}
                      >
                        <Checkbox 
                          checked={r.approved}
                          onCheckedChange={() => toggleReplacement(index)}
                          className="mt-1"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-red-500 line-through text-sm">{r.original}</span>
                            <ArrowRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                            <span className="text-green-500 font-medium text-sm">{r.replacement}</span>
                          </div>
                          {r.context && (
                            <p className="text-xs text-muted-foreground mt-1 truncate">
                              Context: {r.context.slice(0, 100)}...
                            </p>
                          )}
                          {r.reason && (
                            <p className="text-xs text-blue-500 mt-1">{r.reason}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Selected Summary */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">
                  {approvedCount} of {totalCount} changes selected
                </span>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => previewMutation.mutate()}
                  disabled={previewMutation.isPending}
                >
                  {previewMutation.isPending ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <Eye className="w-4 h-4 mr-2" />
                  )}
                  Preview Diff
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Applying */}
          {step === 'applying' && (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-12 h-12 animate-spin text-green-500 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Applying Optimizations...</h3>
              <p className="text-muted-foreground text-center max-w-md">
                Making surgical keyword replacements while preserving your resume structure.
              </p>
              <Progress value={60} className="w-48 mt-4" />
            </div>
          )}

          {/* Step 4: Complete */}
          {step === 'complete' && result && (
            <div className="space-y-6">
              {/* Success Banner */}
              <div className="flex items-center gap-4 p-6 bg-gradient-to-r from-green-500/10 to-emerald-500/10 rounded-xl border border-green-500/30">
                <CheckCircle className="w-12 h-12 text-green-500" />
                <div>
                  <h3 className="text-xl font-bold text-green-500">Optimization Complete!</h3>
                  <p className="text-muted-foreground">
                    {result.changes_applied} keyword optimizations applied successfully
                  </p>
                </div>
              </div>

              {/* Score Comparison */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-muted/30 text-center">
                  <p className="text-sm text-muted-foreground mb-1">Original Score</p>
                  <p className="text-3xl font-bold text-muted-foreground">{(result.original_score / 10).toFixed(1)}<span className="text-lg">/10</span></p>
                </div>
                <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/30 text-center">
                  <p className="text-sm text-muted-foreground mb-1">Optimized Score</p>
                  <p className="text-3xl font-bold text-green-500">{(result.optimized_score / 10).toFixed(1)}<span className="text-lg text-green-400">/10</span></p>
                  <Badge className="bg-green-500/20 text-green-400 mt-1">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    +{(result.score_improvement / 10).toFixed(1)} pts
                  </Badge>
                </div>
              </div>

              {/* Changes Made */}
              <div className="border rounded-xl p-4">
                <h4 className="font-medium mb-3">Changes Applied</h4>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {result.changes_made.map((change, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                      <span className="text-muted-foreground">{change}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Validation */}
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Page count preserved
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Links preserved
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Diff Modal */}
        {showDiff && diffData && (
          <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
            <div className="bg-background rounded-xl w-full max-w-4xl max-h-[80vh] flex flex-col">
              <div className="flex items-center justify-between p-4 border-b">
                <h3 className="font-semibold">Text Diff Preview</h3>
                <Button variant="ghost" size="icon" onClick={() => setShowDiff(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex-1 overflow-hidden grid grid-cols-2 divide-x">
                <div className="p-4 overflow-y-auto">
                  <h4 className="text-sm font-medium text-red-500 mb-2">Original</h4>
                  <pre className="text-xs whitespace-pre-wrap text-muted-foreground">
                    {diffData.original.slice(0, 3000)}
                  </pre>
                </div>
                <div className="p-4 overflow-y-auto">
                  <h4 className="text-sm font-medium text-green-500 mb-2">Optimized</h4>
                  <pre className="text-xs whitespace-pre-wrap text-muted-foreground">
                    {diffData.modified.slice(0, 3000)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <Button variant="ghost" onClick={handleClose}>
            {step === 'complete' ? 'Close' : 'Cancel'}
          </Button>
          
          <div className="flex gap-2">
            {step === 'review' && (
              <Button 
                onClick={handleApply}
                disabled={approvedCount === 0}
                className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Apply {approvedCount} Changes
              </Button>
            )}
            
            {step === 'complete' && (
              <Button 
                onClick={handleDownload}
                className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600"
              >
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Step Indicator Component
function StepIndicator({ 
  number, 
  label, 
  active, 
  complete 
}: { 
  number: number; 
  label: string; 
  active: boolean; 
  complete: boolean; 
}) {
  return (
    <div className={`flex items-center gap-2 ${active ? 'text-purple-500' : complete ? 'text-green-500' : 'text-muted-foreground'}`}>
      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium
        ${active ? 'bg-purple-500 text-white' : complete ? 'bg-green-500 text-white' : 'bg-muted'}`}>
        {complete ? <CheckCircle className="w-4 h-4" /> : number}
      </div>
      <span className="text-sm font-medium hidden sm:inline">{label}</span>
    </div>
  );
}
