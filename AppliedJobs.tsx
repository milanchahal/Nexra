// pages/AppliedJobs.tsx - Applied Jobs Page
// With Platform Source Badges
import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { jobsApi } from '@/lib/api';
import { Job, getJobId } from '@/types';
import { Loader2, MapPin, Building2, ExternalLink, CheckCircle2, Briefcase, TrendingUp } from 'lucide-react';
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

export default function AppliedJobs() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { toast } = useToast();

  const { data: jobs = [], isLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: jobsApi.getJobs,
  });

  // Filter applied jobs and sort by date/score
  const appliedJobs = jobs
    .filter(job => job.status === 'applied')
    .sort((a, b) => (b.match_score || 0) - (a.match_score || 0));

  const handleArchive = async (jobId: string) => {
    try {
      await jobsApi.markAsArchived(jobId);
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      toast({ title: 'Job archived' });
    } catch (error) {
      toast({ title: 'Error', variant: 'destructive' });
    }
  };

  const handleViewJob = (job: Job) => {
    navigate(`/dashboard/job/${getJobId(job)}`);
  };

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
            <Briefcase className="w-8 h-8 text-blue-500" />
            <h1 className="text-2xl font-bold">Applied Jobs</h1>
            <Badge variant="outline" className="bg-blue-500/20 text-blue-400">
              {appliedJobs.length} applied
            </Badge>
          </div>
          <p className="text-muted-foreground">Track your job applications</p>
        </div>

        {/* Empty State */}
        {appliedJobs.length === 0 && (
          <div className="text-center py-16 border border-dashed border-border rounded-xl">
            <Briefcase className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">No applications yet</h2>
            <p className="text-muted-foreground mb-4">Optimize your resume and apply to jobs!</p>
            <Button onClick={() => navigate('/dashboard/new-jobs')}>
              Find Jobs
            </Button>
          </div>
        )}

        {/* Applications List */}
        <div className="space-y-3">
          {appliedJobs.map(job => {
            const platformStyle = getPlatformStyle(job.source);
            const jobId = getJobId(job);
            
            return (
              <div
                key={jobId}
                className="bg-card border border-border rounded-xl p-4 hover:border-blue-500/30 transition-colors cursor-pointer"
                onClick={() => handleViewJob(job)}
              >
                <div className="flex items-center gap-4">
                  {/* Company Logo Placeholder */}
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold flex-shrink-0">
                    {job.company_name?.charAt(0) || 'C'}
                  </div>

                  {/* Job Info */}
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-foreground hover:text-blue-400 line-clamp-1">
                      {job.job_title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Building2 className="w-3 h-3" />
                        {job.company_name}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {job.location || 'Remote'}
                      </span>
                      {/* Platform Badge */}
                      <Badge className={`${platformStyle.bg} ${platformStyle.text} text-xs border-0`}>
                        {platformStyle.label}
                      </Badge>
                    </div>
                  </div>

                  {/* Badges */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> Applied
                    </span>
                    <span className={`px-2 py-1 rounded-lg text-xs font-bold flex items-center gap-1 ${
                      (job.match_score || 0) >= 80 ? 'bg-emerald-500/20 text-emerald-400' :
                      (job.match_score || 0) >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      <TrendingUp className="w-3 h-3" />
                      {job.match_score || 0}%
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 flex-shrink-0" onClick={e => e.stopPropagation()}>
                    {job.source_url && (
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => window.open(job.source_url, '_blank')}
                      >
                        <ExternalLink className="w-3 h-3 mr-1" /> Open
                      </Button>
                    )}
                    <Button 
                      size="sm" 
                      variant="ghost"
                      className="text-muted-foreground hover:text-red-400"
                      onClick={() => handleArchive(jobId)}
                    >
                      Archive
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </DashboardLayout>
  );
}
