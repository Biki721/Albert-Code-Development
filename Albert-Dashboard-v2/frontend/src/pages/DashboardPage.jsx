import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  LogOut, Play, StopCircle, Calendar, Upload, 
  Activity, CheckCircle, Clock, Loader2 
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useAutomationStore } from '../store/automationStore';
import { useDashboardFormStore } from '../store/dashboardFormStore';
import ThemeToggle from '../components/ThemeToggle';
import MultiSelect from '../components/MultiSelect';
import AdhocWordTable from '../components/AdhocWordTable';
import DatePicker from '../components/DatePicker';
import TimePicker from '../components/TimePicker';
import toast from 'react-hot-toast';
import AdhocLinkTable from '../components/AdhocLinkTable';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const {
    languages,
    accounts,
    modules,
    runningJob,
    systemStatus,
    jobs,
    loadLanguages,
    loadAccounts,
    loadModules,
    loadRunningJob,
    loadSystemStatus,
    loadJobs,
    submitJob,
    stopAutomation,
    startPolling,
    stopPolling,
  } = useAutomationStore();

  // Form state (persisted via Zustand store)
  const {
    mode,
    selectedLanguages,
    selectedAccounts,
    selectedDomains,
    selectedModules,
    adhocType,
    sharepointUpload,
    scheduleDate,
    scheduleTime,
    scheduleMode,
    setMode,
    setSelectedLanguages,
    setSelectedAccounts,
    setSelectedDomains,
    setSelectedModules,
    setAdhocType,
    setSharepointUpload,
    setScheduleDate,
    setScheduleTime,
    setScheduleMode,
    resetAfterRun,
  } = useDashboardFormStore();
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Load resources
    loadLanguages();
    loadAccounts();
    loadModules();
    loadSystemStatus();
    loadJobs();
    
    // Start polling for updates
    startPolling();
    
    return () => {
      stopPolling();
    };
  }, []);

  useEffect(() => {
    // Load accounts when languages change
    if (selectedLanguages.length > 0) {
      loadAccounts();
    }
  }, [selectedLanguages]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleRunAutomation = async () => {
    setIsSubmitting(true);
    
    try {
      // Build request
      const request = {
        mode,
        sharepoint_upload: sharepointUpload,
        schedule_time: null,
      };

      // Add schedule time only when scheduling is enabled
      if (scheduleMode === 'later') {
        if (!scheduleDate || !scheduleTime) {
          toast.error('Please select schedule date and time');
          return;
        }
        const scheduledDateTime = new Date(`${scheduleDate}T${scheduleTime}:00`);
        if (scheduledDateTime.getTime() <= Date.now()) {
          toast.error('Schedule time must be in the future');
          return;
        }
        request.schedule_time = `${scheduleDate}T${scheduleTime}:00`;
      }

      if (mode === 'REG') {
        // Regular mode
        if (selectedAccounts.length === 0) {
          toast.error('Please select at least one account');
          return;
        }
        if (selectedDomains.length === 0) {
          toast.error('Please select at least one domain');
          return;
        }
        if (selectedModules.length === 0) {
          toast.error('Please select at least one module');
          return;
        }

        request.accounts = selectedAccounts;
        request.languages = selectedLanguages;
        request.domains = selectedDomains;
        request.modules = selectedModules;
      } else {
        // Adhoc mode
        if (!adhocType) {
          toast.error('Please select an adhoc type');
          return;
        }
        request.adhoc_type = adhocType;
      }

      const result = await submitJob(request);
      
      if (result.success) {
        toast.success(
          request.schedule_time 
            ? 'Automation scheduled successfully!' 
            : 'Automation started!'
        );
        
        // Reset relevant parts of form (but keep mode/languages)
        resetAfterRun();
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Failed to submit automation');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStop = async () => {
    const result = await stopAutomation();
    if (result.success) {
      toast.success('Automation stopped');
    } else {
      toast.error(result.error);
    }
  };

  const formatAccountType = (type) => {
    if (!type) return '';
    const lower = String(type).toLowerCase();
    if (lower === 'distri') return 'Distributor';
    if (lower === 't2') return 'Solution Provider (T2)';
    if (lower === 't1') return 'Partner (T1)';
    return type;
  };

  const formatAccountOption = (account) => {
    const typeLabel = formatAccountType(account.account_type);
    // Clean, human-friendly label like: "Distributor – United Kingdom (English)"
    return `${typeLabel} – ${account.country} (${account.language})`;
  };

  const filteredAccounts =
    selectedLanguages && selectedLanguages.length > 0
      ? accounts.filter((account) => selectedLanguages.includes(account.language))
      : [];

  const lastRegularJob = jobs ? jobs.find((job) => job.mode === 'REG') : null;
  const lastAdhocJob = jobs ? jobs.find((job) => job.mode === 'ADH') : null;

  const getJobDisplayTime = (job) => {
    if (!job) return null;
    const ts = job.completed_at || job.started_at || job.created_at;
    return ts ? new Date(ts).toLocaleString() : null;
  };

  const formatStatusLabel = (status) => {
    if (!status) return '';
    return status.charAt(0).toUpperCase() + status.slice(1);
  };
  

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-950">
      {/* Header */}
      <header className="bg-white/90 dark:bg-slate-950/80 backdrop-blur border-b border-gray-200 dark:border-slate-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* HPE-style logo + title */}
              <div className="flex items-center gap-3">
                <div className="h-6 w-20 border-4 border-hpe-green rounded-sm bg-transparent" />
                <div className="flex flex-col">
                  <span className="text-lg font-semibold text-gray-900 dark:text-slate-50">
                    Albert Dashboard
                  </span>
                  <span className="text-xs text-gray-600 dark:text-slate-400">
                    Welcome, {user?.email}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* System Status */}
              {systemStatus && (
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-slate-800 rounded-lg">
                  <Activity className="w-4 h-4 text-gray-600 dark:text-slate-200" />
                  <span className="text-sm font-medium text-gray-700 dark:text-slate-100">
                    {systemStatus.status === 'running' ? 'Running' : 'Idle'}
                  </span>
                </div>
              )}

              <ThemeToggle />

              <button
                type="button"
                onClick={() => navigate('/fixers')}
                className="btn-secondary flex items-center gap-2"
              >
                Fixers
              </button>
              
              <button
                onClick={handleLogout}
                className="btn-secondary flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Mode Selection */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Mode Selection
              </h2>
              <div>
                <div className="inline-flex rounded-full bg-gray-100 dark:bg-slate-900 p-1 border border-gray-200 dark:border-slate-700">
                  <button
                    type="button"
                    onClick={() => setMode('REG')}
                    className={`px-3 py-1.5 text-xs sm:text-sm rounded-full transition ${
                      mode === 'REG'
                        ? 'bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-50 shadow-sm'
                        : 'text-gray-600 dark:text-slate-300'
                    }`}
                  >
                    Regular
                  </button>
                  <button
                    type="button"
                    onClick={() => setMode('ADH')}
                    className={`px-3 py-1.5 text-xs sm:text-sm rounded-full transition ${
                      mode === 'ADH'
                        ? 'bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-50 shadow-sm'
                        : 'text-gray-600 dark:text-slate-300'
                    }`}
                  >
                    Adhoc
                  </button>
                </div>
              </div>
            </div>

            {/* Regular Mode Configuration */}
            {mode === 'REG' && (
              <div className="card space-y-6">
                <h2 className="text-lg font-semibold text-gray-900">
                  Regular Mode Configuration
                </h2>

                {/* Languages */}
                <div>
                  <MultiSelect
                    label="Languages"
                    options={languages.map((lang) => ({ value: lang, label: lang }))}
                    value={selectedLanguages}
                    onChange={setSelectedLanguages}
                  />
                </div>

                {/* Accounts */}
                {filteredAccounts.length > 0 && (
                  <div>
                    <MultiSelect
                      label="Demo Accounts"
                      options={filteredAccounts.map((account) => {
                        const accountStr = `${account.email}|${account.password}|${account.region}|${account.country}|${account.language}|${account.account_type}`;
                        return {
                          value: accountStr,
                          label: formatAccountOption(account),
                          // Show the raw email in the smaller secondary line
                          description: account.email,
                        };
                      })}
                      value={selectedAccounts}
                      onChange={setSelectedAccounts}
                    />
                  </div>
                )}

                {/* Domains */}
                <div>
                  <MultiSelect
                    label="Domains"
                    options={(modules?.domains || []).map((domain) => ({
                      value: domain,
                      label: domain,
                    }))}
                    value={selectedDomains}
                    onChange={setSelectedDomains}
                  />
                </div>

                {/* Modules */}
                <div>
                  <MultiSelect
                    label="Modules"
                    options={(modules?.modules || []).map((module) => ({
                      value: module,
                      label: module.replace(/_/g, ' '),
                    }))}
                    value={selectedModules}
                    onChange={setSelectedModules}
                  />
                </div>
              </div>
            )}

            {/* Adhoc Mode Configuration */}
            {mode === 'ADH' && (
              <div className="card">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Adhoc Mode Configuration
                </h2>
                <div>
                  <MultiSelect
                    label="Adhoc Type"
                    multiple={false}
                    options={(modules?.adhoc_types || []).map((type) => ({
                      value: type,
                      label: type,
                    }))}
                    value={adhocType}
                    onChange={setAdhocType}
                  />
                </div>
                {adhocType === 'Adhoc Word Search' && (
                  <AdhocWordTable />
                )}
                {adhocType === 'Adhoc URL Search' && (
                  <AdhocLinkTable />
                )}
              </div>
            )}

            {/* Schedule and Options */}
            <div className="card space-y-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Schedule & Options
              </h2>
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-slate-100 mb-2">
                    Run timing
                  </p>
                  <div className="inline-flex rounded-full bg-gray-100 dark:bg-slate-900 p-1 border border-gray-200 dark:border-slate-700">
                    <button
                      type="button"
                      onClick={() => {
                        setScheduleMode('now');
                        setScheduleDate('');
                        setScheduleTime('');
                      }}
                      className={`flex items-center gap-2 px-3 py-1.5 text-xs sm:text-sm rounded-full transition ${
                        scheduleMode === 'now'
                          ? 'bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-50 shadow-sm'
                          : 'text-gray-600 dark:text-slate-300'
                      }`}
                    >
                      <Play className="w-4 h-4" />
                      <span>Run now</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setScheduleMode('later')}
                      className={`flex items-center gap-2 px-3 py-1.5 text-xs sm:text-sm rounded-full transition ${
                        scheduleMode === 'later'
                          ? 'bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-50 shadow-sm'
                          : 'text-gray-600 dark:text-slate-300'
                      }`}
                    >
                      <Calendar className="w-4 h-4" />
                      <span>Schedule</span>
                    </button>
                  </div>
                  <p className="mt-2 text-xs text-gray-500 dark:text-slate-400">
                    {scheduleMode === 'now'
                      ? 'Run will start immediately after submitting.'
                      : scheduleDate && scheduleTime
                        ? `Will run on ${new Date(`${scheduleDate}T${scheduleTime}:00`).toLocaleString()}`
                        : 'Select a date and time to schedule this run.'}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={sharepointUpload}
                    onChange={(e) => setSharepointUpload(e.target.checked)}
                    className="w-4 h-4 text-primary-600"
                  />
                  <label className="text-sm text-gray-700 dark:text-slate-100 flex items-center gap-1">
                    <Upload className="w-4 h-4" />
                    <span>SharePoint Upload</span>
                  </label>
                </div>
              </div>

              {scheduleMode === 'later' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <DatePicker
                    value={scheduleDate}
                    onChange={setScheduleDate}
                  />
                  <TimePicker
                    value={scheduleTime}
                    onChange={setScheduleTime}
                    date={scheduleDate}
                  />
                </div>
              )}

              <div className="flex gap-4 pt-4">
                <button
                  onClick={handleRunAutomation}
                  disabled={isSubmitting || !!runningJob}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      {scheduleMode === 'later' ? 'Schedule Run' : 'Run Now'}
                    </>
                  )}
                </button>
                
                {runningJob && (
                  <button
                    onClick={handleStop}
                    className="btn-danger flex items-center gap-2"
                  >
                    <StopCircle className="w-5 h-5" />
                    Stop
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Status */}
          <div className="space-y-6">
            {/* Running Job Status */}
            {runningJob ? (
              <div className="card border-l-4 border-l-blue-500 dark:border-l-blue-400">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-50 mb-4 flex items-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600 dark:text-blue-400" />
                  Running
                </h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">Job ID:</span>
                    <span className="ml-2 font-mono text-xs">{runningJob.job_id}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Mode:</span>
                    <span className="ml-2">{runningJob.mode}</span>
                  </div>
                  {runningJob.progress && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-900">{runningJob.progress}</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="card border-l-4 border-l-green-500 dark:border-l-emerald-400">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-50 mb-2 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600 dark:text-emerald-400" />
                  System Idle
                </h3>
                <p className="text-sm text-gray-600">
                  Ready to run automation
                </p>
              </div>
            )}

            {/* System Info */}
            {systemStatus && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  System Status
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Jobs:</span>
                    <span className="font-medium">{systemStatus.active_jobs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Scheduled Jobs:</span>
                    <span className="font-medium">{systemStatus.scheduled_jobs}</span>
                  </div>
                  {systemStatus.last_run && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Run:</span>
                      <span className="font-medium">
                        {new Date(systemStatus.last_run).toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Albert / Adhoc Status (derived from jobs) */}
            {(runningJob || (jobs && jobs.length > 0)) && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-slate-50 mb-2">
                  Albert Status
                </h3>
                <div className="space-y-3 text-sm">
                  {/* Current status */}
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-slate-300">Current</span>
                    {runningJob ? (
                      <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
                        <span className="w-2 h-2 rounded-full bg-blue-500 mr-1.5" />
                        Running 
                        <span className="mx-1">·</span>
                        {runningJob.mode === 'REG' ? 'Regular' : 'Adhoc'}
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-green-50 text-green-700 dark:bg-emerald-900/40 dark:text-emerald-300">
                        <span className="w-2 h-2 rounded-full bg-green-500 mr-1.5" />
                        Idle
                      </span>
                    )}
                  </div>

                  {/* Last runs */}
                  <div className="border-t border-gray-100 dark:border-slate-800 pt-2 mt-1">
                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-slate-400 mb-2">
                      Last runs
                    </p>
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600 dark:text-slate-300">Regular</span>
                        {lastRegularJob ? (
                          <div className="text-right">
                            <div className="text-xs font-medium text-gray-800 dark:text-slate-100">
                              {formatStatusLabel(lastRegularJob.status)}
                            </div>
                            {getJobDisplayTime(lastRegularJob) && (
                              <div className="text-[11px] text-gray-500 dark:text-slate-400">
                                {getJobDisplayTime(lastRegularJob)}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-xs text-gray-400 dark:text-slate-500">
                            No runs yet
                          </span>
                        )}
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600 dark:text-slate-300">Adhoc</span>
                        {lastAdhocJob ? (
                          <div className="text-right">
                            <div className="text-xs font-medium text-gray-800 dark:text-slate-100">
                              {formatStatusLabel(lastAdhocJob.status)}
                            </div>
                            {getJobDisplayTime(lastAdhocJob) && (
                              <div className="text-[11px] text-gray-500 dark:text-slate-400">
                                {getJobDisplayTime(lastAdhocJob)}
                              </div>
                            )}
                          </div>
                        ) : (
                          <span className="text-xs text-gray-400 dark:text-slate-500">
                            No runs yet
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Recent runs */}
                  {jobs && jobs.length > 0 && (
                    <div className="border-t border-gray-100 dark:border-slate-800 pt-2 mt-1">
                      <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-slate-400 mb-1">
                        Recent runs
                      </p>
                      <ul className="space-y-1 max-h-32 overflow-y-auto text-xs">
                        {jobs.slice(0, 5).map((job) => {
                          const ts = job.completed_at || job.started_at || job.created_at;
                          return (
                            <li key={job.job_id} className="flex items-center justify-between">
                              <span className="text-gray-700 dark:text-slate-200">
                                {job.mode === 'REG' ? 'Regular' : 'Adhoc'} · {formatStatusLabel(job.status)}
                              </span>
                              <span className="text-gray-500 dark:text-slate-400 ml-2">
                                {ts ? new Date(ts).toLocaleTimeString() : '--'}
                              </span>
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
