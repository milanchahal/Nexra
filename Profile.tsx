// pages/Profile.tsx - Enhanced Profile Page with Resume Upload
import { useState, useEffect, useRef } from 'react';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { profileApi } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import {
  User,
  Briefcase,
  GraduationCap,
  Code,
  Upload,
  FileText,
  Loader2,
  CheckCircle,
  AlertCircle,
  Mail,
  MapPin,
  Phone,
  Linkedin,
  Github,
  Globe,
  Sparkles,
  RefreshCw,
  FileUp,
  Trash2,
} from 'lucide-react';

interface ProfileData {
  id?: string;
  user_id?: string;
  email?: string;
  full_name?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  skills?: string[];
  summary?: string;
  experience?: any[];
  education?: any[];
  projects?: any[];
  raw_resume_text?: string;
  resume_filename?: string;
  created_at?: string;
  updated_at?: string;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    setIsLoading(true);
    try {
      const response = await profileApi.getProfile();
      setProfile(response as unknown as ProfileData);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setIsLoading(false);
    }
  }

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
      toast({ 
        title: 'Invalid file type', 
        description: 'Please upload a PDF, DOC, DOCX, or TXT file',
        variant: 'destructive' 
      });
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      toast({ 
        title: 'File too large', 
        description: 'Please upload a file smaller than 5MB',
        variant: 'destructive' 
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 90));
    }, 200);

    try {
      const result = await profileApi.uploadResume(file);
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      if (result.success) {
        toast({ 
          title: '✅ Resume Uploaded!', 
          description: 'Your resume has been parsed and saved. ATS optimization is now available!' 
        });
        // Reload profile to get updated data
        await loadProfile();
      } else {
        throw new Error(result.message || 'Upload failed');
      }
    } catch (error: any) {
      clearInterval(progressInterval);
      toast({ 
        title: 'Upload failed', 
        description: error.message || 'Something went wrong',
        variant: 'destructive' 
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  const hasResume = !!profile?.raw_resume_text;
  const skills = profile?.skills || [];
  const experience = profile?.experience || [];
  const education = profile?.education || [];
  const projects = profile?.projects || [];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <User className="w-7 h-7" /> Profile
            </h1>
            <p className="text-muted-foreground">
              Your professional profile used for job matching and ATS optimization
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={loadProfile}>
              <RefreshCw className="w-4 h-4 mr-2" /> Refresh
            </Button>
          </div>
        </div>

        {/* Resume Upload Card - PROMINENT */}
        <div className={`border-2 rounded-2xl p-6 transition-all ${
          hasResume 
            ? 'border-emerald-500/50 bg-emerald-500/5' 
            : 'border-dashed border-yellow-500/50 bg-yellow-500/5'
        }`}>
          <div className="flex items-start gap-6">
            {/* Status Icon */}
            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center flex-shrink-0 ${
              hasResume 
                ? 'bg-emerald-500/20 text-emerald-500' 
                : 'bg-yellow-500/20 text-yellow-500'
            }`}>
              {hasResume ? <CheckCircle className="w-8 h-8" /> : <AlertCircle className="w-8 h-8" />}
            </div>

            {/* Info */}
            <div className="flex-1">
              <h2 className="text-lg font-semibold mb-1">
                {hasResume ? '✅ Resume Uploaded' : '⚠️ Resume Required'}
              </h2>
              <p className="text-muted-foreground text-sm mb-4">
                {hasResume 
                  ? `Your resume "${profile?.resume_filename || 'resume'}" has been processed. ATS optimization is ready!`
                  : 'Upload your resume to enable ATS scoring and job-specific resume optimization.'}
              </p>

              {/* Upload Progress */}
              {isUploading && (
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Processing resume...</span>
                    <span className="text-sm text-muted-foreground">{uploadProgress}%</span>
                  </div>
                  <Progress value={uploadProgress} className="h-2" />
                </div>
              )}

              {/* Upload Button */}
              <div className="flex gap-3">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx,.txt"
                  className="hidden"
                />
                <Button 
                  onClick={handleFileSelect}
                  disabled={isUploading}
                  className={hasResume 
                    ? 'bg-emerald-500 hover:bg-emerald-600' 
                    : 'bg-yellow-500 hover:bg-yellow-600 text-black'
                  }
                >
                  <Upload className="w-4 h-4 mr-2" />
                  {hasResume ? 'Update Resume' : 'Upload Resume'}
                </Button>
                {hasResume && (
                  <Button variant="outline" onClick={() => {
                    const element = document.getElementById('resume-preview');
                    element?.scrollIntoView({ behavior: 'smooth' });
                  }}>
                    <FileText className="w-4 h-4 mr-2" /> View Resume
                  </Button>
                )}
              </div>

              <p className="text-xs text-muted-foreground mt-3">
                Accepted: PDF, DOC, DOCX, TXT • Max size: 5MB
              </p>
            </div>

            {/* ATS Readiness */}
            <div className="text-right flex-shrink-0">
              <div className={`text-3xl font-bold ${hasResume ? 'text-emerald-500' : 'text-yellow-500'}`}>
                {hasResume ? '100%' : '0%'}
              </div>
              <p className="text-xs text-muted-foreground">ATS Ready</p>
            </div>
          </div>
        </div>

        {/* Profile Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Skills */}
          <div className="lg:col-span-2 border border-border rounded-xl bg-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Code className="w-5 h-5 text-emerald-500" />
              <h2 className="font-semibold text-foreground">Skills</h2>
              {skills.length > 0 && (
                <Badge variant="secondary" className="ml-auto">{skills.length} skills</Badge>
              )}
            </div>
            {skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {skills.map((skill: string, idx: number) => (
                  <Badge 
                    key={idx} 
                    variant="outline"
                    className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                  >
                    {skill}
                  </Badge>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Code className="w-12 h-12 mx-auto mb-2 opacity-30" />
                <p>Skills will appear after uploading your resume</p>
              </div>
            )}
          </div>

          {/* Summary */}
          <div className="border border-border rounded-xl bg-card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-purple-500" />
              <h2 className="font-semibold text-foreground">Summary</h2>
            </div>
            {profile?.summary ? (
              <p className="text-sm text-muted-foreground leading-relaxed">
                {profile.summary}
              </p>
            ) : (
              <div className="text-center py-4 text-muted-foreground">
                <p className="text-sm">Summary extracted from resume</p>
              </div>
            )}
          </div>

          {/* Raw Resume Preview */}
          {profile?.raw_resume_text && (
            <div id="resume-preview" className="lg:col-span-3 border border-border rounded-xl bg-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-5 h-5 text-blue-500" />
                <h2 className="font-semibold text-foreground">Resume Content</h2>
                <Badge variant="outline" className="ml-auto">
                  {profile.raw_resume_text.split(/\s+/).length} words
                </Badge>
              </div>
              <div className="bg-muted/30 rounded-lg p-4 max-h-80 overflow-y-auto border border-border">
                <pre className="text-sm text-muted-foreground whitespace-pre-wrap font-mono leading-relaxed">
                  {profile.raw_resume_text}
                </pre>
              </div>
            </div>
          )}

          {/* Experience */}
          {experience.length > 0 && (
            <div className="lg:col-span-2 border border-border rounded-xl bg-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <Briefcase className="w-5 h-5 text-blue-500" />
                <h2 className="font-semibold text-foreground">Experience</h2>
                <Badge variant="secondary" className="ml-auto">{experience.length}</Badge>
              </div>
              <div className="space-y-6">
                {experience.map((exp: any, idx: number) => (
                  <div key={idx} className="flex gap-4">
                    <div className="w-3 h-3 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-medium text-foreground">{exp.role || exp.title}</h3>
                          <p className="text-sm text-muted-foreground">{exp.company}</p>
                        </div>
                        <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                          {exp.startDate || exp.start_date} - {exp.isCurrent || exp.is_current ? 'Present' : (exp.endDate || exp.end_date)}
                        </span>
                      </div>
                      {exp.description && (
                        <p className="text-sm text-muted-foreground mt-2">{exp.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education */}
          {education.length > 0 && (
            <div className="border border-border rounded-xl bg-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <GraduationCap className="w-5 h-5 text-purple-500" />
                <h2 className="font-semibold text-foreground">Education</h2>
              </div>
              <div className="space-y-4">
                {education.map((edu: any, idx: number) => (
                  <div key={idx} className="border-l-2 border-purple-500/50 pl-4">
                    <h3 className="font-medium text-foreground">{edu.degree}</h3>
                    <p className="text-sm text-muted-foreground">{edu.institution}</p>
                    <p className="text-xs text-muted-foreground">{edu.field} • {edu.endDate || edu.end_date}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Projects */}
          {projects.length > 0 && (
            <div className="lg:col-span-3 border border-border rounded-xl bg-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <Code className="w-5 h-5 text-orange-500" />
                <h2 className="font-semibold text-foreground">Projects</h2>
                <Badge variant="secondary" className="ml-auto">{projects.length}</Badge>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projects.map((project: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-lg bg-muted/30 border border-border hover:border-orange-500/50 transition-colors">
                    <h3 className="font-medium text-foreground mb-1">{project.name}</h3>
                    <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{project.description}</p>
                    {project.technologies && (
                      <div className="flex flex-wrap gap-1">
                        {project.technologies.slice(0, 4).map((tech: string, techIdx: number) => (
                          <Badge key={techIdx} variant="outline" className="text-xs">
                            {tech}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Empty State for new profiles */}
        {!hasResume && skills.length === 0 && experience.length === 0 && (
          <div className="text-center py-12 border border-dashed border-border rounded-xl">
            <FileUp className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">Complete Your Profile</h2>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Upload your resume to automatically populate your skills, experience, and education. 
              This enables ATS scoring and resume optimization for each job.
            </p>
            <Button 
              onClick={handleFileSelect}
              size="lg"
              className="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700"
            >
              <Upload className="w-5 h-5 mr-2" /> Upload Your Resume Now
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
