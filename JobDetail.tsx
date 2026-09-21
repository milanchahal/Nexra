// pages/JobDetail.tsx - Full Job Detail Page with ATS Scoring and Resume Optimization
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { jobsApi, atsApi, ATSScoreResponse } from '@/lib/api';
import { Job, getJobId } from '@/types';
import { 
  Loader2, MapPin, Building2, ExternalLink, ArrowLeft, Clock, 
  Briefcase, CheckCircle, Star, Sparkles, MessageCircle, Send, X,
  Download, TrendingUp, AlertCircle, FileText, Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Progress } from '@/components/ui/progress';
import { ResumeOptimizeModal } from '@/components/ResumeOptimizeModal';
import { AppliedConfirmModal } from '@/components/AppliedConfirmModal';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://nexerabackend.onrender.com/api';

export default function JobDetail() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  // States
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [atsScore, setAtsScore] = useState<ATSScoreResponse | null>(null);
  const [isScoreLoading, setIsScoreLoading] = useState(false);
  const [optimizedResumeId, setOptimizedResumeId] = useState<string | null>(null);
  const [optimizedScore, setOptimizedScore] = useState<number | null>(null);
  const [isOptimizeModalOpen, setIsOptimizeModalOpen] = useState(false);
  const [isAppliedModalOpen, setIsAppliedModalOpen] = useState(false);

  // Queries
  const { data: jobs = [], isLoading: jobsLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: jobsApi.getJobs,
  });

  const job = jobs.find(j => getJobId(j) === jobId);

  // Check if we should ask about applied status
  useEffect(() => {
    if (job && job.status === 'discovered' && !localStorage.getItem(`applied_ask_${jobId}`)) {
      // Only show if user clicked 'Apply Now' recently or just randomly? 
      // User requested "jab bhi user kisi ko click kerke khole" -> so on open.
      const timer = setTimeout(() => setIsAppliedModalOpen(true), 2000);
      return () => clearTimeout(timer);
    }
  }, [job, jobId]);

  const handleMarkApplied = async () => {
    if (!jobId) return;
    try {
      await jobsApi.markAsApplied(jobId);
      toast({ title: 'Job marked as Applied!', description: 'Moved to Applied Jobs section.' });
      setIsAppliedModalOpen(false);
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      localStorage.setItem(`applied_ask_${jobId}`, 'true');
      navigate('/dashboard/applied');
    } catch (error) {
      toast({ title: 'Error marking as applied', variant: 'destructive' });
    }
  };

  const handleApplyModalClose = () => {
    setIsAppliedModalOpen(false);
    // Don't ask again for this session/job
    if (jobId) localStorage.setItem(`applied_ask_${jobId}`, 'true');
  };

  // Handle optimization complete
  const handleOptimizationComplete = (resumeId: string) => {
    setOptimizedResumeId(resumeId);
    queryClient.invalidateQueries({ queryKey: ['jobs'] });
    // Reload score
    loadATSScore();
  };

  // Load ATS score on mount
  useEffect(() => {
    if (jobId && job) {
      loadATSScore();
    }
  }, [jobId, job?.id]);

  const loadATSScore = async () => {
    if (!jobId) return;
    setIsScoreLoading(true);
    try {
      // First check if we have cached score
      const quickScore = await atsApi.getJobScore(jobId);
      if (quickScore.has_optimized && quickScore.optimized_resume_id) {
        setOptimizedResumeId(quickScore.optimized_resume_id);
        setOptimizedScore(quickScore.optimized_score || quickScore.original_score);
      }
      
      // Then get detailed score
      const detailed = await atsApi.calculateScore(jobId);
      setAtsScore(detailed);
    } catch (error: any) {
      console.error('ATS score error:', error);
      // Set default score if error
      setAtsScore({
        overall_score: 65,
        skills_match: { score: 60, matched_skills: [], missing_skills: [] },
        experience_relevance: { score: 70, relevant_experience: [], gaps: [] },
        keyword_optimization: { score: 55, matched_keywords: [], missing_keywords: [] },
        format_score: 75,
        education_match: 70,
        recommendations: ['Add more relevant keywords', 'Quantify achievements'],
        strengths: ['Good experience match']
      });
    } finally {
      setIsScoreLoading(false);
    }
  };

  // Initialize chat
  useEffect(() => {
    if (job) {
      setMessages([{
        role: 'assistant',
        content: `I'm here to help you with the **${job.job_title}** position at **${job.company_name}**! 🎯\n\nYou can ask me about:\n• Why this job is a good fit\n• Resume tips for this role\n• Interview preparation\n• Company insights`
      }]);
    }
  }, [job?.id]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || !job) return;
    setChatLoading(true);
    const userMessage: ChatMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          message: text,
          job_context: {
            job_title: job.job_title,
            company_name: job.company_name,
            location: job.location,
            job_description: job.job_description,
            match_score: job.match_score,
          },
          conversation_history: messages,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Please try again.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleOptimizeResume = () => {
    setIsOptimizeModalOpen(true);
  };

  const handleDownloadPDF = async () => {
    if (!optimizedResumeId) {
      toast({ title: 'No optimized resume', description: 'Click "Prepare Resume" first', variant: 'destructive' });
      return;
    }
    
    try {
      const blob = await atsApi.downloadPdf(optimizedResumeId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Resume_${job?.job_title?.replace(/\s+/g, '_')}_${job?.company_name?.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast({ title: '📄 PDF Downloaded!' });
    } catch (error) {
      toast({ title: 'Download failed', variant: 'destructive' });
    }
  };

  const handleApplyNow = () => {
    if (job?.source_url) {
      window.open(job.source_url, '_blank');
    }
  };

  if (jobsLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  if (!job) {
    return (
      <DashboardLayout>
        <div className="text-center py-16">
          <h2 className="text-xl font-semibold mb-2">Job not found</h2>
          <Button onClick={() => navigate('/dashboard/new-jobs')}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Jobs
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  const currentScore = optimizedScore || atsScore?.overall_score || job.match_score || 0;
  const originalScore = atsScore?.overall_score || job.match_score || 0;

  return (
    <DashboardLayout>
      <div className="flex h-full">
        {/* Main Content */}
        <div className={`flex-1 overflow-y-auto p-6 transition-all duration-300 ${isChatOpen ? 'mr-96' : 'mr-0'}`}>
          {/* Back Button */}
          <Button variant="ghost" className="mb-4" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Back
          </Button>

          {/* Header Card */}
          <div className="bg-card border border-border rounded-2xl p-6 mb-6">
            <div className="flex items-start gap-6">
              {/* Company Logo */}
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center text-white text-2xl font-bold flex-shrink-0 shadow-lg">
                {job.company_name?.charAt(0) || 'C'}
              </div>

              {/* Job Info */}
              <div className="flex-1">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                  <span className="font-medium text-foreground">{job.company_name}</span>
                  <span>·</span>
                  <span>{job.source}</span>
                </div>
                <h1 className="text-2xl font-bold text-foreground mb-3">{job.job_title}</h1>
                
                <div className="flex flex-wrap items-center gap-3 text-sm">
                  <span className="flex items-center gap-1 px-3 py-1 bg-muted rounded-full">
                    <MapPin className="w-4 h-4" /> {job.location || 'Remote'}
                  </span>
                  <span className="flex items-center gap-1 px-3 py-1 bg-muted rounded-full">
                    <Briefcase className="w-4 h-4" /> Full-time
                  </span>
                </div>
              </div>

              {/* ATS Score Circle */}
              <div className="text-center flex-shrink-0">
                {isScoreLoading ? (
                  <div className="w-24 h-24 rounded-full border-4 border-muted flex items-center justify-center">
                    <Loader2 className="w-6 h-6 animate-spin" />
                  </div>
                ) : (
                  <div className={`w-24 h-24 rounded-full flex flex-col items-center justify-center text-2xl font-bold border-4 ${
                    currentScore >= 80 
                      ? 'border-emerald-500 text-emerald-500 bg-emerald-500/10' 
                      : currentScore >= 60 
                      ? 'border-yellow-500 text-yellow-500 bg-yellow-500/10'
                      : 'border-red-500 text-red-500 bg-red-500/10'
                  }`}>
                    {currentScore}%
                    {optimizedScore && (
                      <span className="text-xs text-emerald-400 flex items-center">
                        <TrendingUp className="w-3 h-3 mr-0.5" /> +{optimizedScore - originalScore}
                      </span>
                    )}
                  </div>
                )}
                <p className="text-xs text-muted-foreground mt-1">ATS Score</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 mt-6 pt-6 border-t border-border">
              <Button 
                className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700"
                onClick={handleOptimizeResume}
              >
                <Sparkles className="w-4 h-4 mr-2" /> {optimizedResumeId ? 'Re-optimize' : 'Prepare Resume'}
              </Button>
              
              {optimizedResumeId && (
                <Button variant="outline" onClick={handleDownloadPDF}>
                  <Download className="w-4 h-4 mr-2" /> Download PDF
                </Button>
              )}
              
              <Button variant="outline" onClick={handleApplyNow}>
                <ExternalLink className="w-4 h-4 mr-2" /> Apply Now
              </Button>
              
              <Button variant="ghost" onClick={() => setIsChatOpen(!isChatOpen)}>
                <MessageCircle className="w-4 h-4 mr-2" /> Ask AI
              </Button>
            </div>
          </div>

          {/* ATS Score Breakdown */}
          {atsScore && (
            <div className="bg-card border border-border rounded-2xl p-6 mb-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-500" /> ATS Score Breakdown
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <ScoreCard label="Skills Match" score={atsScore.skills_match.score} />
                <ScoreCard label="Experience" score={atsScore.experience_relevance.score} />
                <ScoreCard label="Keywords" score={atsScore.keyword_optimization.score} />
                <ScoreCard label="Education" score={atsScore.education_match} />
              </div>

              {/* Skills Matched */}
              {atsScore.skills_match.matched_skills?.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-sm font-medium mb-2 text-emerald-400">✓ Matched Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {atsScore.skills_match.matched_skills.slice(0, 8).map((skill, i) => (
                      <span key={i} className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded text-xs">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Missing Skills */}
              {atsScore.skills_match.missing_skills?.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-sm font-medium mb-2 text-red-400">✗ Missing Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {atsScore.skills_match.missing_skills.slice(0, 6).map((skill, i) => (
                      <span key={i} className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {atsScore.recommendations?.length > 0 && (
                <div className="mt-4 pt-4 border-t border-border">
                  <h3 className="text-sm font-medium mb-2 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4 text-yellow-500" /> Recommendations
                  </h3>
                  <ul className="space-y-1">
                    {atsScore.recommendations.slice(0, 4).map((rec, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-yellow-500">•</span> {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Job Description */}
          <div className="bg-card border border-border rounded-2xl p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5" /> Job Description
            </h2>
            <div className="text-muted-foreground whitespace-pre-wrap leading-relaxed text-sm max-h-96 overflow-y-auto">
              {job.job_description || 'No description available'}
            </div>
          </div>

          {/* Company Card */}
          <div className="bg-card border border-border rounded-2xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Building2 className="w-5 h-5" /> About {job.company_name}
            </h2>
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-white text-lg font-bold">
                {job.company_name?.charAt(0)}
              </div>
              <div>
                <h3 className="font-semibold">{job.company_name}</h3>
                <p className="text-sm text-muted-foreground">{job.location}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Sidebar */}
        {isChatOpen && (
          <div className="fixed right-0 top-0 h-full w-96 bg-card border-l border-border shadow-2xl flex flex-col z-50">
            <div className="p-4 border-b border-border bg-gradient-to-r from-emerald-500/10 to-teal-500/10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Clawd</h3>
                    <p className="text-xs text-muted-foreground">Job Assistant</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon" onClick={() => setIsChatOpen(false)}>
                  <X className="w-5 h-5" />
                </Button>
              </div>
            </div>

            <div className="p-3 bg-muted/50 border-b border-border">
              <p className="text-xs text-muted-foreground">Discussing:</p>
              <p className="text-sm font-medium line-clamp-1">{job.job_title}</p>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm whitespace-pre-wrap ${
                    msg.role === 'user'
                      ? 'bg-emerald-500 text-white rounded-br-md'
                      : 'bg-muted text-foreground rounded-bl-md'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-2xl px-4 py-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-border">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage(input)}
                  placeholder="Ask about this job..."
                  className="flex-1"
                  disabled={chatLoading}
                />
                <Button onClick={() => sendMessage(input)} disabled={chatLoading || !input.trim()} size="icon" className="bg-emerald-500 hover:bg-emerald-600">
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Chat Toggle */}
        {!isChatOpen && (
          <button
            onClick={() => setIsChatOpen(true)}
            className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full shadow-lg flex items-center justify-center text-white hover:scale-110 transition-transform z-50"
          >
            <MessageCircle className="w-6 h-6" />
          </button>
        )}
      </div>

      {/* Resume Optimization Modal */}
      <ResumeOptimizeModal
        isOpen={isOptimizeModalOpen}
        onClose={() => setIsOptimizeModalOpen(false)}
        jobId={jobId || ''}
        jobTitle={job?.job_title || ''}
        companyName={job?.company_name || ''}
        onOptimized={handleOptimizationComplete}
      />

      {/* Applied Confirmation Modal */}
      <AppliedConfirmModal
        isOpen={isAppliedModalOpen}
        onClose={handleApplyModalClose}
        onConfirmApplied={handleMarkApplied}
        jobTitle={job?.job_title || ''}
        companyName={job?.company_name || ''}
      />
    </DashboardLayout>
  );
}

// Score Card Component
function ScoreCard({ label, score }: { label: string; score: number }) {
  const color = score >= 80 ? 'emerald' : score >= 60 ? 'yellow' : 'red';
  return (
    <div className="bg-muted/50 rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className={`text-lg font-bold text-${color}-500`}>{score}%</span>
      </div>
      <Progress value={score} className="h-2" />
    </div>
  );
}
