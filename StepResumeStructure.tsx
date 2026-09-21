import { Textarea } from '@/components/ui/textarea';
import { FileText, Lightbulb } from 'lucide-react';

interface StepResumeStructureProps {
  value: string;
  onChange: (value: string) => void;
}

const EXAMPLE_STRUCTURE = `# [Your Name]
[Email] | [Phone] | [LinkedIn]

## Summary
[2-3 sentence professional summary highlighting your key strengths and experience]

## Experience
### [Job Title] | [Company] | [Start Date] - [End Date]
- [Achievement with measurable impact]
- [Key responsibility or project]
- [Relevant skill demonstration]

## Skills
[Skill 1], [Skill 2], [Skill 3], [Skill 4]

## Education
[Degree] | [University] | [Year]`;

export function StepResumeStructure({ value, onChange }: StepResumeStructureProps) {
  return (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-semibold text-foreground">
          Define Your Resume Structure
        </h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          This template will be used to generate tailored 1-page resumes for each job.
          Use placeholders for dynamic content.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Editor */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm font-medium text-foreground">
            <FileText className="w-4 h-4" />
            Resume Template
          </div>
          <Textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={EXAMPLE_STRUCTURE}
            className="min-h-[400px] font-mono text-sm resize-none"
          />
          <p className="text-xs text-muted-foreground">
            {value.length} characters • Use markdown formatting
          </p>
        </div>

        {/* Tips */}
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm font-medium text-foreground">
            <Lightbulb className="w-4 h-4 text-warning" />
            Tips for a great resume structure
          </div>
          
          <div className="space-y-4 p-4 rounded-lg bg-muted/30 border border-border">
            <div className="space-y-2">
              <h4 className="font-medium text-foreground text-sm">Keep it to 1 page</h4>
              <p className="text-sm text-muted-foreground">
                Recruiters spend 6-7 seconds on initial scan. Make every word count.
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium text-foreground text-sm">Use action verbs</h4>
              <p className="text-sm text-muted-foreground">
                Start bullet points with "Led", "Built", "Increased", "Reduced", etc.
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium text-foreground text-sm">Quantify achievements</h4>
              <p className="text-sm text-muted-foreground">
                Include numbers: "Increased revenue by 40%", "Led team of 5", etc.
              </p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium text-foreground text-sm">Use placeholders</h4>
              <p className="text-sm text-muted-foreground">
                Use [brackets] for content that will be tailored per job application.
              </p>
            </div>
          </div>

          <button
            onClick={() => onChange(EXAMPLE_STRUCTURE)}
            className="text-sm text-primary hover:underline"
          >
            Use example template
          </button>
        </div>
      </div>
    </div>
  );
}
