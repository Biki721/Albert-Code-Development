"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserLogin(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthStatus(BaseModel):
    """Authentication status response"""
    authenticated: bool
    user_email: Optional[str] = None
    locked_by: Optional[str] = None
    lock_expires_at: Optional[datetime] = None


class AutomationMode(str, Enum):
    """Automation mode"""
    REGULAR = "REG"
    ADHOC = "ADH"


class DomainType(str, Enum):
    """Domain types"""
    PRP = "PRP"


class ModuleType(str, Enum):
    """Module types"""
    BROKEN_LINKS = "Broken_Links"
    TRANSLATION_EMPTY = "Translation_and_Empty_Page"
    NEW_TAB = "New_Tab"
    T_VARIABLE = "T_variable"
    EXTERNAL_LINKS = "External_Links"
    TRANSLATION_SPELLING_EMPTY = "Translation_Spelling_and_Empty_Page"
    SPELLING_CHECK = "Spelling_check"
    LOGIN = "Login"


class AdhocType(str, Enum):
    """Adhoc task types"""
    WORD_SEARCH = "Adhoc Word Search"
    URL_SEARCH = "Adhoc URL Search"


class AccountInfo(BaseModel):
    """Demo account information"""
    email: str
    password: str
    region: str
    country: str
    language: str
    account_type: str


class AutomationRequest(BaseModel):
    """Request to run automation"""
    mode: AutomationMode
    accounts: Optional[List[str]] = None  # Account emails for regular mode
    languages: Optional[List[str]] = None  # Languages to filter accounts
    domains: Optional[List[DomainType]] = None
    modules: Optional[List[ModuleType]] = None
    adhoc_type: Optional[AdhocType] = None
    sharepoint_upload: bool = False
    schedule_time: Optional[datetime] = None  # If None, run immediately
    
    @validator('accounts', 'domains', 'modules')
    def validate_regular_mode(cls, v, values):
        """Validate required fields for regular mode"""
        if values.get('mode') == AutomationMode.REGULAR:
            if 'accounts' in values and not values.get('accounts'):
                raise ValueError("accounts required for regular mode")
            if 'domains' in values and not values.get('domains'):
                raise ValueError("domains required for regular mode")
            if 'modules' in values and not values.get('modules'):
                raise ValueError("modules required for regular mode")
        return v
    
    @validator('adhoc_type')
    def validate_adhoc_mode(cls, v, values):
        """Validate required fields for adhoc mode"""
        if values.get('mode') == AutomationMode.ADHOC and not v:
            raise ValueError("adhoc_type required for adhoc mode")
        return v


class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class AutomationJob(BaseModel):
    """Automation job status"""
    job_id: str
    user_email: str
    status: JobStatus
    mode: AutomationMode
    request: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    progress: Optional[str] = None
    error: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


class AutomationResponse(BaseModel):
    """Response after submitting automation"""
    job_id: str
    status: JobStatus
    message: str
    scheduled_for: Optional[datetime] = None


class StopRequest(BaseModel):
    """Request to stop running automation"""
    job_id: Optional[str] = None  # If None, stop current running job


class AvailableModules(BaseModel):
    """Available automation modules"""
    domains: List[str]
    modules: List[str]
    adhoc_types: List[str]


class SystemStatus(BaseModel):
    """System status information"""
    status: str
    locked_by: Optional[str] = None
    active_jobs: int
    scheduled_jobs: int
    last_run: Optional[datetime] = None


class TableSheet(BaseModel):
    """Generic table sheet (for Excel-backed tables)"""
    name: str
    columns: List[str]
    rows: List[Dict[str, Any]]


class FixersWorkbook(BaseModel):
    """Fixers workbook with multiple sheets"""
    sheets: List[TableSheet]


class AdhocWordTable(BaseModel):
    """Adhoc word-search table"""
    columns: List[str]
    rows: List[Dict[str, Any]]

class AdhocLinkTable(BaseModel):
    """Adhoc word-search table"""
    columns: List[str]
    rows: List[Dict[str, Any]]
