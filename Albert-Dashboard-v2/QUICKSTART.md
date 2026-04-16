# Quick Start Guide - Albert Dashboard v2

Get up and running in 5 minutes for development.

## Development Setup

### Backend (Terminal 1)

```bash
# 1. Navigate to backend
cd Albert-Dashboard-v2/backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Windows)
venv\Scripts\activate
# Or Mac/Linux:
# source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright
python -m playwright install chromium

# 6. Create .env file
cp .env.example .env
# Edit .env and set SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")

# 7. Run backend
python -m app.main
```

Backend will run on: **http://localhost:8000**  
API docs: **http://localhost:8000/docs**

### Frontend (Terminal 2)

```bash
# 1. Navigate to frontend
cd Albert-Dashboard-v2/frontend

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev
```

Frontend will run on: **http://localhost:3000**

### Access Dashboard

1. Open browser: http://localhost:3000
2. Login with:
   - **Email:** admin@hpe.com
   - **Password:** Admin@123

## Testing the System

### 1. Test Authentication
- Try logging in with correct credentials
- Try logging in with wrong credentials
- Try logging in while already logged in (from another browser/incognito)

### 2. Test Exclusive Lock
- Login from one browser
- Try to login from another browser/incognito window
- Should show: "admin@hpe.com is currently logged in"

### 3. Test Automation (if UAT modules available)
- Select Regular mode
- Choose languages → accounts → domains → modules
- Click "Run Now"
- Watch status updates

## Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment guide to:
- Install backend as Windows service
- Deploy frontend to IIS
- Configure security and networking
- Setup remote access

## Key Files

- `backend/app/main.py` - FastAPI application
- `backend/app/auth.py` - Authentication & session locking
- `backend/app/module_runner.py` - Automation module executor
- `frontend/src/pages/DashboardPage.jsx` - Main UI
- `config/users.json` - User accounts

## Common Issues

### Backend won't start
- Check Python version (3.9+)
- Ensure venv is activated
- Check .env file exists
- Verify port 8000 is not in use

### Frontend shows blank page
- Check backend is running
- Open browser console for errors
- Verify API calls are proxied correctly

### Modules not found
- Check MODULES_DIR in backend/app/config.py
- Ensure ../UAT directory exists with automation modules

### Session lock stuck
- Restart backend server (lock clears)
- Or wait 30 minutes for automatic timeout

## Next Steps

1. **Add Users:** Edit `config/users.json` or use user manager API
2. **Customize:** Update branding in frontend
3. **Configure:** Adjust timeouts and settings in backend .env
4. **Deploy:** Follow DEPLOYMENT.md for production setup

## Architecture Overview

```
┌──────────────┐         REST API         ┌─────────────────┐
│   React UI   │◄─────────────────────────┤  FastAPI        │
│  (Port 3000) │                          │  (Port 8000)    │
└──────────────┘                          └─────────────────┘
                                                   │
                                                   │ Executes
                                                   ▼
                                          ┌─────────────────┐
                                          │ UAT Modules     │
                                          │ (Playwright/    │
                                          │  Selenium)      │
                                          └─────────────────┘
```

## Support

- **Documentation:** See README.md and DEPLOYMENT.md
- **API Docs:** http://localhost:8000/docs (when backend running)
- **Logs:** backend/service.log
- **Contact:** biki.dey@hpe.com
