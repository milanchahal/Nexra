// lib/api.ts
// This file is the central point for all frontend API communications.
// It uses a fetch-based client with an interceptor to handle JWT authentication.

import { type Job, type Profile } from "@/types"; // Add other types as needed

const PROD_API_URL = "https://nexerabackend.onrender.com/api";
const LOCAL_API_URL = "http://localhost:8000/api";

// Dynamic API URL determination
let activeApiUrl = import.meta.env.VITE_API_URL || PROD_API_URL;
let isUrlChecked = false;

// Function to check which API is matching
const determineBestApiUrl = async () => {
  if (isUrlChecked) return;

  try {
    // Try localhost first with a short timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);

    // Attempt to hit a lightweight endpoint (e.g., docs or root) to check availability
    // Using simple fetch to localhost root to see if it's alive
    try {
      await fetch("http://localhost:8000/docs", {
        method: "HEAD",
        signal: controller.signal,
        mode: 'no-cors' // Just checking connectivity
      });
      console.log("🚀 Connected to Local API");
      activeApiUrl = LOCAL_API_URL;
    } catch (e) {
      console.log("🌍 defaulting to Production API (Locahost not found)");
      activeApiUrl = PROD_API_URL;
    } finally {
      clearTimeout(timeoutId);
      isUrlChecked = true;
    }
  } catch (e) {
    // Fallback to prod
    activeApiUrl = PROD_API_URL;
    isUrlChecked = true;
  }
};

// Initialize check immediately
determineBestApiUrl();

// --- API Client with Auth Interceptor ---

// A simple in-memory store for the JWT token.
// Avoids using localStorage for the access token to mitigate XSS risks.
let token: string | null = null;

export const setAuthToken = (newToken: string | null) => {
  token = newToken;
};

export const getAuthToken = () => token;

// The core fetch function that all API calls will use.
async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Ensure we've at least tried to check the URL once if it's still default
  if (!isUrlChecked) {
    await determineBestApiUrl();
  }

  const headers = new Headers(options.headers || {});
  headers.append("Content-Type", "application/json");

  // Attach the JWT if it exists
  if (token) {
    headers.append("Authorization", `Bearer ${token}`);
  }

  let finalUrl = `${activeApiUrl}${endpoint}`;

  try {
    const response = await fetch(finalUrl, {
      ...options,
      headers,
    });

    if (!response.ok) {
      // Handle HTTP errors
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    if (response.status === 204) { // No Content
      return null as T;
    }

    return response.json();
  } catch (error: any) {
    // If request failed and we were using local, switch to prod and retry ONCE
    if (activeApiUrl === LOCAL_API_URL && (error.message.includes('Failed to fetch') || error.name === 'TypeError')) {
      console.warn("⚠️ Local API failed, switching to Production and retrying...");
      activeApiUrl = PROD_API_URL;
      finalUrl = `${activeApiUrl}${endpoint}`;

      const retryResponse = await fetch(finalUrl, {
        ...options,
        headers,
      });

      if (!retryResponse.ok) {
        const errorData = await retryResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed with status ${retryResponse.status}`);
      }
      return retryResponse.json();
    }
    throw error;
  }
}

// --- API Service Definitions ---

export const authApi = {
  login: async (email: string, password: string): Promise<any> => {
    // Ensure URL is checked
    if (!isUrlChecked) await determineBestApiUrl();

    // Use URLSearchParams for application/x-www-form-urlencoded (required by OAuth2PasswordRequestForm)
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2PasswordRequestForm expects 'username'
    formData.append('password', password);

    const response = await fetch(`${activeApiUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return { success: false, message: errorData.detail || 'Login failed' };
    }

    const data = await response.json();
    // Store token for future API calls
    setAuthToken(data.access_token);
    // Also store in localStorage for persistence
    localStorage.setItem('auth_token', data.access_token);

    return {
      success: true,
      data: {
        token: data.access_token,
        user: { email, name: email.split('@')[0], isOnboarded: false }
      }
    };
  },

  signup: async (email: string, password: string, name?: string): Promise<any> => {
    if (!isUrlChecked) await determineBestApiUrl();

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${activeApiUrl}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return { success: false, message: errorData.detail || 'Signup failed' };
    }

    // After signup, also login to get the token
    return authApi.login(email, password);
  },

  getCurrentUser: async (): Promise<any> => {
    // If no token, user is not logged in
    if (!getAuthToken()) {
      return { success: false };
    }

    // For now, just return success if token exists
    // A full implementation would call /auth/me endpoint
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      return { success: true, data: JSON.parse(storedUser) };
    }

    return { success: false };
  },

  logout: async (): Promise<void> => {
    setAuthToken(null);
    // No backend call needed for stateless JWT
  },
};

