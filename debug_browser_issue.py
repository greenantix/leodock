import psutil
import subprocess
import time
import requests
from datetime import datetime

def monitor_browser_processes():
    """Monitor and log browser process creation"""
    print("🔍 Monitoring browser processes...")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    initial_browsers = []
    
    # Get current browser processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            proc_name = proc.info['name'].lower()
            if any(browser in proc_name for browser in ['browser', 'chrome', 'firefox', 'chromium']):
                browser_info = {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': proc.info['cmdline'][:5] if proc.info['cmdline'] else [],
                    'create_time': proc.info['create_time']
                }
                initial_browsers.append(browser_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    print(f"📊 Initial browser processes: {len(initial_browsers)}")
    for browser in initial_browsers:
        print(f"   - {browser['name']} (PID: {browser['pid']}) - {' '.join(browser['cmdline'][:2])}")
    
    print(f"\n🔍 Monitoring for new browser processes...")
    
    try:
        while True:
            time.sleep(3)  # Check every 3 seconds
            current_browsers = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(browser in proc_name for browser in ['browser', 'chrome', 'firefox', 'chromium']):
                        browser_info = {
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': proc.info['cmdline'][:5] if proc.info['cmdline'] else [],
                            'create_time': proc.info['create_time']
                        }
                        current_browsers.append(browser_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Check for new browsers
            new_browsers = []
            for current in current_browsers:
                is_new = True
                for initial in initial_browsers:
                    if current['pid'] == initial['pid']:
                        is_new = False
                        break
                if is_new:
                    new_browsers.append(current)
            
            if new_browsers:
                print(f"\n🚨 NEW BROWSER(S) DETECTED! Time: {datetime.now().strftime('%H:%M:%S')}")
                print(f"   Total browsers now: {len(current_browsers)}")
                for browser in new_browsers:
                    cmd_str = ' '.join(browser['cmdline'][:3]) if browser['cmdline'] else 'No command line'
                    create_time = datetime.fromtimestamp(browser['create_time']).strftime('%H:%M:%S')
                    print(f"   NEW: {browser['name']} (PID: {browser['pid']}) - Created: {create_time}")
                    print(f"        Command: {cmd_str}")
                
                # Check if it's LeoDock related
                for browser in new_browsers:
                    cmdline_str = ' '.join(browser['cmdline']) if browser['cmdline'] else ''
                    if any(keyword in cmdline_str.lower() for keyword in ['localhost', '5000', '5001', 'leodock']):
                        print(f"   ⚠️ LeoDock-related browser detected!")
                    else:
                        print(f"   ❓ Non-LeoDock browser - potential multiplication issue!")
                
                initial_browsers = current_browsers  # Update baseline
                
    except KeyboardInterrupt:
        print(f"\n🛑 Browser monitoring stopped at {datetime.now().strftime('%H:%M:%S')}")
        
        # Final report
        final_browsers = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if any(browser in proc.info['name'].lower() 
                      for browser in ['browser', 'chrome', 'firefox', 'chromium']):
                    final_browsers.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print(f"📊 Final browser count: {len(final_browsers)}")

def check_current_browser_situation():
    """Quick check of current browser processes"""
    print("🔍 Current Browser Process Analysis")
    print("=" * 40)
    
    browsers = []
    leodock_browsers = 0
    other_browsers = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            proc_name = proc.info['name'].lower()
            if any(browser in proc_name for browser in ['browser', 'chrome', 'firefox', 'chromium']):
                cmdline_str = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                create_time = datetime.fromtimestamp(proc.info['create_time']).strftime('%H:%M:%S')
                
                browser_info = {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline_str,
                    'create_time': create_time
                }
                browsers.append(browser_info)
                
                if any(keyword in cmdline_str.lower() for keyword in ['localhost', '5000', '5001', 'leodock']):
                    leodock_browsers += 1
                else:
                    other_browsers += 1
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    print(f"📊 Total browsers: {len(browsers)}")
    print(f"🦁 LeoDock-related: {leodock_browsers}")
    print(f"❓ Other browsers: {other_browsers}")
    
    if other_browsers > 2:
        print(f"⚠️ WARNING: {other_browsers} non-LeoDock browsers detected - possible multiplication!")
    
    print(f"\n📋 Browser Process Details:")
    for browser in browsers:
        is_leodock = any(keyword in browser['cmdline'].lower() 
                        for keyword in ['localhost', '5000', '5001', 'leodock'])
        marker = "🦁" if is_leodock else "❓"
        print(f"   {marker} {browser['name']} (PID: {browser['pid']}) - {browser['create_time']}")
        print(f"      {browser['cmdline'][:80]}...")
    
    return {
        'total': len(browsers),
        'leodock': leodock_browsers,
        'other': other_browsers,
        'browsers': browsers
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        # Continuous monitoring mode
        monitor_browser_processes()
    else:
        # Quick analysis mode
        result = check_current_browser_situation()
        
        if result['other'] > 2:
            print(f"\n🚨 ISSUE DETECTED: {result['other']} non-LeoDock browsers running")
            print("   Recommendation: Investigate browser multiplication cause")
        else:
            print(f"\n✅ Browser situation looks normal")
        
        print(f"\n💡 To monitor in real-time, run:")
        print(f"   python debug_browser_issue.py monitor")