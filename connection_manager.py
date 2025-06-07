import socket
import os
import signal
import time
import psutil
import subprocess
from datetime import datetime

class LeoDockConnectionManager:
    def __init__(self):
        self.ports = [5000, 5001]
        self.lock_files = [f"/tmp/leodock_{port}.lock" for port in self.ports]
        self.service_names = {5000: "terminal", 5001: "dashboard"}
        
    def check_port_available(self, port):
        """Check if port is already in use"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0  # True if available (connection failed)
    
    def create_lock_file(self, port):
        """Create lock file to prevent multiple instances"""
        lock_file = f"/tmp/leodock_{port}.lock"
        
        # Check if lock file exists and if process is still running
        if os.path.exists(lock_file):
            try:
                with open(lock_file, 'r') as f:
                    old_pid = int(f.read().strip())
                
                # Check if old process is still running
                if psutil.pid_exists(old_pid):
                    try:
                        old_process = psutil.Process(old_pid)
                        if old_process.is_running():
                            print(f"🔒 Port {port} locked by existing process (PID: {old_pid})")
                            return False
                    except psutil.NoSuchProcess:
                        pass
                
                # Old process is dead, remove stale lock
                os.remove(lock_file)
                print(f"🧹 Removed stale lock file for port {port}")
                
            except (ValueError, IOError):
                # Invalid lock file, remove it
                os.remove(lock_file)
                print(f"🧹 Removed invalid lock file for port {port}")
        
        # Create new lock file
        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            print(f"🔒 Created lock file for port {port}")
            return True
        except IOError:
            print(f"❌ Failed to create lock file for port {port}")
            return False
    
    def cleanup_locks(self):
        """Clean up lock files on exit"""
        current_pid = os.getpid()
        for port in self.ports:
            lock_file = f"/tmp/leodock_{port}.lock"
            if os.path.exists(lock_file):
                try:
                    with open(lock_file, 'r') as f:
                        lock_pid = int(f.read().strip())
                    
                    if lock_pid == current_pid:
                        os.remove(lock_file)
                        print(f"🧹 Cleaned up lock file for port {port}")
                except (ValueError, IOError):
                    pass
    
    def safe_start_server(self, port, command):
        """Safely start server only if not already running"""
        service_name = self.service_names.get(port, f"service-{port}")
        
        print(f"🚀 Attempting to start {service_name} on port {port}")
        
        # Check if port is already in use
        if not self.check_port_available(port):
            print(f"⚠️ {service_name} already running on port {port}")
            return False
        
        # Try to acquire lock
        if not self.create_lock_file(port):
            print(f"⚠️ Could not acquire lock for {service_name} on port {port}")
            return False
        
        # Port is available and lock acquired
        print(f"✅ Starting {service_name} on port {port}")
        print(f"🔧 Command: {command}")
        
        return True
    
    def check_running_services(self):
        """Check status of all LeoDock services"""
        print(f"🔍 LeoDock Service Status - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        status = {}
        
        for port in self.ports:
            service_name = self.service_names[port]
            is_available = self.check_port_available(port)
            lock_file = f"/tmp/leodock_{port}.lock"
            has_lock = os.path.exists(lock_file)
            
            if has_lock:
                try:
                    with open(lock_file, 'r') as f:
                        lock_pid = int(f.read().strip())
                    lock_info = f"PID {lock_pid}"
                    
                    # Check if process is still running
                    if psutil.pid_exists(lock_pid):
                        try:
                            process = psutil.Process(lock_pid)
                            lock_info += f" ({process.name()})"
                        except psutil.NoSuchProcess:
                            lock_info += " (dead)"
                    else:
                        lock_info += " (dead)"
                        
                except (ValueError, IOError):
                    lock_info = "invalid"
            else:
                lock_info = "none"
            
            service_status = "🔴 Down" if is_available else "🟢 Running"
            status[port] = {
                'name': service_name,
                'running': not is_available,
                'lock': lock_info
            }
            
            print(f"{service_name.capitalize():>10}: {service_status} | Lock: {lock_info}")
        
        return status
    
    def kill_duplicate_browsers(self, keep_count=2):
        """Kill excess browser processes to prevent multiplication"""
        print(f"\n🔧 Checking for duplicate browsers (keeping {keep_count})")
        
        browser_processes = []
        leodock_browsers = []
        other_browsers = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                if any(browser in proc_name for browser in ['chrome', 'firefox', 'browser', 'chromium']):
                    cmdline_str = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    
                    browser_info = {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline_str
                    }
                    
                    if any(keyword in cmdline_str.lower() for keyword in ['localhost', '5000', '5001', 'leodock']):
                        leodock_browsers.append(browser_info)
                    else:
                        other_browsers.append(browser_info)
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        print(f"   LeoDock browsers: {len(leodock_browsers)}")
        print(f"   Other browsers: {len(other_browsers)}")
        
        # Kill excess LeoDock browsers
        if len(leodock_browsers) > keep_count:
            excess_count = len(leodock_browsers) - keep_count
            print(f"   🗑️ Killing {excess_count} excess LeoDock browsers")
            
            for browser in leodock_browsers[keep_count:]:
                try:
                    process = psutil.Process(browser['pid'])
                    process.terminate()
                    print(f"      Terminated PID {browser['pid']} ({browser['name']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
        # Warn about unusual number of other browsers
        if len(other_browsers) > 3:
            print(f"   ⚠️ Warning: {len(other_browsers)} non-LeoDock browsers running")
            print(f"      This might indicate a browser multiplication issue")
    
    def emergency_cleanup(self):
        """Emergency cleanup of all LeoDock processes and locks"""
        print("🚨 Emergency cleanup initiated")
        
        # Clean up lock files
        self.cleanup_locks()
        
        # Kill excess browsers
        self.kill_duplicate_browsers(keep_count=1)
        
        # Kill any python processes related to LeoDock
        killed_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                    cmdline_str = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if any(keyword in cmdline_str.lower() for keyword in ['leodock', 'pyxtermjs']):
                        if proc.info['pid'] != os.getpid():  # Don't kill ourselves!
                            try:
                                process = psutil.Process(proc.info['pid'])
                                process.terminate()
                                killed_processes.append(proc.info['pid'])
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if killed_processes:
            print(f"🗑️ Terminated LeoDock processes: {killed_processes}")
        
        print("✅ Emergency cleanup complete")

if __name__ == "__main__":
    import sys
    manager = LeoDockConnectionManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            manager.check_running_services()
        elif command == "cleanup":
            manager.emergency_cleanup()
        elif command == "kill-browsers":
            manager.kill_duplicate_browsers()
        elif command == "test":
            # Test safe server starting
            for port in [5000, 5001]:
                can_start = manager.safe_start_server(port, f"test-command-{port}")
                print(f"Can start on port {port}: {can_start}")
        else:
            print("Unknown command")
    else:
        # Default: check current status
        status = manager.check_running_services()
        manager.kill_duplicate_browsers()
        
        print(f"\n💡 Available commands:")
        print(f"   python connection_manager.py status    - Check service status")
        print(f"   python connection_manager.py cleanup   - Emergency cleanup")
        print(f"   python connection_manager.py kill-browsers - Remove excess browsers")
        print(f"   python connection_manager.py test      - Test port availability")