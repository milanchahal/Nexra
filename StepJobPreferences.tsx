import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Briefcase, MapPin, Building2, TrendingUp, X } from 'lucide-react';
import type { JobPreferences } from '@/types';

interface StepJobPreferencesProps {
  preferences: JobPreferences;
  onChange: (preferences: JobPreferences) => void;
}

const ROLE_SUGGESTIONS = [
  'Software Engineer',
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'Python Developer',
  'Java Developer',
  'React Developer',
  'Node.js Developer',
  'Data Scientist',
  'ML Engineer',
  'AI Engineer',
  'DevOps Engineer',
  'Cloud Engineer',
  'Product Manager',
  'UX Designer',
  'Mobile Developer',
  'QA Engineer',
  'Software Intern',
  'Data Analyst',
  'Fresher',
];

// All major Indian cities and tech hubs
const LOCATION_SUGGESTIONS = [
  // Major Tech Hubs
  'Bangalore',
  'Hyderabad',
  'Pune',
  'Chennai',
  'Mumbai',
  'Delhi NCR',
  'Gurgaon',
  'Noida',
  'Kolkata',
  'Ahmedabad',
  // Other Major Cities
  'Jaipur',
  'Chandigarh',
  'Lucknow',
  'Kochi',
  'Coimbatore',
  'Indore',
  'Bhopal',
  'Nagpur',
  'Visakhapatnam',
  'Thiruvananthapuram',
  // Remote Option
  'Remote',
  'Work from Home',
  'Pan India',
];

export function StepJobPreferences({
  preferences,
  onChange,
}: StepJobPreferencesProps) {
  const toggleRole = (role: string) => {
    const roles = preferences.roles.includes(role)
      ? preferences.roles.filter((r) => r !== role)
      : [...preferences.roles, role];
    onChange({ ...preferences, roles });
  };

  const toggleLocation = (location: string) => {
    const locations = preferences.locations.includes(location)
      ? preferences.locations.filter((l) => l !== location)
      : [...preferences.locations, location];
    onChange({ ...preferences, locations });
  };

  return (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-semibold text-foreground">
          Set Your Job Preferences
        </h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          Tell us what you're looking for. Clawd.bot will automatically find and match jobs for you.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Preferred Roles */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-muted-foreground" />
            <Label className="text-base">Preferred Roles</Label>
          </div>
          <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
            {ROLE_SUGGESTIONS.map((role) => (
              <Badge
                key={role}
                variant={preferences.roles.includes(role) ? 'default' : 'outline'}
                className="cursor-pointer hover:bg-primary/90 transition-colors"
                onClick={() => toggleRole(role)}
              >
                {role}
                {preferences.roles.includes(role) && (
                  <X className="ml-1 h-3 w-3" />
                )}
              </Badge>
            ))}
          </div>
          {preferences.roles.length > 0 && (
            <p className="text-sm text-muted-foreground">
              {preferences.roles.length} role(s) selected
            </p>
          )}
        </div>

        {/* Preferred Locations - India */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-muted-foreground" />
            <Label className="text-base">Preferred Locations (India)</Label>
          </div>
          <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
            {LOCATION_SUGGESTIONS.map((location) => (
              <Badge
                key={location}
                variant={preferences.locations.includes(location) ? 'default' : 'outline'}
                className="cursor-pointer hover:bg-primary/90 transition-colors"
                onClick={() => toggleLocation(location)}
              >
                {location}
                {preferences.locations.includes(location) && (
                  <X className="ml-1 h-3 w-3" />
                )}
              </Badge>
            ))}
          </div>
          {preferences.locations.length > 0 && (
            <p className="text-sm text-muted-foreground">
              {preferences.locations.length} location(s) selected
            </p>
          )}
        </div>

        {/* Remote Preference */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-muted-foreground" />
            <Label className="text-base">Work Style</Label>
          </div>
          <RadioGroup
            value={preferences.remotePreference}
            onValueChange={(value) =>
              onChange({
                ...preferences,
                remotePreference: value as JobPreferences['remotePreference'],
              })
            }
            className="grid grid-cols-2 gap-3"
          >
            {[
              { value: 'remote', label: 'Remote Only' },
              { value: 'hybrid', label: 'Hybrid' },
              { value: 'onsite', label: 'On-site' },
              { value: 'any', label: 'Any' },
            ].map(({ value, label }) => (
              <div key={value} className="flex items-center space-x-2">
                <RadioGroupItem value={value} id={`remote-${value}`} />
                <Label htmlFor={`remote-${value}`} className="font-normal cursor-pointer">
                  {label}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>

        {/* Experience Level */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-muted-foreground" />
            <Label className="text-base">Experience Level</Label>
          </div>
          <RadioGroup
            value={preferences.experienceLevel}
            onValueChange={(value) =>
              onChange({
                ...preferences,
                experienceLevel: value as JobPreferences['experienceLevel'],
              })
            }
            className="grid grid-cols-2 gap-3"
          >
            {[
              { value: 'fresher', label: 'Fresher (0-1 yr)' },
              { value: 'entry', label: 'Entry (1-3 yrs)' },
              { value: 'mid', label: 'Mid (3-5 yrs)' },
              { value: 'senior', label: 'Senior (5+ yrs)' },
              { value: 'any', label: 'Any Level' },
            ].map(({ value, label }) => (
              <div key={value} className="flex items-center space-x-2">
                <RadioGroupItem value={value} id={`exp-${value}`} />
                <Label htmlFor={`exp-${value}`} className="font-normal cursor-pointer">
                  {label}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>

        {/* Company Type */}
        <div className="space-y-4 md:col-span-2">
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-muted-foreground" />
            <Label className="text-base">Company Type</Label>
          </div>
          <RadioGroup
            value={preferences.companyType}
            onValueChange={(value) =>
              onChange({
                ...preferences,
                companyType: value as JobPreferences['companyType'],
              })
            }
            className="flex flex-wrap gap-4"
          >
            {[
              { value: 'startup', label: 'Startups' },
              { value: 'mnc', label: 'MNCs (Google, Microsoft, etc.)' },
              { value: 'product', label: 'Product Companies' },
              { value: 'service', label: 'Service Companies' },
              { value: 'any', label: 'Open to any' },
            ].map(({ value, label }) => (
              <div key={value} className="flex items-center space-x-2">
                <RadioGroupItem value={value} id={`company-${value}`} />
                <Label htmlFor={`company-${value}`} className="font-normal cursor-pointer">
                  {label}
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>
      </div>
    </div>
  );
}
