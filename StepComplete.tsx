import { Button } from '@/components/ui/button';
import { Sparkles, CheckCircle, Loader2 } from 'lucide-react';

interface StepCompleteProps {
  isLoading: boolean;
  onBuild: () => void;
}

const FEATURES = [
  'AI-powered job matching based on your profile',
  'Tailored 1-page resumes for each application',
  'Keyword optimization for ATS systems',
  'Application tracking and interview prep',
];

export function StepComplete({ isLoading, onBuild }: StepCompleteProps) {
  return (
    <div className="space-y-8 text-center">
      <div className="space-y-4">
        <div className="w-20 h-20 rounded-2xl bg-primary/20 flex items-center justify-center mx-auto">
          <Sparkles className="w-10 h-10 text-primary" />
        </div>
        <h2 className="text-2xl font-semibold text-foreground">
          Ready to Build Your Profile!
        </h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          We have everything we need to create your AI-powered job application copilot.
        </p>
      </div>

      <div className="max-w-md mx-auto">
        <div className="p-6 rounded-xl bg-card border border-border space-y-4">
          <h3 className="font-medium text-foreground">What happens next:</h3>
          <ul className="space-y-3 text-left">
            {FEATURES.map((feature, index) => (
              <li key={index} className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                <span className="text-sm text-muted-foreground">{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <Button
        size="lg"
        onClick={onBuild}
        disabled={isLoading}
        className="px-8"
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Building profile...
          </>
        ) : (
          <>
            <Sparkles className="mr-2 h-5 w-5" />
            Build My Profile
          </>
        )}
      </Button>
    </div>
  );
}