export const jobsApi = {
  getJobs: (): Promise<Job[]> => {
    return apiClient<Job[]>("/jobs", { method: "GET" });
  },
  markAsArchived: (jobId: string): Promise<Job> => {
    return apiClient<Job>(`/jobs/${jobId}/mark-archived`, { method: "POST" });
  },
  markAsApplied: (jobId: string): Promise<Job> => {
    return apiClient<Job>(`/jobs/${jobId}/mark-applied`, { method: "POST" });
  },
  optimizeResume: (jobId: string): Promise<any> => {
    return apiClient(`/jobs/${jobId}/optimize`, { method: "POST" });
  },
  improveResume: (jobId: string, custom_instructions: string): Promise<any> => {
    return apiClient(`/jobs/${jobId}/improve-resume`, {
      method: "POST",
      body: JSON.stringify({ custom_instructions }),
    });
  },
  getOptimizedResume: (resumeId: string): Promise<any> => {
    return apiClient(`/resumes/${resumeId}`, { method: "GET" });
  },
  triggerPrepare: (jobId: string): Promise<Job> => {
    return apiClient<Job>(`/jobs/${jobId}/prepare`, { method: "POST" });
  },
  seedDemoJobs: (): Promise<{ message: string; total_demo_jobs: number }> => {
    return apiClient(`/jobs/seed-demo`, { method: "POST" });
  },
  updateJobStatus: (jobId: string, status: string): Promise<Job> => {
    return apiClient<Job>(`/jobs/${jobId}/status`, {
      method: "PUT",
      body: JSON.stringify({ status })
    });
  },
};

export const automationApi = {
  launchApply: async (jobId: string): Promise<{ message: string; url: string }> => {
    return apiClient(`/automation/launch-apply/${jobId}`, { method: "POST" });
  },
};

