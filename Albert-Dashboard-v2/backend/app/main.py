"""
FastAPI main application
Albert Automation Dashboard Backend
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional
import json
import ast
from pathlib import Path

import pandas as pd

from .config import settings
from .models import (
    UserLogin, Token, AuthStatus, AutomationRequest, 
    AutomationResponse, AutomationJob, StopRequest,
    AvailableModules, SystemStatus, AccountInfo,
    DomainType, ModuleType, AdhocType,
    FixersWorkbook, TableSheet, AdhocWordTable, AdhocLinkTable
)
from .auth import (
    login_user, logout_user, get_current_user, 
    require_session_lock, session_lock
)
from .scheduler import job_scheduler


def load_demo_accounts():
    """Load demo_accounts from UAT/demo_accounts.py without executing code."""
    accounts_file = settings.MODULES_DIR / "demo_accounts.py"
    source = accounts_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(accounts_file))

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "demo_accounts":
                    return ast.literal_eval(node.value)

    raise ValueError("demo_accounts assignment not found")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Albert Dashboard Backend...")
    print(f"📁 Modules directory: {settings.MODULES_DIR}")
    print(f"📊 Reports directory: {settings.REPORTS_DIR}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down scheduler...")
    job_scheduler.shutdown()
    print("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": settings.APP_NAME
    }


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Login endpoint
    Authenticates user and acquires exclusive session lock
    """
    return login_user(login_data)


@app.post("/api/auth/logout")
async def logout(email: str = Depends(get_current_user)):
    """
    Logout endpoint
    Releases session lock
    """
    success = logout_user(email)
    if success:
        return {"message": "Logged out successfully"}
    return {"message": "Logout failed"}


@app.get("/api/auth/status", response_model=AuthStatus)
async def auth_status():
    """
    Get current authentication/lock status
    Public endpoint - no authentication required
    """
    return session_lock.get_status()


@app.get("/api/auth/me")
async def get_me(email: str = Depends(get_current_user)):
    """Get current user info"""
    return {"email": email}


# ============================================================================
# ACCOUNTS AND MODULES
# ============================================================================

@app.get("/api/accounts", response_model=List[AccountInfo])
async def get_accounts(
    language: Optional[str] = None,
    email: str = Depends(require_session_lock)
):
    """
    Get available demo accounts
    Optionally filter by language
    """
    try:
        demo_accounts = load_demo_accounts()
        
        # Flatten accounts
        all_accounts = []
        for lang, accounts in demo_accounts.items():
            if language and lang != language:
                continue
            
            for account in accounts:
                all_accounts.append(AccountInfo(
                    email=account[0],
                    password=account[1],
                    region=account[2],
                    country=account[3],
                    language=account[4],
                    account_type=account[5]
                ))
        
        return all_accounts
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load accounts: {str(e)}"
        )


@app.get("/api/languages")
async def get_languages(email: str = Depends(require_session_lock)):
    """Get available languages"""
    try:
        demo_accounts = load_demo_accounts()
        
        return {"languages": list(demo_accounts.keys())}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load languages: {str(e)}"
        )


@app.get("/api/modules", response_model=AvailableModules)
async def get_modules(email: str = Depends(require_session_lock)):
    """Get available automation modules"""
    return AvailableModules(
        domains=[d.value for d in DomainType],
        modules=[m.value for m in ModuleType],
        adhoc_types=[a.value for a in AdhocType]
    )


# ============================================================================
# AUTOMATION ENDPOINTS
# ============================================================================

@app.post("/api/automation/run", response_model=AutomationResponse)
async def run_automation(
    request: AutomationRequest,
    email: str = Depends(require_session_lock)
):
    """
    Submit automation job
    Can run immediately or schedule for later
    """
    try:
        # Prevent new runs while another job is currently running
        running_job = job_scheduler.get_running_job()
        if running_job:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Job {running_job.job_id} is currently running. Please wait until it completes.",
            )

        job = job_scheduler.submit_job(request, email)
        
        return AutomationResponse(
            job_id=job.job_id,
            status=job.status,
            message=f"Job {'scheduled for' if request.schedule_time else 'started'} successfully",
            scheduled_for=request.schedule_time
        )
    except HTTPException:
        # Re-raise explicit HTTP errors (like 423 lock)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit job: {str(e)}"
        )


@app.get("/api/automation/jobs", response_model=List[AutomationJob])
async def get_jobs(
    email: str = Depends(require_session_lock)
):
    """Get all jobs for current user"""
    return job_scheduler.get_all_jobs(user_email=email)


@app.get("/api/automation/job/{job_id}", response_model=AutomationJob)
async def get_job_status(
    job_id: str,
    email: str = Depends(require_session_lock)
):
    """Get status of specific job"""
    job = job_scheduler.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify user owns this job
    if job.user_email != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this job"
        )
    
    return job


@app.get("/api/automation/running", response_model=Optional[AutomationJob])
async def get_running_job(email: str = Depends(require_session_lock)):
    """Get currently running job"""
    return job_scheduler.get_running_job()


