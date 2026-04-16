"""
Windows Service Setup for Albert Dashboard Backend
Install backend as a Windows service
"""
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import logging
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))


class AlbertDashboardService(win32serviceutil.ServiceFramework):
    """Windows Service for Albert Dashboard Backend"""
    
    _svc_name_ = "AlbertDashboardBackend"
    _svc_display_name_ = "Albert Dashboard Backend Service"
    _svc_description_ = "FastAPI backend service for Albert Automation Dashboard"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True
        
        # Setup logging
        log_path = Path(__file__).parent / "service.log"
        logging.basicConfig(
            filename=str(log_path),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def SvcStop(self):
        """Stop the service"""
        self.logger.info('Stopping Albert Dashboard Backend Service...')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_running = False
    
    def SvcDoRun(self):
        """Run the service"""
        self.logger.info('Starting Albert Dashboard Backend Service...')
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
    
    def main(self):
        """Main service loop"""
        try:
            self.logger.info('Initializing FastAPI server...')
            
            # Import here to avoid issues with service startup
            import uvicorn
            from app.main import app
            from app.config import settings
            
            # Configure uvicorn
            config = uvicorn.Config(
                app,
                host=settings.HOST,
                port=settings.PORT,
                log_level="info",
                access_log=True
            )
            server = uvicorn.Server(config)
            
            self.logger.info(f'Server starting on {settings.HOST}:{settings.PORT}')
            
            # Run server
            import asyncio
            asyncio.run(server.serve())
            
        except Exception as e:
            self.logger.error(f'Service error: {str(e)}', exc_info=True)
            servicemanager.LogErrorMsg(f"Albert Dashboard Backend error: {str(e)}")


def install_service():
    """Install the Windows service"""
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AlbertDashboardService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AlbertDashboardService)


if __name__ == '__main__':
    """
    Usage:
        python service_setup.py install   - Install service
        python service_setup.py start     - Start service
        python service_setup.py stop      - Stop service
        python service_setup.py remove    - Remove service
        python service_setup.py restart   - Restart service
        python service_setup.py debug     - Run in debug mode (not as service)
    """
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        # Run in debug mode (not as a service)
        print("Running in debug mode...")
        service = AlbertDashboardService([])
        service.main()
    else:
        install_service()