export const profileApi = {
  getProfile: (): Promise<Profile> => {
    return apiClient<Profile>("/profiles/me", { method: "GET" });
  },
  uploadResume: async (file: File): Promise<{ success: boolean; data?: any; message?: string }> => {
    if (!isUrlChecked) await determineBestApiUrl();

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${activeApiUrl}/profiles/resume`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return { success: false, message: errorData.detail || 'Upload failed' };
      }

      const data = await response.json();
      return {
        success: true,
        data: {
          ...data,
          skills: data.skills || [],
        }
      };
    } catch (error) {
      return { success: false, message: 'Network error during upload' };
    }
  },
  buildProfile: (preferences: any, resumeStructure: string): Promise<any> => {
    return apiClient("/profiles/build", {
      method: "POST",
      body: JSON.stringify({ preferences, resumeStructure })
    });
  },
  triggerDiscovery: (): Promise<{ success: boolean; message: string }> => {
    return apiClient("/profiles/trigger-discovery", { method: "POST" });
  },
};

export const applicationsApi = {
  getApplications: (): Promise<any> => {
    // Ideally this would be a specific endpoint, but for now filtering jobs filtering
    return apiClient<Job[]>("/jobs?status=applied", { method: "GET" }).then(jobs => ({ data: jobs }));
  },
};

export const interviewsApi = {
  getInterviews: (): Promise<any> => {
    // Placeholder for interviews endpoint
    return Promise.resolve({ data: [] });
  }
};

export interface UserSettings {
  emailNotifications: boolean;
  jobDiscoveryEnabled: boolean;
  autoResumeGeneration: boolean;
  autofillEnabled: boolean;
}

export const settingsApi = {
  getSettings: (): Promise<{ data: UserSettings }> => {
    // Placeholder default settings
    return Promise.resolve({
      data: {
        emailNotifications: true,
        jobDiscoveryEnabled: true,
        autoResumeGeneration: false,
        autofillEnabled: false
      }
    });
  },
  updateSettings: (settings: UserSettings): Promise<any> => {
    console.log("Saving settings", settings);
    return Promise.resolve({ success: true });
  }
};

// ATS Resume Optimization API - Jobright Style
export interface ATSScoreResponse {
  overall_score: number;
  skills_match: { score: number; matched_skills: string[]; missing_skills: string[] };
  experience_relevance: { score: number; relevant_experience: string[]; gaps: string[] };
  keyword_optimization: { score: number; matched_keywords: string[]; missing_keywords: string[] };
  format_score: number;
  education_match: number;
  recommendations: string[];
  strengths: string[];
}

export interface ReplacementItem {
  original: string;
  replacement: string;
  context: string;
  reason: string;
  max_occurrences: number;
  approved: boolean;
}

export interface SuggestReplacementsResponse {
  job_id: string;
  job_title: string;
  company_name: string;
  current_score: number;
  keywords_found: string[];
  replacements: ReplacementItem[];
  total_suggestions: number;
  score_breakdown: {
    skills_match: number;
    keyword_optimization: number;
    experience_relevance: number;
  };
  recommendations: string[];
}

export interface PreviewDiffResponse {
  original_text: string;
  modified_text: string;
  changes_count: number;
  job_title: string;
}

export interface ApplyReplacementsResponse {
  success: boolean;
  optimized_resume_id: string;
  original_score: number;
  optimized_score: number;
  score_improvement: number;
  changes_applied: number;
  changes_made: string[];
  job_title: string;
  company_name: string;
  validation: {
    page_count_unchanged: boolean;
    links_preserved: boolean;
  };
}

export interface OptimizedResumeListItem {
  id: string;
  job_id: string;
  job_title: string;
  company_name: string;
  original_score: number;
  optimized_score: number;
  changes_count: number;
  created_at: string;
}

export const atsApi = {
  // Step 1: Get replacement suggestions
  suggestReplacements: (jobId: string): Promise<SuggestReplacementsResponse> => {
    return apiClient<SuggestReplacementsResponse>("/ats/suggest-replacements", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId })
    });
  },

  // Step 2: Preview text diff
  previewDiff: (jobId: string, replacements: ReplacementItem[]): Promise<PreviewDiffResponse> => {
    return apiClient<PreviewDiffResponse>("/ats/preview-diff", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, replacements })
    });
  },

  // Step 3: Apply approved replacements
  applyReplacements: (jobId: string, replacements: ReplacementItem[]): Promise<ApplyReplacementsResponse> => {
    return apiClient<ApplyReplacementsResponse>("/ats/apply-replacements", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId, replacements })
    });
  },

  // Calculate ATS score for a job
  calculateScore: (jobId: string): Promise<ATSScoreResponse> => {
    return apiClient<ATSScoreResponse>("/ats/score", {
      method: "POST",
      body: JSON.stringify({ job_id: jobId })
    });
  },

  // Get quick ATS score (cached)
  getJobScore: (jobId: string): Promise<{
    original_score: number;
    optimized_score?: number;
    has_optimized: boolean;
    optimized_resume_id?: string;
    changes_count?: number;
    recommendations?: string[];
  }> => {
    return apiClient(`/ats/job/${jobId}/score`, { method: "GET" });
  },

  // List all optimized resumes
  listOptimizedResumes: (): Promise<OptimizedResumeListItem[]> => {
    return apiClient<OptimizedResumeListItem[]>("/ats/optimized-resumes", { method: "GET" });
  },

  // Get specific optimized resume
  getOptimizedResume: (resumeId: string): Promise<{
    id: string;
    job_id: string;
    job_title: string;
    company_name: string;
    optimized_resume_text: string;
    original_score: number;
    optimized_score: number;
    changes_made: string[];
    replacements_applied: ReplacementItem[];
    created_at: string;
  }> => {
    return apiClient(`/ats/optimized-resumes/${resumeId}`, { method: "GET" });
  },

  // Download PDF - returns URL for download
  getDownloadUrl: (resumeId: string): string => {
    const token = getAuthToken();
    return `${activeApiUrl}/ats/optimized-resumes/${resumeId}/pdf${token ? `?token=${token}` : ''}`;
  },

  // Download PDF with fetch
  downloadPdf: async (resumeId: string): Promise<Blob> => {
    if (!isUrlChecked) await determineBestApiUrl();

    const headers: HeadersInit = {
      'Authorization': `Bearer ${getAuthToken()}`
    };

    const response = await fetch(`${activeApiUrl}/ats/optimized-resumes/${resumeId}/pdf`, {
      method: 'GET',
      headers
    });

    if (!response.ok) {
      throw new Error('Failed to download PDF');
    }

    return response.blob();
  }
};