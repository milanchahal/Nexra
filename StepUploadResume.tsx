import { useCallback, useState } from 'react';
import { Upload, FileText, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface StepUploadResumeProps {
  isLoading: boolean;
  resumeUploaded: boolean;
  parsedSkills: string[];
  onUpload: (file: File) => void;
}

export function StepUploadResume({
  isLoading,
  resumeUploaded,
  parsedSkills,
  onUpload,
}: StepUploadResumeProps) {
  const [dragActive, setDragActive] = useState(false);
  const [fileName, setFileName] = useState<string>('');

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const file = e.dataTransfer.files[0];
        setFileName(file.name);
        onUpload(file);
      }
    },
    [onUpload]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        setFileName(file.name);
        onUpload(file);
      }
    },
    [onUpload]
  );

  return (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-semibold text-foreground">
          Upload Your Resume
        </h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          We'll extract your skills, experience, and projects to build your profile.
          This is the only time you need to upload.
        </p>
      </div>

      {!resumeUploaded ? (
        <div
          className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all ${
            dragActive
              ? 'border-primary bg-primary/5'
              : 'border-border hover:border-primary/50 hover:bg-muted/30'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {isLoading ? (
            <div className="space-y-4">
              <Loader2 className="w-12 h-12 mx-auto text-primary animate-spin" />
              <div className="space-y-2">
                <p className="font-medium text-foreground">Parsing resume...</p>
                <p className="text-sm text-muted-foreground">
                  Extracting skills, experience, and projects
                </p>
              </div>
            </div>
          ) : (
            <>
              <Upload className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <div className="space-y-2">
                <p className="font-medium text-foreground">
                  Drag and drop your resume here
                </p>
                <p className="text-sm text-muted-foreground">
                  or click to browse (PDF or DOCX)
                </p>
              </div>
              <input
                type="file"
                accept=".pdf,.docx,.doc"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={handleFileSelect}
              />
            </>
          )}
        </div>
      ) : (
        <div className="border border-border rounded-xl p-8 bg-card">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-success/20 flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-6 h-6 text-success" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <FileText className="w-5 h-5 text-muted-foreground" />
                <span className="font-medium text-foreground truncate">
                  {fileName || 'Resume.pdf'}
                </span>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Resume parsed successfully! We found the following skills:
              </p>
              <div className="flex flex-wrap gap-2">
                {parsedSkills.map((skill) => (
                  <Badge key={skill} variant="secondary">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-border">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setFileName('');
                // Parent should reset resumeUploaded state
              }}
            >
              Upload different resume
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