@app.post("/api/automation/stop")
async def stop_automation(
    request: StopRequest,
    email: str = Depends(require_session_lock)
):
    """
    Stop running or cancel scheduled job
    """
    if request.job_id:
        success = job_scheduler.cancel_job(request.job_id)
        if success:
            return {"message": f"Job {request.job_id} cancelled"}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel job (may not exist or already completed)"
        )
    else:
        # Stop current running job
        running_job = job_scheduler.get_running_job()
        if running_job:
            job_scheduler.cancel_job(running_job.job_id)
            return {"message": f"Stopped job {running_job.job_id}"}
        return {"message": "No running job to stop"}


@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status(email: str = Depends(require_session_lock)):
    """Get system status"""
    lock_status = session_lock.get_status()
    running_job = job_scheduler.get_running_job()
    all_jobs = job_scheduler.get_all_jobs(user_email=email)
    
    # Get last completed job
    completed_jobs = [j for j in all_jobs if j.completed_at]
    last_run = completed_jobs[0].completed_at if completed_jobs else None
    
    return SystemStatus(
        status="running" if running_job else "idle",
        locked_by=lock_status.locked_by,
        active_jobs=1 if running_job else 0,
        scheduled_jobs=job_scheduler.get_scheduled_jobs_count(),
        last_run=last_run
    )


# ============================================================================
# TABLE ENDPOINTS - FIXERS & ADHOC WORD SEARCH
# ============================================================================

FIXERS_SOURCE_PATH = settings.MODULES_DIR / "Fixers_list.xlsx"
ADHOC_WORDS_PATH = settings.MODULES_DIR / "Ad hoc Requests" / "Aruba Series names - Adhoc request.xlsx"
ADHOC_LINKS_PATH = settings.MODULES_DIR / "Ad hoc Requests" / "AD_HOC_Links_To_Search.xlsx"


@app.get("/api/fixers", response_model=FixersWorkbook)
async def get_fixers(email: str = Depends(require_session_lock)):
    """Get Fixers workbook (all sheets)"""
    try:
        if not FIXERS_SOURCE_PATH.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fixers_list.xlsx not found",
            )

        xls = pd.ExcelFile(FIXERS_SOURCE_PATH)
        sheets: List[TableSheet] = []

        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            sheets.append(
                TableSheet(
                    name=sheet_name,
                    columns=list(df.columns),
                    rows=df.to_dict(orient="records"),
                )
            )

        return FixersWorkbook(sheets=sheets)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load fixers workbook: {str(e)}",
        )


@app.post("/api/fixers")
async def save_fixers(
    payload: FixersWorkbook,
    email: str = Depends(require_session_lock),
):
    """Save Fixers workbook edits to Fixers_list.xlsx"""
    try:
        FIXERS_SOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)

        with pd.ExcelWriter(FIXERS_SOURCE_PATH) as writer:
            for sheet in payload.sheets:
                df = pd.DataFrame(sheet.rows, columns=sheet.columns)
                df.to_excel(writer, sheet_name=sheet.name, index=False)

        return {"message": "Fixers workbook saved"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save fixers workbook: {str(e)}",
        )


@app.get("/api/adhoc/words", response_model=AdhocWordTable)
async def get_adhoc_words(email: str = Depends(require_session_lock)):
    try:
        if not ADHOC_WORDS_PATH.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Adhoc request file not found",
            )

        df = pd.read_excel(ADHOC_WORDS_PATH)

        # 🔥 CRITICAL FIX
        df = df.where(pd.notnull(df), None)

        return AdhocWordTable(
            columns=list(df.columns),
            rows=df.to_dict(orient="records"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load adhoc words table: {str(e)}",
        )


@app.post("/api/adhoc/words")
async def save_adhoc_words(
    payload: AdhocWordTable,
    email: str = Depends(require_session_lock),
):
    """Save adhoc word-search table edits"""
    try:
        ADHOC_WORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(payload.rows, columns=payload.columns)
        df.to_excel(ADHOC_WORDS_PATH, index=False)
        return {"message": "Adhoc words table saved"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save adhoc words table: {str(e)}",
        )



@app.get("/api/adhoc/links", response_model=AdhocLinkTable)
async def get_adhoc_links(email: str = Depends(require_session_lock)):
    try:
        if not ADHOC_LINKS_PATH.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Adhoc links file not found",
            )

        df = pd.read_excel(ADHOC_LINKS_PATH)

        # 🔥 Critical JSON safety
        df = df.where(pd.notnull(df), None)

        return AdhocLinkTable(
            columns=list(df.columns),
            rows=df.to_dict(orient="records"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load adhoc links table: {str(e)}",
        )


@app.post("/api/adhoc/links")
async def save_adhoc_links(
    payload: AdhocLinkTable,
    email: str = Depends(require_session_lock),
):
    try:
        ADHOC_LINKS_PATH.parent.mkdir(parents=True, exist_ok=True)

        df = pd.DataFrame(payload.rows, columns=payload.columns)
        df.to_excel(ADHOC_LINKS_PATH, index=False)

        return {"message": "Adhoc links table saved"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save adhoc links table: {str(e)}",
        )



# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  Albert Automation Dashboard - Backend Server            ║
    ║  Version: {settings.APP_VERSION}                         ║
    ╚══════════════════════════════════════════════════════════╝
    
    Starting server on {settings.HOST}:{settings.PORT} 
    
    API Documentation: http://localhost:{settings.PORT}/docs
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
