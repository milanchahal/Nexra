// pages/ResumeReady.tsx - Shows jobs with prepared/optimized resumes
// With Platform Source Badges and ATS Score Display
import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { jobsApi, atsApi, OptimizedResumeListItem } from '@/lib/api';
import { Job, getJobId } from '@/types';
import { 
  Loader2, FileText, Download, Eye, TrendingUp, 
  CheckCircle, ExternalLink, Sparkles, MapPin
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';

// Platform source colors - All 47+ platforms
const PLATFORM_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  // Traditional Job Boards
  'naukri': { bg: 'bg-purple-500/20', text: 'text-purple-400', label: 'Naukri' },
  'instahyre': { bg: 'bg-orange-500/20', text: 'text-orange-400', label: 'Instahyre' },
  'glassdoor': { bg: 'bg-green-500/20', text: 'text-green-400', label: 'Glassdoor' },
  'wellfound': { bg: 'bg-pink-500/20', text: 'text-pink-400', label: 'Wellfound' },
  // Remote Job Platforms (47 platforms)
  'remoteok': { bg: 'bg-red-500/20', text: 'text-red-400', label: 'RemoteOK' },
  'remotive': { bg: 'bg-cyan-500/20', text: 'text-cyan-400', label: 'Remotive' },
  'workingnomads': { bg: 'bg-amber-500/20', text: 'text-amber-400', label: 'Working Nomads' },
  'himalayas': { bg: 'bg-sky-500/20', text: 'text-sky-400', label: 'Himalayas' },
  'arcdev': { bg: 'bg-violet-500/20', text: 'text-violet-400', label: 'Arc.dev' },
  'weworkremotely': { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'We Work Remotely' },
  'flexjobs': { bg: 'bg-lime-500/20', text: 'text-lime-400', label: 'FlexJobs' },
  'jobspresso': { bg: 'bg-rose-500/20', text: 'text-rose-400', label: 'Jobspresso' },
  'justremote': { bg: 'bg-fuchsia-500/20', text: 'text-fuchsia-400', label: 'JustRemote' },
  'jsremotely': { bg: 'bg-yellow-400/20', text: 'text-yellow-300', label: 'JS Remotely' },
  'hubstaff': { bg: 'bg-emerald-500/20', text: 'text-emerald-400', label: 'Hubstaff' },
  'nodesk': { bg: 'bg-teal-500/20', text: 'text-teal-400', label: 'Nodesk' },
  'authenticjobs': { bg: 'bg-orange-400/20', text: 'text-orange-300', label: 'AuthenticJobs' },
  'landingjobs': { bg: 'bg-blue-400/20', text: 'text-blue-300', label: 'Landing.jobs' },
  'turing': { bg: 'bg-indigo-400/20', text: 'text-indigo-300', label: 'Turing' },
  'pangian': { bg: 'bg-purple-400/20', text: 'text-purple-300', label: 'Pangian' },
  'powertofly': { bg: 'bg-pink-400/20', text: 'text-pink-300', label: 'PowerToFly' },
  'remote100k': { bg: 'bg-green-400/20', text: 'text-green-300', label: 'Remote100K' },
  'levelsfyi': { bg: 'bg-cyan-400/20', text: 'text-cyan-300', label: 'Levels.fyi' },
  'workatastartup': { bg: 'bg-orange-600/20', text: 'text-orange-400', label: 'YC Startups' },
  '4dayweek': { bg: 'bg-lime-400/20', text: 'text-lime-300', label: '4 Day Week' },
  'skipthedrive': { bg: 'bg-sky-400/20', text: 'text-sky-300', label: 'SkipTheDrive' },
  'vanhack': { bg: 'bg-red-400/20', text: 'text-red-300', label: 'VanHack' },
  'snaphunt': { bg: 'bg-violet-400/20', text: 'text-violet-300', label: 'SnapHunt' },
  'totaljobs': { bg: 'bg-blue-600/20', text: 'text-blue-400', label: 'TotalJobs' },
  'gunio': { bg: 'bg-slate-500/20', text: 'text-slate-300', label: 'Gun.io' },
  'hired': { bg: 'bg-amber-400/20', text: 'text-amber-300', label: 'Hired' },
  'soshace': { bg: 'bg-rose-400/20', text: 'text-rose-300', label: 'Soshace' },
  'strider': { bg: 'bg-emerald-400/20', text: 'text-emerald-300', label: 'Strider' },
  'tecla': { bg: 'bg-fuchsia-400/20', text: 'text-fuchsia-300', label: 'Tecla' },
  'beontech': { bg: 'bg-teal-400/20', text: 'text-teal-300', label: 'Beon.Tech' },
  'flatworld': { bg: 'bg-indigo-600/20', text: 'text-indigo-400', label: 'Flatworld' },
  'geekhunter': { bg: 'bg-green-600/20', text: 'text-green-400', label: 'GeekHunter' },
  'idealist': { bg: 'bg-purple-600/20', text: 'text-purple-400', label: 'Idealist' },
  'kula': { bg: 'bg-cyan-600/20', text: 'text-cyan-400', label: 'Kula' },
  'loka': { bg: 'bg-pink-600/20', text: 'text-pink-400', label: 'Loka' },
  'nixa': { bg: 'bg-orange-500/20', text: 'text-orange-400', label: 'Nixa' },
  'programathor': { bg: 'bg-yellow-600/20', text: 'text-yellow-400', label: 'Programathor' },
  'remotecom': { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Remote.com' },
  'remoteyeah': { bg: 'bg-red-600/20', text: 'text-red-400', label: 'RemoteYeah' },
  'revelo': { bg: 'bg-violet-600/20', text: 'text-violet-400', label: 'Revelo' },
  'seujob': { bg: 'bg-lime-600/20', text: 'text-lime-400', label: 'SeuJob' },
  'coodesh': { bg: 'bg-amber-600/20', text: 'text-amber-400', label: 'Coodesh' },
  'impulso': { bg: 'bg-sky-600/20', text: 'text-sky-400', label: 'Impulso' },
  'insquad': { bg: 'bg-rose-600/20', text: 'text-rose-400', label: 'Insquad' },
  'distro': { bg: 'bg-slate-600/20', text: 'text-slate-400', label: 'Distro' },
  // Other sources
  'company': { bg: 'bg-emerald-500/20', text: 'text-emerald-400', label: 'Company' },
  'career_page': { bg: 'bg-teal-500/20', text: 'text-teal-400', label: 'Career Page' },
  'github': { bg: 'bg-gray-500/20', text: 'text-gray-300', label: 'GitHub' },
  'jobright': { bg: 'bg-blue-500/20', text: 'text-blue-400', label: 'Jobright' },
  'jobspy': { bg: 'bg-purple-500/20', text: 'text-purple-400', label: 'JobSpy' },
  'internshala': { bg: 'bg-cyan-500/20', text: 'text-cyan-400', label: 'Internshala' },
  'default': { bg: 'bg-gray-500/20', text: 'text-gray-400', label: 'Job Board' }
};

function getPlatformStyle(source: string | undefined) {
  if (!source) return PLATFORM_STYLES.default;
  const key = source.toLowerCase().replace(/[^a-z]/g, '');
  for (const [platform, style] of Object.entries(PLATFORM_STYLES)) {
    if (key.includes(platform)) return { ...style, label: style.label };
  }
  return { ...PLATFORM_STYLES.default, label: source };
}

export default function ResumeReady() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  // Get jobs that are resume_ready
  const { data: jobs = [], isLoading: jobsLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: jobsApi.getJobs,
  });

  // Get all optimized resumes
  const { data: optimizedResumes = [], isLoading: resumesLoading } = useQuery<OptimizedResumeListItem[]>({
    queryKey: ['optimized-resumes'],
    queryFn: atsApi.listOptimizedResumes,
  });

  // Filter resume ready jobs and sort by optimized score
  const readyJobs = jobs
    .filter(job => job.status === 'resume_ready')
    .sort((a, b) => (b.match_score || 0) - (a.match_score || 0));

  // Match jobs with their optimized resumes
  const jobsWithResumes = readyJobs.map(job => {
    const resume = optimizedResumes.find(r => r.job_id === getJobId(job) || r.job_id === (job as any)._id);
    return { job, resume };
  }).sort((a, b) => {
    const scoreA = a.resume?.optimized_score || a.job.match_score || 0;
    const scoreB = b.resume?.optimized_score || b.job.match_score || 0;
    return scoreB - scoreA;
  });

  const handleDownloadPDF = async (resumeId: string, jobTitle: string, companyName: string) => {
    setDownloadingId(resumeId);
    try {
      const blob = await atsApi.downloadPdf(resumeId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Resume_${jobTitle.replace(/\s+/g, '_')}_${companyName.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast({ title: '📄 PDF Downloaded!' });
    } catch (error) {
      toast({ title: 'Download failed', variant: 'destructive' });
    } finally {
      setDownloadingId(null);
    }
  };

  const handleViewJob = (job: Job) => {
    navigate(`/dashboard/job/${getJobId(job)}`);
  };

  const handleApply = async (job: Job) => {
    if (job.source_url) {
      window.open(job.source_url, '_blank');
      // Mark as applied
      try {
        await jobsApi.markAsApplied(getJobId(job));
        queryClient.invalidateQueries({ queryKey: ['jobs'] });
        toast({ title: '🎉 Good luck with your application!' });
      } catch (error) {
        // Ignore errors
      }
    }
  };

  const isLoading = jobsLoading || resumesLoading;

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div>
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="w-8 h-8 text-emerald-500" />
            <h1 className="text-2xl font-bold">Resume Ready</h1>
            <Badge variant="outline" className="bg-emerald-500/20 text-emerald-400">
              {readyJobs.length} ready
            </Badge>
          </div>
          <p className="text-muted-foreground">Sorted by optimized ATS score • Download and apply!</p>
        </div>

        {/* Empty State */}
        {jobsWithResumes.length === 0 && (
          <div className="text-center py-16 border border-dashed border-border rounded-xl">
            <FileText className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">No optimized resumes yet</h2>
            <p className="text-muted-foreground mb-4">Go to New Jobs and click "Optimize Resume" to prepare your resume for a job</p>
            <Button onClick={() => navigate('/dashboard/new-jobs')}>
              <Sparkles className="w-4 h-4 mr-2" /> Find Jobs
            </Button>
          </div>
        )}

        {/* Jobs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {jobsWithResumes.map(({ job, resume }, index) => {
            const platformStyle = getPlatformStyle(job.source);
            
            return (
              <div
                key={getJobId(job)}
                className="bg-card border border-emerald-500/30 rounded-xl p-5 hover:border-emerald-500/60 transition-all relative"
              >
                {/* Rank Badge */}
                {index < 3 && (
                  <div className={`absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    index === 0 ? 'bg-yellow-500 text-black' :
                    index === 1 ? 'bg-gray-400 text-black' :
                    'bg-orange-700 text-white'
                  }`}>
                    {index + 1}
                  </div>
                )}

                {/* Header */}
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center text-white text-xl font-bold flex-shrink-0">
                    {job.company_name?.charAt(0) || 'C'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-lg text-foreground line-clamp-1">{job.job_title}</h3>
                    <p className="text-muted-foreground">{job.company_name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm text-muted-foreground flex items-center gap-1">
                        <MapPin className="w-3 h-3" /> {job.location || 'Remote'}
                      </span>
                      {/* Platform Badge */}
                      <Badge className={`${platformStyle.bg} ${platformStyle.text} text-xs border-0`}>
                        {platformStyle.label}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right">
                    {resume && (
                      <div className="flex items-center gap-1 text-emerald-400 text-sm">
                        <TrendingUp className="w-4 h-4" />
                        <span className="font-bold text-lg">{resume.optimized_score}%</span>
                      </div>
                    )}
                    <span className="text-xs text-muted-foreground">
                      {resume ? `+${resume.optimized_score - resume.original_score}% boost` : 'ATS Score'}
                    </span>
                  </div>
                </div>

                {/* Score Comparison */}
                {resume && (
                  <div className="bg-muted/50 rounded-lg p-3 mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Original Score</span>
                      <span className="text-red-400">{resume.original_score}%</span>
                    </div>
                    <div className="flex items-center justify-between text-sm mt-1">
                      <span className="text-muted-foreground">Optimized Score</span>
                      <span className="text-emerald-400 font-bold">{resume.optimized_score}%</span>
                    </div>
                    <div className="flex items-center gap-2 mt-2 pt-2 border-t border-border">
                      <CheckCircle className="w-4 h-4 text-emerald-500" />
                      <span className="text-xs text-emerald-400">Resume optimized • {resume.changes_count} improvements made</span>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2">
                  {resume && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      className="flex-1"
                      onClick={() => handleDownloadPDF(resume.id, job.job_title || '', job.company_name || '')}
                      disabled={downloadingId === resume.id}
                    >
                      {downloadingId === resume.id ? (
                        <><Loader2 className="w-4 h-4 mr-1 animate-spin" /> Downloading...</>
                      ) : (
                        <><Download className="w-4 h-4 mr-1" /> Download PDF</>
                      )}
                    </Button>
                  )}
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={() => handleViewJob(job)}
                  >
                    <Eye className="w-4 h-4 mr-1" /> View
                  </Button>
                  <Button 
                    size="sm" 
                    className="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700"
                    onClick={() => handleApply(job)}
                  >
                    <ExternalLink className="w-4 h-4 mr-1" /> Apply Now
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </DashboardLayout>
  );
}
