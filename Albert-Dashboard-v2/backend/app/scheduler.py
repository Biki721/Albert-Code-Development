"""
Job scheduler for automation tasks
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from typing import Dict, Optional, List
from datetime import datetime
import uuid
import threading

from .config import settings
from .models import AutomationRequest, AutomationJob, JobStatus
from .module_runner import module_runner


class JobScheduler:
    """
    Manages scheduling and execution of automation jobs
    """
    
    def __init__(self):
        # Configure APScheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=1)  # Only 1 concurrent job
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 300
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=settings.SCHEDULER_TIMEZONE
        )
        
        # Job tracking
        self._jobs: Dict[str, AutomationJob] = {}
        self._lock = threading.Lock()
        self._current_running_job: Optional[str] = None
        
        # Start scheduler
        self.scheduler.start()
    
    def create_job_id(self) -> str:
        """Generate unique job ID"""
        return str(uuid.uuid4())
    
    def submit_job(
        self, 
        request: AutomationRequest, 
        user_email: str
    ) -> AutomationJob:
        """
        Submit a new automation job
        """
        job_id = self.create_job_id()
        
        # Create job record (use local server time for timestamps)
        job = AutomationJob(
            job_id=job_id,
            user_email=user_email,
            status=JobStatus.PENDING,
            mode=request.mode,
            request=request.dict(),
            created_at=datetime.now(),
            scheduled_for=request.schedule_time
        )
        
        with self._lock:
            self._jobs[job_id] = job
        
        # Schedule or run immediately
        if request.schedule_time:
            self._schedule_job(job_id, request, request.schedule_time)
        else:
            self._run_job_async(job_id, request)
        
        return job
    
    def _schedule_job(
        self, 
        job_id: str, 
        request: AutomationRequest, 
        run_time: datetime
    ):
        """Schedule job for future execution"""
        with self._lock:
            self._jobs[job_id].status = JobStatus.SCHEDULED
        
        self.scheduler.add_job(
            func=self._execute_job,
            trigger='date',
            run_date=run_time,
            args=[job_id, request],
            id=job_id,
            replace_existing=True
        )
    
    def _run_job_async(self, job_id: str, request: AutomationRequest):
        """Run job asynchronously in background thread"""
        thread = threading.Thread(
            target=self._execute_job,
            args=(job_id, request),
            daemon=True
        )
        thread.start()
    
    def _execute_job(self, job_id: str, request: AutomationRequest):
        """Execute automation job"""
        try:
            # Update status
            with self._lock:
                if job_id not in self._jobs:
                    return
                self._jobs[job_id].status = JobStatus.RUNNING
                self._jobs[job_id].started_at = datetime.now()
                self._current_running_job = job_id
            
            # Set progress callback
            def progress_callback(message: str):
                with self._lock:
                    if job_id in self._jobs:
                        self._jobs[job_id].progress = message
            
            module_runner.set_progress_callback(progress_callback)
            
            # Run automation
            results = module_runner.run_automation(request, job_id)
            
            # Update with results
            with self._lock:
                if job_id in self._jobs:
                    self._jobs[job_id].status = self._status_from_results(results)
                    self._jobs[job_id].completed_at = datetime.now()
                    self._jobs[job_id].results = results
                    if self._jobs[job_id].status == JobStatus.FAILED:
                        self._jobs[job_id].error = results.get("error") or "One or more automation units failed"
                    elif self._jobs[job_id].status == JobStatus.CANCELLED:
                        self._jobs[job_id].error = "Stopped by user"
                    self._current_running_job = None
        
        except Exception as e:
            with self._lock:
                if job_id in self._jobs:
                    self._jobs[job_id].status = JobStatus.FAILED
                    self._jobs[job_id].completed_at = datetime.now()
                    self._jobs[job_id].error = str(e)
                    self._current_running_job = None

    def _status_from_results(self, results: dict) -> JobStatus:
        """Derive the API job status from nested UAT runner results."""
        if results.get("status") == "failed":
            return JobStatus.FAILED

        unit_results = []
        for key in ("domain_results", "module_results", "adhoc_results"):
            values = results.get(key) or []
            if isinstance(values, list):
                unit_results.extend(values)

        statuses = {item.get("status") for item in unit_results if isinstance(item, dict)}
        if "cancelled" in statuses:
            return JobStatus.CANCELLED
        if "error" in statuses:
            return JobStatus.FAILED
        if results.get("sharepoint_upload_error"):
            return JobStatus.FAILED
        return JobStatus.COMPLETED
    
    def get_job(self, job_id: str) -> Optional[AutomationJob]:
        """Get job by ID"""
        with self._lock:
            return self._jobs.get(job_id)
    
    def get_all_jobs(self, user_email: Optional[str] = None) -> List[AutomationJob]:
        """Get all jobs, optionally filtered by user"""
        with self._lock:
            jobs = list(self._jobs.values())
            if user_email:
                jobs = [j for j in jobs if j.user_email == user_email]
            return sorted(jobs, key=lambda x: x.created_at, reverse=True)
    
    def get_running_job(self) -> Optional[AutomationJob]:
        """Get currently running job"""
        with self._lock:
            if self._current_running_job:
                return self._jobs.get(self._current_running_job)
            return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job"""
        try:
            with self._lock:
                job = self._jobs.get(job_id)
                if not job:
                    return False
                
                # Can only cancel scheduled jobs
                if job.status == JobStatus.SCHEDULED:
                    self.scheduler.remove_job(job_id)
                    job.status = JobStatus.CANCELLED
                    return True
                
                # Can stop running jobs
                elif job.status == JobStatus.RUNNING:
                    if self._current_running_job == job_id:
                        module_runner.stop()
                        job.status = JobStatus.CANCELLED
                        return True
                
                return False
        except Exception:
            return False
    
    def get_scheduled_jobs_count(self) -> int:
        """Get count of scheduled jobs"""
        with self._lock:
            return sum(1 for j in self._jobs.values() if j.status == JobStatus.SCHEDULED)
    
    def shutdown(self):
        """Shutdown scheduler"""
        self.scheduler.shutdown(wait=False)


# Global scheduler instance
job_scheduler = JobScheduler()
