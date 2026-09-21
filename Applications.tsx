// pages/Applications.tsx - Applied Jobs Table View
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { jobsApi } from '@/lib/api';
import { Job } from '@/types';
import { Loader2, Search, ExternalLink, MoreHorizontal, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MatchScoreRing } from '@/components/dashboard/MatchScoreRing';
import { JobDetailModal } from '@/components/dashboard/JobDetailModal';
import { ChatbotSidebar } from '@/components/dashboard/ChatbotSidebar';

type ApplicationStatus = 'applied' | 'interviewing' | 'offer_received' | 'rejected' | 'archived';

const STATUS_TABS: { key: ApplicationStatus | 'all'; label: string }[] = [
  { key: 'applied', label: 'Applied' },
  { key: 'interviewing', label: 'Interviewing' },
  { key: 'offer_received', label: 'Offer Received' },
  { key: 'rejected', label: 'Rejected' },
  { key: 'archived', label: 'Archived' },
];

export default function Applications() {
  const [activeTab, setActiveTab] = useState<ApplicationStatus | 'all'>('applied');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(true);

  const { data: jobs = [], isLoading } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: jobsApi.getJobs,
  });

  // Filter jobs by status and search
  const filteredJobs = useMemo(() => {
    return jobs.filter(job => {
      // Status filter
      const statusMatch = activeTab === 'all' || 
        job.status === activeTab || 
        (activeTab === 'applied' && job.status === 'applied');
      
      // Search filter
      const searchMatch = !searchQuery || 
        job.job_title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.company_name?.toLowerCase().includes(searchQuery.toLowerCase());
      
      return statusMatch && searchMatch;
    });
  }, [jobs, activeTab, searchQuery]);

  // Count by status
  const statusCounts = useMemo(() => {
    return {
      applied: jobs.filter(j => j.status === 'applied').length,
      interviewing: jobs.filter(j => j.status === 'interviewing').length,
      offer_received: jobs.filter(j => j.status === 'offer_received').length,
      rejected: jobs.filter(j => j.status === 'rejected').length,
      archived: jobs.filter(j => j.status === 'archived').length,
    };
  }, [jobs]);

  const handleJobClick = (job: Job) => {
    setSelectedJob(job);
    setIsDetailOpen(true);
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
      <div className={`transition-all duration-300 ${isChatOpen ? 'mr-80' : 'mr-0'}`}>
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">Applications</h1>
          <p className="text-muted-foreground">Track your job applications and interview progress</p>
        </div>

        {/* Status Tabs */}
        <div className="flex items-center gap-1 mb-6 border-b border-border">
          {STATUS_TABS.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-3 text-sm font-medium transition-colors relative ${
                activeTab === tab.key
                  ? 'text-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {tab.label}
              <span className={`ml-1.5 px-1.5 py-0.5 rounded text-xs ${
                activeTab === tab.key
                  ? 'bg-emerald-500/20 text-emerald-400'
                  : 'bg-muted text-muted-foreground'
              }`}>
                {statusCounts[tab.key as keyof typeof statusCounts] || 0}
              </span>
              {activeTab === tab.key && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500" />
              )}
            </button>
          ))}
          
          {/* Search */}
          <div className="ml-auto relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search applications..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-64"
            />
          </div>
        </div>

        {/* Applications List */}
        <div className="space-y-4">
          {filteredJobs.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>No applications in this category</p>
            </div>
          ) : (
            filteredJobs.map(job => (
              <ApplicationCard 
                key={job.id} 
                job={job} 
                onClick={() => handleJobClick(job)}
              />
            ))
          )}
        </div>
      </div>

      {/* Chatbot Sidebar */}
      <ChatbotSidebar
        isOpen={isChatOpen}
        onToggle={() => setIsChatOpen(!isChatOpen)}
        currentJob={selectedJob}
      />

      {/* Job Detail Modal */}
      {selectedJob && (
        <JobDetailModal
          job={selectedJob}
          isOpen={isDetailOpen}
          onClose={() => setIsDetailOpen(false)}
          onChatAboutJob={(job) => {
            setSelectedJob(job);
            setIsChatOpen(true);
            setIsDetailOpen(false);
          }}
        />
      )}
    </DashboardLayout>
  );
}

// Application Card Component
function ApplicationCard({ job, onClick }: { job: Job; onClick: () => void }) {
  return (
    <div 
      className="flex items-center gap-4 p-4 rounded-xl bg-card border border-border hover:border-emerald-500/30 transition-colors cursor-pointer group"
      onClick={onClick}
    >
      {/* Company Logo */}
      <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center text-white font-bold flex-shrink-0">
        {job.company_name?.charAt(0) || 'C'}
      </div>

      {/* Job Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs text-muted-foreground">
            {job.applied_at ? `Applied on ${new Date(job.applied_at).toLocaleDateString()}` : 'Recently'}
          </span>
        </div>
        <h3 className="font-semibold text-foreground truncate">{job.job_title}</h3>
        <p className="text-sm text-muted-foreground truncate">
          {job.company_name} • {job.location || 'Remote'}
        </p>
        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
          <span>{job.job_type || 'Full-time'}</span>
          {job.salary_range && <span>{job.salary_range}</span>}
        </div>
      </div>

      {/* Match Score */}
      <div className="flex-shrink-0">
        <MatchScoreRing score={job.match_score || 75} size="sm" showBreakdown={false} />
      </div>

      {/* Status Dropdown */}
      <div className="flex-shrink-0">
        <Button variant="outline" size="sm" className="gap-2">
          {job.status === 'applied' && 'Applied'}
          {job.status === 'interviewing' && 'Interviewing'}
          {job.status === 'offer_received' && 'Offer Received'}
          {job.status === 'rejected' && 'Rejected'}
          {job.status === 'archived' && 'Archived'}
          <ChevronDown className="w-3 h-3" />
        </Button>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="icon"
          onClick={(e) => {
            e.stopPropagation();
            if (job.source_url) window.open(job.source_url, '_blank');
          }}
        >
          <ExternalLink className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
