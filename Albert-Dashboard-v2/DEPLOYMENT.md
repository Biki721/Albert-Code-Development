# Albert Dashboard v2 - Deployment Guide

Complete guide for deploying the Albert Automation Dashboard on Windows RDP server.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Security Configuration](#security-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Windows Server** (2016 or later)
- **IIS 10.0** or later with URL Rewrite module
- **Python 3.9+** installed on RDP server
- **Node.js 18+** for building frontend
- **Administrator access** for service installation

### Software Installation

1. **Install Python 3.9+**
   ```powershell
   # Download and install from python.org
   # Verify installation
   python --version
   ```

2. **Install IIS and URL Rewrite**
   ```powershell
   # Enable IIS
   Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer
   
   # Install URL Rewrite module
   # Download from: https://www.iis.net/downloads/microsoft/url-rewrite
   ```

3. **Install Node.js** (only needed for building, not for runtime)
   ```powershell
   # Download from nodejs.org
   node --version
   npm --version
   ```

---

## Backend Deployment

### Step 1: Setup Python Environment

```powershell
# Navigate to backend directory
cd C:\Albert-Dashboard-v2\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install chromium
```

### Step 2: Configure Environment

```powershell
# Copy .env.example to .env
copy .env.example .env

# Edit .env file with your configuration
notepad .env
```

**Important .env settings:**
```env
SECRET_KEY=<generate-a-strong-random-key>
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://your-iis-server,http://localhost:3000
SESSION_LOCK_TIMEOUT=1800
MODULES_DIR=C:\Albert-Code-Development\UAT
```

**Generate SECRET_KEY:**
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Test Backend

```powershell
# Run in debug mode first
python -m app.main

# Test endpoints
# Open browser: http://localhost:8000/docs
```

### Step 4: Install as Windows Service

```powershell
# Ensure pywin32 is installed
pip install pywin32

# Install service (run as Administrator)
python service_setup.py install

# Start service
python service_setup.py start

# Check service status
python service_setup.py status

# View logs
type service.log
```

**Service Management Commands:**
```powershell
# Stop service
python service_setup.py stop

# Restart service
python service_setup.py restart

# Remove service
python service_setup.py remove

# Run in debug mode (not as service)
python service_setup.py debug
```

### Step 5: Configure Firewall

```powershell
# Allow inbound traffic on port 8000
New-NetFirewallRule -DisplayName "Albert Dashboard Backend" `
  -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

---

## Frontend Deployment

### Step 1: Build React App

```powershell
# Navigate to frontend directory
cd C:\Albert-Dashboard-v2\frontend

# Install dependencies
npm install

# Create production build
npm run build

# Build output will be in: dist/
```

### Step 2: Configure IIS

1. **Create IIS Website:**
   ```powershell
   # Open IIS Manager
   inetmgr
   
   # Or use PowerShell:
   Import-Module WebAdministration
   
   # Create new website
   New-Website -Name "AlbertDashboard" `
     -PhysicalPath "C:\Albert-Dashboard-v2\frontend\dist" `
     -Port 80
   ```

2. **Copy web.config:**
   ```powershell
   # web.config should already be in dist/ after build
   # If not, copy it manually:
   copy web.config dist\web.config
   ```

3. **Configure Application Pool:**
   - Open IIS Manager
   - Select Application Pools → AlbertDashboard
   - Set .NET CLR Version: "No Managed Code"
   - Set Identity: ApplicationPoolIdentity or custom account with appropriate permissions

### Step 3: Configure URL Rewrite (API Proxy)

The `web.config` already includes API proxy rules. Verify in IIS Manager:

1. Select your site → URL Rewrite
2. Should see two rules:
   - **React Routes** - Handles SPA routing
   - **ReverseProxyInbound** - Proxies `/api/*` to backend

### Step 4: Test Frontend

1. Open browser: `http://your-server`
2. Should see Albert Dashboard login page
3. Default credentials: `admin@hpe.com` / `Admin@123`

---

## Security Configuration

### 1. HTTPS Setup (Recommended)

```powershell
# Generate self-signed certificate (for internal use)
New-SelfSignedCertificate -DnsName "your-server.domain.com" `
  -CertStoreLocation "cert:\LocalMachine\My"

# Or import corporate certificate
# Import-PfxCertificate -FilePath certificate.pfx `
#   -CertStoreLocation Cert:\LocalMachine\My

# Bind certificate to IIS site
# In IIS Manager:
# Site → Bindings → Add → Type: https → Select certificate
```

### 2. Update Backend CORS

After enabling HTTPS, update backend `.env`:
```env
CORS_ORIGINS=https://your-server,https://your-server.domain.com
```

Then restart backend service:
```powershell
python service_setup.py restart
```

### 3. Firewall Rules

```powershell
# Allow HTTPS
New-NetFirewallRule -DisplayName "Albert Dashboard HTTPS" `
  -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow

# Restrict access to specific IPs (optional)
New-NetFirewallRule -DisplayName "Albert Dashboard Backend Restricted" `
  -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow `
  -RemoteAddress 192.168.1.0/24
```

### 4. User Management

**Add new user:**
```python
# On RDP server
cd C:\Albert-Dashboard-v2\backend
.\venv\Scripts\activate
python

# In Python shell:
from app.auth import user_manager
user_manager.create_user(
    email="user@hpe.com",
    password="SecurePassword123",
    full_name="User Name"
)
```

### 5. Change Default Password

**Edit config/users.json** or use Python:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
new_hash = pwd_context.hash("NewPassword123")
print(new_hash)
```

Update `config/users.json` with new hash.

---

## Remote Access Setup

### From Local Computer

1. **Update Frontend API URL:**
   
   Edit `frontend/.env` or `frontend/vite.config.js`:
   ```javascript
   // vite.config.js
   export default defineConfig({
     server: {
       proxy: {
         '/api': {
           target: 'http://rdp-server-ip:8000', // Update this
           changeOrigin: true,
         },
       },
     },
   });
   ```

2. **Or update after build:**
   
   Frontend makes API calls to `/api/*` which IIS proxies to backend.
   No additional configuration needed if accessing via IIS.

### Network Configuration

1. **RDP Server:**
   - Ensure port 80/443 (IIS) is accessible
   - Backend port 8000 should only be accessible locally or from IIS
   
2. **VPN/Network:**
   - Connect to corporate VPN if required
   - Ensure no firewall blocking between local machine and RDP server

---

## Monitoring and Maintenance

### Backend Logs

```powershell
# Service logs
type C:\Albert-Dashboard-v2\backend\service.log

# Application logs
type C:\Albert-Dashboard-v2\backend\albert_dashboard.db
```

### IIS Logs

Located in: `C:\inetpub\logs\LogFiles\`

### Check Service Status

```powershell
# Windows Services
Get-Service | Where-Object {$_.Name -eq "AlbertDashboardBackend"}

# Or use service manager
services.msc
```

### Restart Services

```powershell
# Restart backend service
python service_setup.py restart

# Restart IIS
iisreset
```

---

## Troubleshooting

### Backend Service Won't Start

1. **Check logs:**
   ```powershell
   type C:\Albert-Dashboard-v2\backend\service.log
   ```

2. **Test manually:**
   ```powershell
   cd C:\Albert-Dashboard-v2\backend
   .\venv\Scripts\activate
   python service_setup.py debug
   ```

3. **Common issues:**
   - Port 8000 already in use
   - Missing dependencies
   - Incorrect paths in config.py
   - Insufficient permissions

### Frontend Shows Blank Page

1. **Check IIS logs** in Event Viewer
2. **Verify web.config** is in dist folder
3. **Check URL Rewrite module** is installed
4. **Browser console** for JavaScript errors

### API Calls Failing

1. **Check backend service is running:**
   ```powershell
   Get-Service AlbertDashboardBackend
   ```

2. **Test backend directly:**
   ```powershell
   curl http://localhost:8000/health
   ```

3. **Check CORS settings** in backend `.env`
4. **Verify IIS proxy rules** in web.config

### Session Lock Issues

1. **Check inactivity timeout** in config
2. **Clear stuck lock** (if needed):
   ```python
   # On RDP server
   from app.auth import session_lock
   session_lock._release_internal()
   ```

### Automation Modules Not Found

1. **Verify MODULES_DIR** in backend `.env`:
   ```env
   MODULES_DIR=C:\Albert-Code-Development\UAT
   ```

2. **Check file permissions** on UAT directory
3. **Ensure all dependencies** are installed in venv

---

## Backup and Recovery

### Backup Important Files

```powershell
# User database
copy C:\Albert-Dashboard-v2\config\users.json backup\

# Backend database
copy C:\Albert-Dashboard-v2\backend\albert_dashboard.db backup\

# Configuration
copy C:\Albert-Dashboard-v2\backend\.env backup\
```

### Disaster Recovery

1. Reinstall dependencies
2. Restore configuration files
3. Reinstall Windows service
4. Rebuild and redeploy frontend

---

## Support

For issues or questions:
1. Check logs first
2. Review this documentation
3. Contact: biki.dey@hpe.com

---

**Last Updated:** 2024-11-29
**Version:** 2.0.0
