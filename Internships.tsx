// pages/Internships.tsx - Internships Page
// Enahnced with Advanced Filters & Rich Data
import { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { jobsApi } from '@/lib/api';
import { Job, getJobId } from '@/types';
import { 
  Loader2, MapPin, GraduationCap, Sparkles, Filter, Briefcase, 
  DollarSign, Clock, ArrowDownWideNarrow, Bot
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

// Utility to format stipend
const formatStipend = (min?: number, max?: number, type?: string) => {
  if (!min && !max) return 'Unpaid / Not Disclosed';
  
  const formatNum = (num: number) => {
    if (num >= 100000) return `₹${(num/100000).toFixed(1)}L`;
    if (num >= 1000) return `₹${(num/1000).toFixed(0)}k`;
    return `₹${num}`;
  };

  const period = type === 'monthly' ? '/mo' : type === 'hourly' ? '/hr' : (type === 'yearly' ? '/yr' : '');
  
  if (min && max) return `${formatNum(min)} - ${formatNum(max)}${period}`;
  if (min) return `${formatNum(min)}${period}`;
  return `${formatNum(max!)}${period}`;
};

export default function Internships() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { toast } = useToast();

  // Filters state
  const [sortBy, setSortBy] = useState<'score' | 'date' | 'stipend'>('score');
  const [locationFilter, setLocationFilter] = useState<string>('all');
  const [modeFilter, setModeFilter] = useState<string>('all'); 
  const [stipendFilter, setStipendFilter] = useState<number>(0);

  const { data: jobs = [], isLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: jobsApi.getJobs,
    refetchInterval: 30000,
  });

  const internJobs = useMemo(() => {
    return jobs.filter(job => {
      const title = job.job_title?.toLowerCase() || '';
      const desc = job.job_description?.toLowerCase() || '';
      const source = job.source?.toLowerCase() || '';
      const jobType = (job as any).job_type?.toLowerCase() || '';
      
      return (
        title.includes('intern') ||
        title.includes('internship') ||
        desc.includes('internship') ||
        source.includes('internshala') ||
        jobType === 'internship' ||
        jobType === 'intern'
      );
    });
  }, [jobs]);

  // Extract unique locations
  const uniqueLocations = useMemo(() => {
    const locs = new Set<string>();
    internJobs.forEach(job => {
      if (job.location && job.location !== 'Remote') {
        const city = job.location.split(',')[0].trim();
        locs.add(city);
      }
    });
    return Array.from(locs).sort();
  }, [internJobs]);

  // Filter Logic
  const filteredJobs = useMemo(() => {
    let filtered = [...internJobs];

    // Location
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

    // Work Mode
    if (modeFilter !== 'all') {
      filtered = filtered.filter(job => 
        job.work_mode === modeFilter || 
        (modeFilter === 'remote' && job.location?.toLowerCase().includes('remote'))
      );
    }

    // Sorting
    return filtered.sort((a, b) => {
      if (sortBy === 'score') {
        return (b.match_score || 0) - (a.match_score || 0);
      }
      if (sortBy === 'stipend') {
        const salA = a.salary_max || a.salary_min || 0;
        const salB = b.salary_max || b.salary_min || 0;
        return salB - salA;
      }
      // Date
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    });
  }, [internJobs, locationFilter, modeFilter, sortBy]);

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
          <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <GraduationCap className="w-8 h-8 text-purple-500" />
              <h1 className="text-2xl font-bold">Internships</h1>
            </div>
            <p className="text-muted-foreground">{filteredJobs.length} opportunities for students & freshers</p>
          </div>
        </div>

        {/* Filters Toolbar */}
        <div className="p-4 bg-card border border-purple-500/20 rounded-xl shadow-sm space-y-4 md:space-y-0 md:flex md:items-center md:gap-4 md:flex-wrap">
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
              <SelectItem value="stipend">Sort by Stipend (High-Low)</SelectItem>
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
            <GraduationCap className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">No internships found</h2>
            <p className="text-muted-foreground">Try adjusting filters or check back later</p>
          </div>
        )}

        {/* Jobs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredJobs.map((job) => {
            const jobId = getJobId(job);
            const stipendText = formatStipend(job.salary_min, job.salary_max, job.salary_type || 'monthly');
            const score = job.match_score || 0;
            
            return (
              <div
                key={jobId}
                className="bg-card border border-purple-500/20 rounded-xl p-4 hover:border-purple-500/60 transition-all cursor-pointer group hover:shadow-lg flex flex-col h-full"
                onClick={() => handleViewJob(job)}
              >
                {/* Company Logo & Match */}
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold flex-shrink-0">
                    {job.company_name?.charAt(0) || 'C'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-foreground group-hover:text-purple-400 transition-colors line-clamp-1">
                      {job.job_title}
                    </h3>
                    <p className="text-sm text-muted-foreground line-clamp-1">{job.company_name}</p>
                  </div>
                </div>

                {/* Metadata Tags */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between">
                     <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                      score >= 80 ? 'bg-emerald-500/20 text-emerald-400' :
                      score >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {score}% Match
                    </span>
                    <Badge variant="outline" className="border-purple-500/30 text-purple-400 text-[10px]">
                      Internship
                    </Badge>
                  </div>

                  {/* Info Grid */}
                  <div className="grid grid-cols-2 gap-y-2 text-xs text-muted-foreground mt-2">
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-purple-400/70" />
                      <span className="truncate">{job.location || 'Remote'}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <DollarSign className="w-3.5 h-3.5 text-purple-400/70" />
                      <span className="truncate">{stipendText}</span>
                    </div>
                    {job.duration && (
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-purple-400/70" />
                        <span className="truncate">{job.duration}</span>
                      </div>
                    )}
                    {job.work_mode && (
                      <div className="flex items-center gap-1.5 capitalize">
                        <Briefcase className="w-3.5 h-3.5 text-purple-400/70" />
                        <span className="truncate">{job.work_mode === 'hybrid' ? 'Hybrid' : job.work_mode}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-auto pt-4 flex gap-2 border-t border-purple-500/10">
                  <Button 
                    size="sm" 
                    className="flex-1 bg-purple-500 hover:bg-purple-600 shadow-sm"
                    onClick={(e) => handlePrepareResume(jobId, e)}
                  >
                    <Sparkles className="w-3 h-3 mr-1" /> Optimize
                  </Button>
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={(e) => handleIgnore(jobId, e)}
                    className="text-muted-foreground hover:text-red-400"
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
