# Albert Automation Dashboard v2

Modern, secure web-based automation dashboard with exclusive single-user access.

## Architecture

```
┌─────────────────┐         HTTP/REST API        ┌──────────────────┐
│   React App     │◄──────────────────────────────┤  FastAPI Backend │
│   (IIS Hosted)  │                               │  (Windows Svc)   │
└─────────────────┘                               └──────────────────┘
                                                           │
                                                           │ Executes
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ Automation      │
                                                  │ Modules         │
                                                  │ (RDP Server)    │
                                                  └─────────────────┘
```

## Features

- **Single-user exclusive access** - Only one authenticated user at a time
- **30-minute inactivity timeout** - Automatic session expiration
- **Secure authentication** - Bcrypt password hashing
- **Remote execution** - All automation runs on RDP server
- **Scheduling support** - Run now or schedule for later
- **Modern React UI** - Clean, responsive interface
- **Windows Service** - Backend runs as system service

## Project Structure

```
Albert-Dashboard-v2/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI app entry
│   │   ├── auth.py         # Authentication logic
│   │   ├── models.py       # Data models
│   │   ├── database.py     # Database/session storage
│   │   ├── scheduler.py    # Job scheduling
│   │   ├── module_runner.py # Automation module executor
│   │   └── config.py       # Configuration
│   ├── requirements.txt
│   └── service_setup.py    # Windows service installer
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── web.config          # IIS configuration
├── modules/                 # Unified module wrappers
│   ├── module_wrapper.py   # Base wrapper class
│   └── runners/            # Individual module runners
└── config/
    ├── users.json          # User credentials
    └── accounts.json       # Demo accounts
```

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m app.main  # Development mode
# OR install as Windows service (see deployment docs)
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev  # Development mode
npm run build  # Production build for IIS
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions on:
- Installing backend as Windows service
- Configuring IIS for React app
- Setting up SSL/HTTPS
- Firewall configuration

## API Endpoints

- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/logout` - Logout and release lock
- `GET /api/auth/status` - Check current session
- `POST /api/automation/run` - Execute automation now
- `POST /api/automation/schedule` - Schedule automation
- `GET /api/automation/status` - Get execution status
- `GET /api/accounts` - List available accounts
- `GET /api/modules` - List automation modules

## Security

- Passwords hashed with bcrypt (cost factor: 12)
- JWT tokens with 30-min expiration
- CORS configured for specific origin only
- Rate limiting on authentication endpoints
- Session lock prevents concurrent access

## License

Internal HPE tool - Not for external distribution
