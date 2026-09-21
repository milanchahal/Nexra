import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { useAuth } from '@/contexts/AuthContext';
import { settingsApi, type UserSettings } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import {
  Settings as SettingsIcon,
  Bell,
  Zap,
  FileText,
  MousePointer,
  LogOut,
  Loader2,
  Save,
} from 'lucide-react';

export default function Settings() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const { logout } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    setIsLoading(true);
    try {
      const response = await settingsApi.getSettings();
      setSettings(response.data);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSaveSettings() {
    if (!settings) return;
    
    setIsSaving(true);
    try {
      await settingsApi.updateSettings(settings);
      toast({
        title: 'Settings saved',
        description: 'Your preferences have been updated.',
      });
    } catch (error) {
      toast({
        title: 'Failed to save',
        description: 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  }

  function handleToggle(key: keyof UserSettings) {
    if (!settings) return;
    setSettings({ ...settings, [key]: !settings[key] });
  }

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-2xl">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Settings</h1>
          <p className="text-muted-foreground">
            Manage your preferences and automation settings
          </p>
        </div>

        {/* Email Preferences */}
        <div className="border border-border rounded-xl bg-card p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-muted-foreground" />
            <h2 className="font-medium text-foreground">Notifications</h2>
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Email Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Receive updates about new jobs and application status
              </p>
            </div>
            <Switch
              checked={settings?.emailNotifications}
              onCheckedChange={() => handleToggle('emailNotifications')}
            />
          </div>
        </div>

        {/* Automation Settings */}
        <div className="border border-border rounded-xl bg-card p-6 space-y-6">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-muted-foreground" />
            <h2 className="font-medium text-foreground">Automation</h2>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="flex items-center gap-2">
                <SettingsIcon className="w-4 h-4" />
                Job Discovery
              </Label>
              <p className="text-sm text-muted-foreground">
                Automatically find and match jobs to your profile
              </p>
            </div>
            <Switch
              checked={settings?.jobDiscoveryEnabled}
              onCheckedChange={() => handleToggle('jobDiscoveryEnabled')}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Auto Resume Generation
              </Label>
              <p className="text-sm text-muted-foreground">
                Automatically generate tailored resumes for high-match jobs
              </p>
            </div>
            <Switch
              checked={settings?.autoResumeGeneration}
              onCheckedChange={() => handleToggle('autoResumeGeneration')}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="flex items-center gap-2">
                <MousePointer className="w-4 h-4" />
                Autofill Applications
              </Label>
              <p className="text-sm text-muted-foreground">
                Automatically fill application forms with your profile data
              </p>
            </div>
            <Switch
              checked={settings?.autofillEnabled}
              onCheckedChange={() => handleToggle('autofillEnabled')}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <Button
            variant="destructive"
            onClick={handleLogout}
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
          <Button onClick={handleSaveSettings} disabled={isSaving}>
            {isSaving ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Save Changes
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
}
