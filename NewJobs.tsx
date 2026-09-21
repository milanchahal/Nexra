// pages/NewJobs.tsx - New Jobs / Discovered Jobs Page
// With ATS Score Sorting, Platform Source Badges, and Advanced Filters
import { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { jobsApi, profileApi } from '@/lib/api';
import { Job, getJobId } from '@/types';
import { 
  Loader2, Zap, MapPin, Building2, ExternalLink, Bot, Sparkles, 
  Eye, TrendingUp, ArrowDownWideNarrow, Filter, DollarSign, Clock, Briefcase
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { useToast } from '@/hooks/use-toast';

// Platform source colors and icons - All 47+ platforms
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
  
  // Internship Platforms (Indian Students)
  'internshala': { bg: 'bg-cyan-500/20', text: 'text-cyan-400', label: '🎓 Internshala' },
  'unstop': { bg: 'bg-orange-500/20', text: 'text-orange-400', label: '🎓 Unstop' },
  'linkedin_intern': { bg: 'bg-blue-600/20', text: 'text-blue-400', label: '🎓 LinkedIn' },
  'indeed_intern': { bg: 'bg-purple-600/20', text: 'text-purple-400', label: '🎓 Indeed' },
  'naukri_intern': { bg: 'bg-emerald-600/20', text: 'text-emerald-400', label: '🎓 Naukri' },
  'glassdoor_intern': { bg: 'bg-green-600/20', text: 'text-green-400', label: '🎓 Glassdoor' },
  'remoteok_intern': { bg: 'bg-red-600/20', text: 'text-red-400', label: '🎓 RemoteOK' },
  'remotive_intern': { bg: 'bg-cyan-600/20', text: 'text-cyan-400', label: '🎓 Remotive' },
  
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

// Utility to format salary
const formatSalary = (min?: number, max?: number, type?: string) => {
  if (!min && !max) return 'Not Disclosed';
  
  const formatNum = (num: number) => {
    if (num >= 10000000) return `₹${(num/10000000).toFixed(1)}Cr`;
    if (num >= 100000) return `₹${(num/100000).toFixed(1)}L`;
    if (num >= 1000) return `₹${(num/1000).toFixed(0)}k`;
    return `₹${num}`;
  };

  const period = type === 'monthly' ? '/mo' : type === 'hourly' ? '/hr' : '/yr';
  
  if (min && max) return `${formatNum(min)} - ${formatNum(max)}${period}`;
  if (min) return `${formatNum(min)}${period}`;
  return `${formatNum(max!)}${period}`;
};

export default function NewJobs() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isDiscovering, setIsDiscovering] = useState(false);
  
  // Filters state
  const [sortBy, setSortBy] = useState<'score' | 'date' | 'salary'>('score');
  const [locationFilter, setLocationFilter] = useState<string>('all');
  const [modeFilter, setModeFilter] = useState<string>('all'); // all, remote, onsite, hybrid
  const [salaryFilter, setSalaryFilter] = useState<number>(0); // Min salary filter

  const { data: jobs = [], isLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: jobsApi.getJobs,
    refetchInterval: 30000,
  });

  // Extract unique locations for filter
  const uniqueLocations = useMemo(() => {
    const locs = new Set<string>();
    jobs.forEach(job => {
      if (job.location && job.location !== 'Remote') {
        // Normalize: take first part if comma separated
        const city = job.location.split(',')[0].trim();
        locs.add(city);
      }
    });
    return Array.from(locs).sort();
  }, [jobs]);

  // Filter and Sort Jobs
  const filteredJobs = useMemo(() => {
    let filtered = jobs.filter(job => job.status === 'discovered');

    // Location Filter
    if (locationFilter !== 'all') {
      if (locationFilter === 'remote') {
        filtered = filtered.filter(job => 
          job.location?.toLowerCase().includes('remote') || 
          job.work_mode === 'remote'
        );
      } else {
        filtered = filtered.filter(job => 
          job.location?.toLowerCase().includes(locationFilter.toLowerCase())
        );
      }
    }

    // Work Mode Filter
    if (modeFilter !== 'all') {
      filtered = filtered.filter(job => 
        job.work_mode === modeFilter || 
        (modeFilter === 'remote' && job.location?.toLowerCase().includes('remote'))
      );
    }

    // Salary Filter
    if (salaryFilter > 0) {
      filtered = filtered.filter(job => {
        const salary = job.salary_max || job.salary_min || 0;
        // Normalize monthly to yearly for filtering if needed? assuming filter is in LPA or similar
        // For now assume filter is raw number. If user selects 5LPA => 500000
        return salary >= salaryFilter;
      });
    }

    // Sorting
    return filtered.sort((a, b) => {
      if (sortBy === 'score') {
        return (b.match_score || 0) - (a.match_score || 0);
      }
      if (sortBy === 'salary') {
        const salA = a.salary_max || a.salary_min || 0;
        const salB = b.salary_max || b.salary_min || 0;
        return salB - salA;
      }
      // Date sorting (newest first)
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    });
  }, [jobs, locationFilter, modeFilter, salaryFilter, sortBy]);

  const handleTriggerDiscovery = async () => {
    setIsDiscovering(true);
    try {
      await profileApi.triggerDiscovery();
      toast({ title: '🤖 Clawd.bot Activated!', description: 'Searching for jobs across platforms...' });
      setTimeout(() => queryClient.invalidateQueries({ queryKey: ['jobs'] }), 5000);
    } catch (error) {
      toast({ title: 'Discovery Failed', variant: 'destructive' });
    } finally {
      setIsDiscovering(false);
    }
  };

  const handlePrepareResume = async (jobId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigate(`/dashboard/job/${jobId}`);
  };

  const handleIgnore = async (jobId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await jobsApi.markAsArchived(jobId);
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      toast({ title: 'Job archived' });
    } catch (error) {
      toast({ title: 'Error', variant: 'destructive' });
    }
  };

  const handleViewJob = (job: Job) => {
    const id = getJobId(job);
    navigate(`/dashboard/job/${id}`);
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
      <div className="space-y-6">
        {/* Header & Controls */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              New Jobs
              <Badge variant="outline" className="text-xs font-normal">
                {filteredJobs.length} found
              </Badge>
            </h1>
            <p className="text-muted-foreground">AI-curated opportunities matching your profile</p>
          </div>
          
          <Button onClick={handleTriggerDiscovery} disabled={isDiscovering} className="bg-gradient-to-r from-emerald-500 to-teal-600">
            {isDiscovering ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Zap className="w-4 h-4 mr-2" />}
            Find New Jobs
          </Button>
        </div>

        {/* Filters Toolbar - Professional Look */}
        <div className="p-4 bg-card border border-border rounded-xl shadow-sm space-y-4 md:space-y-0 md:flex md:items-center md:gap-4 md:flex-wrap">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mr-2">
            <Filter className="w-4 h-4" /> Filters:
          </div>

          <Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Sort By" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="score">Sort by Match Score</SelectItem>
              <SelectItem value="date">Sort by Date</SelectItem>
              <SelectItem value="salary">Sort by Salary (High-Low)</SelectItem>
            </SelectContent>
          </Select>

          <Select value={locationFilter} onValueChange={setLocationFilter}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Location" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Locations</SelectItem>
              <SelectItem value="remote">Remote Only</SelectItem>
              {uniqueLocations.map(loc => (
                <SelectItem key={loc} value={loc}>{loc}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={modeFilter} onValueChange={setModeFilter}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Work Mode" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Any Mode</SelectItem>
              <SelectItem value="remote">Remote</SelectItem>
              <SelectItem value="hybrid">Hybrid</SelectItem>
              <SelectItem value="onsite">On-site</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Empty State */}
        {filteredJobs.length === 0 && (
          <div className="text-center py-16 border border-dashed border-border rounded-xl">
            <Bot className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">No jobs found</h2>
            <p className="text-muted-foreground mb-4">Try adjusting your filters or click "Find New Jobs"</p>
          </div>
        )}

        {/* Jobs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredJobs.map((job, index) => {
            const jobId = getJobId(job);
            const platformStyle = getPlatformStyle(job.source);
            const score = job.match_score || 0;
            const salaryText = formatSalary(job.salary_min, job.salary_max, job.salary_type);
            
            return (
              <div
                key={jobId}
                className="bg-card border border-border rounded-xl p-4 hover:border-emerald-500/50 transition-all cursor-pointer group hover:shadow-lg relative flex flex-col h-full"
                onClick={() => handleViewJob(job)}
              >
                {/* Ranking Badge */}
                {index < 3 && sortBy === 'score' && (
                  <div className={`absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shadow-sm z-10 ${
                    index === 0 ? 'bg-amber-400 text-black' :
                    index === 1 ? 'bg-slate-300 text-black' :
                    'bg-orange-700 text-white'
                  }`}>
                    {index + 1}
                  </div>
                )}

                {/* Top Section */}
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0 shadow-sm">
                    {job.company_name?.charAt(0) || 'C'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-foreground group-hover:text-emerald-400 transition-colors line-clamp-1" title={job.job_title}>
                      {job.job_title}
                    </h3>
                    <p className="text-sm text-muted-foreground line-clamp-1">{job.company_name}</p>
                  </div>
                </div>

                {/* Metadata Tags */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary" className={`bg-opacity-20 ${
                      score >= 80 ? 'bg-emerald-500 text-emerald-500' :
                      score >= 60 ? 'bg-yellow-500 text-yellow-500' :
                      'bg-red-500 text-red-500'
                    }`}>
                      {score}% Match
                    </Badge>
                    <Badge variant="outline" className={`${platformStyle.bg} ${platformStyle.text} border-0`}>
                      {platformStyle.label}
                    </Badge>
                  </div>

                  {/* Info Grid */}
                  <div className="grid grid-cols-2 gap-y-2 text-xs text-muted-foreground mt-2">
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-emerald-500/70" />
                      <span className="truncate">{job.location || 'Remote'}</span>
                    </div>
                    {salaryText !== 'Not Disclosed' && (
                      <div className="flex items-center gap-1.5">
                        <DollarSign className="w-3.5 h-3.5 text-emerald-500/70" />
                        <span className="truncate">{salaryText}</span>
                      </div>
                    )}
                    {job.duration && (
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-emerald-500/70" />
                        <span className="truncate">{job.duration}</span>
                      </div>
                    )}
                    {job.work_mode && (
                      <div className="flex items-center gap-1.5 capitalize">
                        <Briefcase className="w-3.5 h-3.5 text-emerald-500/70" />
                        <span className="truncate">{job.work_mode}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-auto pt-4 flex gap-2 border-t border-border">
                  <Button 
                    size="sm" 
                    className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 shadow-md"
                    onClick={(e) => handlePrepareResume(jobId, e)}
                  >
                    <Sparkles className="w-3 h-3 mr-2" /> Optimize
                  </Button>
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={(e) => handleIgnore(jobId, e)}
                    className="text-muted-foreground hover:text-red-400 px-2"
                  >
                   Ignore
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
