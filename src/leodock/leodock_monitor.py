import psutil
import requests
import time
import subprocess
import sys
from datetime import datetime
from advanced_chat_history import AdvancedChatHistory

class LeoDockMonitor:
    def __init__(self):
        self.services = {
            'terminal': 'http://127.0.0.1:5000',
            'dashboard': 'http://127.0.0.1:5001', 
            'lm_studio': 'http://127.0.0.1:1234/v1/models'
        }
        self.chat_history = AdvancedChatHistory()
        self.alerts = []
        
    def check_service_health(self):
        """Check health of all LeoDock services"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"🏥 LeoDock Health Check - {timestamp}")
        print("=" * 50)
        
        service_status = {}
        
        for service, url in self.services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    status = "✅ Healthy"
                    health = True
                else:
                    status = f"⚠️ Status {response.status_code}"
                    health = False
                    self.alerts.append(f"{service} returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                status = f"❌ Down ({str(e)[:30]}...)"
                health = False
                self.alerts.append(f"{service} is down: {str(e)[:50]}")
            
            service_status[service] = health
            print(f"{service.capitalize():>10}: {status}")
        
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"\n🖥️ System Resources:")
        print(f"CPU Usage: {cpu_percent:.1f}%")
        print(f"Memory: {memory.percent:.1f}% ({memory.used // 1024**2}MB / {memory.total // 1024**2}MB)")
        print(f"Disk: {disk.percent:.1f}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)")
        
        # Resource alerts
        if cpu_percent > 80:
            self.alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
        if memory.percent > 85:
            self.alerts.append(f"High memory usage: {memory.percent:.1f}%")
        if disk.percent > 90:
            self.alerts.append(f"High disk usage: {disk.percent:.1f}%")
        
        # Check for browser processes
        browser_processes = self._check_browser_processes()
        
        # Check for Python processes related to LeoDock
        leodock_processes = self._check_leodock_processes()
        
        print(f"\n📊 Process Summary:")
        print(f"Browser processes: {browser_processes['count']} {'⚠️' if browser_processes['count'] > 3 else '✅'}")
        print(f"LeoDock processes: {leodock_processes['count']} {'⚠️' if leodock_processes['count'] > 5 else '✅'}")
        
        return {
            'timestamp': timestamp,
            'services': service_status,
            'resources': {
                'cpu': cpu_percent,
                'memory': memory.percent,
                'disk': disk.percent
            },
            'processes': {
                'browsers': browser_processes,
                'leodock': leodock_processes
            },
            'alerts': self.alerts.copy()
        }
    
    def _check_browser_processes(self):
        """Check browser processes for multiplication issues"""
        browsers = {'leodock': [], 'other': [], 'count': 0}
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            try:
                proc_name = proc.info['name'].lower()
                if any(browser in proc_name for browser in ['chrome', 'firefox', 'browser', 'chromium']):
                    cmdline_str = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    memory_mb = proc.info['memory_info'].rss // 1024**2
                    
                    browser_info = {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'memory': memory_mb,
                        'cmdline': cmdline_str[:100]
                    }
                    
                    if any(keyword in cmdline_str.lower() for keyword in ['localhost', '5000', '5001', 'leodock']):
                        browsers['leodock'].append(browser_info)
                    else:
                        browsers['other'].append(browser_info)
                    
                    browsers['count'] += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Check for excessive browsers
        if browsers['count'] > 5:
            self.alerts.append(f"Excessive browser processes: {browsers['count']}")
        
        if len(browsers['other']) > 3:
            self.alerts.append(f"Too many non-LeoDock browsers: {len(browsers['other'])}")
        
        return browsers
    
    def _check_leodock_processes(self):
        """Check LeoDock-related Python processes"""
        processes = {'count': 0, 'details': []}
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
            try:
                if proc.info['name'] in ['python', 'python3']:
                    cmdline_str = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if any(keyword in cmdline_str.lower() for keyword in ['leodock', 'pyxtermjs', 'talk_to_leo', 'llm_', 'chat_history']):
                        memory_mb = proc.info['memory_info'].rss // 1024**2
                        
                        process_info = {
                            'pid': proc.info['pid'],
                            'memory': memory_mb,
                            'cpu': proc.info['cpu_percent'],
                            'cmdline': cmdline_str[:80]
                        }
                        
                        processes['details'].append(process_info)
                        processes['count'] += 1
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return processes
    
    def auto_fix_issues(self):
        """Automatically fix common issues"""
        print("\n🔧 Auto-fixing common issues...")
        fixes_applied = []
        
        # Kill excessive browser processes
        browser_processes = self._check_browser_processes()
        
        if len(browser_processes['other']) > 3:
            print(f"🗑️ Killing {len(browser_processes['other']) - 2} excess non-LeoDock browsers")
            killed_count = 0
            
            for browser in browser_processes['other'][2:]:  # Keep first 2
                try:
                    psutil.Process(browser['pid']).terminate()
                    killed_count += 1
                    fixes_applied.append(f"Killed browser PID {browser['pid']}")
                except psutil.NoSuchProcess:
                    pass
            
            if killed_count > 0:
                print(f"   ✅ Terminated {killed_count} excess browsers")
        
        # Check for zombie LeoDock processes
        leodock_processes = self._check_leodock_processes()
        high_memory_processes = [p for p in leodock_processes['details'] if p['memory'] > 500]  # > 500MB
        
        if high_memory_processes:
            print(f"🧠 Found {len(high_memory_processes)} high-memory LeoDock processes")
            for proc in high_memory_processes:
                print(f"   ⚠️ PID {proc['pid']}: {proc['memory']}MB - {proc['cmdline'][:50]}...")
        
        # Clean up old lock files
        import os
        lock_files_cleaned = 0
        for port in [5000, 5001]:
            lock_file = f"/tmp/leodock_{port}.lock"
            if os.path.exists(lock_file):
                try:
                    with open(lock_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    if not psutil.pid_exists(pid):
                        os.remove(lock_file)
                        lock_files_cleaned += 1
                        fixes_applied.append(f"Removed stale lock file for port {port}")
                except (ValueError, IOError):
                    os.remove(lock_file)
                    lock_files_cleaned += 1
                    fixes_applied.append(f"Removed invalid lock file for port {port}")
        
        if lock_files_cleaned > 0:
            print(f"🧹 Cleaned up {lock_files_cleaned} stale lock files")
        
        if not fixes_applied:
            print("   ✅ No issues found that require auto-fixing")
        
        return fixes_applied
    
    def run_health_check_with_leo(self):
        """Run health check and get Leo's analysis"""
        print("🦁 Running health check with Leo's analysis...")
        
        health_data = self.check_service_health()
        auto_fixes = self.auto_fix_issues()
        
        # Prepare health summary for Leo
        health_summary = f"""
        LeoDock Health Check Results:
        - Services: {len([s for s in health_data['services'].values() if s])} of {len(health_data['services'])} healthy
        - CPU: {health_data['resources']['cpu']:.1f}%
        - Memory: {health_data['resources']['memory']:.1f}%
        - Browser processes: {health_data['processes']['browsers']['count']}
        - LeoDock processes: {health_data['processes']['leodock']['count']}
        - Alerts: {len(health_data['alerts'])}
        - Auto-fixes applied: {len(auto_fixes)}
        """
        
        # Ask Leo for analysis
        try:
            from talk_to_leo import talk_to_leo
            leo_analysis = talk_to_leo(
                f"Analyze this LeoDock platform health report and provide recommendations: {health_summary}",
                mode="code_analysis"
            )
            
            print(f"\n🦁 Leo's Health Analysis:")
            print(f"   {leo_analysis}")
            
            # Store the health check in chat history
            self.chat_history.save_conversation(
                "leodock_monitor",
                f"Health check completed. Services: {health_data['services']}, Alerts: {len(health_data['alerts'])}",
                session_id="health_monitoring",
                metadata={"type": "health_check", "alerts": health_data['alerts']}
            )
            
        except Exception as e:
            print(f"❌ Could not get Leo's analysis: {e}")
        
        return health_data
    
    def continuous_monitoring(self, interval=30):
        """Run continuous monitoring"""
        print(f"🔄 Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                health_data = self.run_health_check_with_leo()
                
                # Log critical alerts
                critical_alerts = [alert for alert in health_data['alerts'] 
                                 if any(keyword in alert.lower() for keyword in ['down', 'high', 'excessive'])]
                
                if critical_alerts:
                    print(f"\n🚨 CRITICAL ALERTS:")
                    for alert in critical_alerts:
                        print(f"   - {alert}")
                
                print(f"\n{'='*60}")
                print(f"Next check in {interval} seconds...")
                print(f"{'='*60}\n")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped by user")
            
            # Final cleanup
            self.auto_fix_issues()
            print("✅ Final cleanup completed")

def main():
    monitor = LeoDockMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "watch":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            monitor.continuous_monitoring(interval)
            
        elif command == "fix":
            print("🔧 Running auto-fix only...")
            fixes = monitor.auto_fix_issues()
            if fixes:
                print(f"✅ Applied {len(fixes)} fixes")
                for fix in fixes:
                    print(f"   - {fix}")
            else:
                print("✅ No fixes needed")
                
        elif command == "leo":
            monitor.run_health_check_with_leo()
            
        else:
            print("❌ Unknown command")
            print("Usage: python leodock_monitor.py [watch|fix|leo]")
    else:
        # Single health check
        monitor.check_service_health()
        monitor.auto_fix_issues()

if __name__ == "__main__":
    main()