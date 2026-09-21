import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { profileApi } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Briefcase, ArrowLeft, ArrowRight, Check, Loader2 } from 'lucide-react';
import { StepUploadResume } from '@/components/onboarding/StepUploadResume';
import { StepResumeStructure } from '@/components/onboarding/StepResumeStructure';
import { StepJobPreferences } from '@/components/onboarding/StepJobPreferences';
import { StepComplete } from '@/components/onboarding/StepComplete';
import type { JobPreferences } from '@/types';

const STEPS = [
  { id: 1, title: 'Upload Resume', description: 'Upload your existing resume' },
  { id: 2, title: 'Resume Structure', description: 'Set your resume template' },
  { id: 3, title: 'Job Preferences', description: 'Define your ideal job' },
  { id: 4, title: 'Build Profile', description: 'Create your profile' },
];

export default function Onboarding() {
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [resumeUploaded, setResumeUploaded] = useState(false);
  const [parsedSkills, setParsedSkills] = useState<string[]>([]);
  const [resumeStructure, setResumeStructure] = useState('');
  const [preferences, setPreferences] = useState<JobPreferences>({
    roles: [],
    locations: [],
    remotePreference: 'any',
    experienceLevel: 'any',
    companyType: 'any',
  });
  
  const navigate = useNavigate();
  const { setOnboarded } = useAuth();
  const { toast } = useToast();

  const progress = (currentStep / STEPS.length) * 100;

  const handleResumeUpload = useCallback(async (file: File) => {
    setIsLoading(true);
    try {
      const result = await profileApi.uploadResume(file);
      if (result.success) {
        setResumeUploaded(true);
        setParsedSkills(result.data.skills);
        toast({
          title: 'Resume uploaded!',
          description: 'We extracted your skills and experience.',
        });
      }
    } catch (error) {
      toast({
        title: 'Upload failed',
        description: 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const handleBuildProfile = async () => {
    setIsLoading(true);
    try {
      const result = await profileApi.buildProfile(preferences, resumeStructure);
      if (result.success) {
        localStorage.setItem('profile', JSON.stringify(result.data));
        setOnboarded();
        toast({
          title: 'Profile created!',
          description: 'Your AI copilot is ready to find jobs.',
        });
        navigate('/dashboard');
      }
    } catch (error) {
      toast({
        title: 'Failed to build profile',
        description: 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return resumeUploaded;
      case 2:
        return resumeStructure.length > 50;
      case 3:
        return preferences.roles.length > 0;
      case 4:
        return true;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.jpg" alt="Nexara AI" className="w-9 h-9 rounded-lg object-contain" />
            <span className="font-semibold text-foreground">Nexara AI</span>
          </div>
          
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground hidden sm:block">
              Step {currentStep} of {STEPS.length}
            </span>
            <div className="w-32 hidden sm:block">
              <Progress value={progress} className="h-2" />
            </div>
          </div>
        </div>
      </header>

      {/* Progress steps */}
      <div className="container max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-12">
          {STEPS.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                    step.id < currentStep
                      ? 'bg-primary text-primary-foreground'
                      : step.id === currentStep
                      ? 'bg-primary text-primary-foreground ring-4 ring-primary/20'
                      : 'bg-muted text-muted-foreground'
                  }`}
                >
                  {step.id < currentStep ? (
                    <Check className="w-5 h-5" />
                  ) : (
                    step.id
                  )}
                </div>
                <span
                  className={`mt-2 text-xs font-medium hidden md:block ${
                    step.id === currentStep
                      ? 'text-foreground'
                      : 'text-muted-foreground'
                  }`}
                >
                  {step.title}
                </span>
              </div>
              {index < STEPS.length - 1 && (
                <div
                  className={`w-12 sm:w-24 h-0.5 mx-2 ${
                    step.id < currentStep ? 'bg-primary' : 'bg-border'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step content */}
        <div className="min-h-[400px] animate-fade-in">
          {currentStep === 1 && (
            <StepUploadResume
              isLoading={isLoading}
              resumeUploaded={resumeUploaded}
              parsedSkills={parsedSkills}
              onUpload={handleResumeUpload}
            />
          )}
          {currentStep === 2 && (
            <StepResumeStructure
              value={resumeStructure}
              onChange={setResumeStructure}
            />
          )}
          {currentStep === 3 && (
            <StepJobPreferences
              preferences={preferences}
              onChange={setPreferences}
            />
          )}
          {currentStep === 4 && (
            <StepComplete
              isLoading={isLoading}
              onBuild={handleBuildProfile}
            />
          )}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8 pt-8 border-t border-border">
          <Button
            variant="ghost"
            onClick={handleBack}
            disabled={currentStep === 1 || isLoading}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          
          {currentStep < STEPS.length ? (
            <Button
              onClick={handleNext}
              disabled={!canProceed() || isLoading}
            >
              {isLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <>
                  Continue
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
