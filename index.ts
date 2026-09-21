// User & Auth Types
export interface User {
  id: string;
  email: string;
  name: string;
  isOnboarded: boolean;
  createdAt: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Profile Types
export interface Profile {
  id: string;
  userId: string;
  skills: string[];
  experience: Experience[];
  education: Education[];
  projects: Project[];
  summary: string;
  preferences: JobPreferences;
  resumeStructure: string;
  createdAt: string;
  updatedAt: string;
}

export interface Experience {
  id: string;
  company: string;
  role: string;
  startDate: string;
  endDate: string | null;
  description: string;
  isCurrent: boolean;
}

export interface Education {
  id: string;
  institution: string;
  degree: string;
  field: string;
  startDate: string;
  endDate: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  technologies: string[];
  url?: string;
}

export interface JobPreferences {
  roles: string[];
  locations: string[];
  remotePreference: 'remote' | 'hybrid' | 'onsite' | 'any';
  experienceLevel: 'entry' | 'mid' | 'senior' | 'lead' | 'any';
  companyType: 'startup' | 'mnc' | 'any';
  salaryMin?: number;
  salaryMax?: number;
}

// Job Types - aligned with backend models
export type JobStatus = 'discovered' | 'resume_ready' | 'optimized' | 'applied' | 'archived';

export interface ATSScore {
  score: number;
  skills_matched: number;
  total_skills_in_job: number;
  top_missing_skills: string[];
  title_alignment: 'low' | 'medium' | 'high';
}

export interface OptimizedResume {
  id: string;
  user_id: string;
  job_id: string;
  source_resume_version_id: string;
  optimized_text: string;
  ats_score: ATSScore;
  refinement_instructions?: string;
  created_at: string;
}

export interface Job {
  id: string;
  _id?: string; // MongoDB returns _id
  user_id: string;
  job_title: string;
  company_name: string;
  job_description: string;
  source: 'linkedin' | 'naukri' | 'company' | 'manual';
  source_url?: string;
  location?: string;
  match_score: number;
  match_explanation?: string;
  status: JobStatus;
  active_optimized_resume_id?: string;
  created_at: string;
  discovered_at: string;
  applied_at?: string;

  // Enhanced Data
  salary_min?: number;
  salary_max?: number;
  salary_type?: string;
  work_mode?: string;
  duration?: string;
  experience_required?: string;

  // For frontend display compatibility
  company?: string;
  role?: string;
  fitScore?: number;
}

// Helper to get job ID (handles both id and _id from MongoDB)
export function getJobId(job: Job): string {
  return job.id || job._id || '';
}

// Application Types
export type ApplicationStatus = 'prepared' | 'applied' | 'interview' | 'offer' | 'rejected';

export interface Application {
  id: string;
  jobId: string;
  job: Job;
  resumeVersionId: string;
  status: ApplicationStatus;
  appliedAt?: string;
  preparedAt: string;
  notes?: string;
}

// Interview Types
export type InterviewStage = 'phone_screen' | 'technical' | 'behavioral' | 'onsite' | 'final';

export interface Interview {
  id: string;
  applicationId: string;
  application: Application;
  stage: InterviewStage;
  scheduledAt: string;
  duration: number; // minutes
  interviewerName?: string;
  notes: string;
  meetingLink?: string;
}

// Resume Types
export interface TailoredResume {
  id: string;
  jobId: string;
  content: string;
  highlightedKeywords: string[];
  matchScore: number;
  createdAt: string;
  isApproved: boolean;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// Onboarding Types
export interface OnboardingState {
  currentStep: number;
  resumeUploaded: boolean;
  resumeStructureSet: boolean;
  preferencesSet: boolean;
  isComplete: boolean;
}
