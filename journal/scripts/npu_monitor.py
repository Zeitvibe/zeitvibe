#!/usr/bin/env python3
"""
ZeitVibe NPU Monitor - Shows only NPU-related activity
"""

import os
import subprocess
import time
from datetime import datetime

CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def get_npu_messages():
    """Get NPU-specific kernel messages only"""
    try:
        # Use dmesg with grep to filter only NPU lines
        result = subprocess.run(['dmesg', '|', 'grep', '-i', 'npu'], 
                               capture_output=True, text=True, shell=True)
        if result.stdout:
            lines = [l for l in result.stdout.strip().split('\n') if 'npu' in l.lower()]
            return lines[-5:] if len(lines) > 5 else lines
        return []
    except:
        return []

def monitor_npu():
    print(f"\n{CYAN}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║              ZEITVIBE NPU MONITOR                         ║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════════════════════════╝{RESET}")
    print(f"\n{CYAN}Press Ctrl+C to stop{RESET}\n")
    
    try:
        while True:
            os.system('clear')
            
            print(f"{CYAN}════════════════════════════════════════════════════════════{RESET}")
            print(f"{CYAN}NPU STATUS - {datetime.now().strftime('%H:%M:%S')}{RESET}")
            print(f"{CYAN}════════════════════════════════════════════════════════════{RESET}")
            
            # Check NPU driver
            result = subprocess.run(['lsmod'], capture_output=True, text=True)
            driver_status = "✅ LOADED" if "galcore" in result.stdout else "❌ NOT LOADED"
            driver_color = GREEN if "✅" in driver_status else RED
            print(f"{driver_color}Driver: {driver_status}{RESET}")
            
            # Check NPU device
            device_status = "✅ PRESENT" if os.path.exists('/dev/galcore') else "❌ MISSING"
            device_color = GREEN if "✅" in device_status else RED
            print(f"{device_color}Device: {device_status}{RESET}")
            
            # Get NPU version
            result = subprocess.run(['dmesg', '|', 'grep', 'npu_version'], 
                                   capture_output=True, text=True, shell=True)
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if 'npu_version' in line:
                        print(f"{YELLOW}Version: {line.strip()}{RESET}")
                        break
            
            # Show recent NPU messages
            npu_msgs = get_npu_messages()
            # Filter out non-NPU lines
            npu_msgs = [msg for msg in npu_msgs if 'npu' in msg.lower()]
            
            if npu_msgs:
                print(f"\n{CYAN}Recent NPU Activity:{RESET}")
                for msg in npu_msgs:
                    if 'version' in msg.lower():
                        print(f"  {GREEN}{msg}{RESET}")
                    elif 'error' in msg.lower() or 'fail' in msg.lower():
                        print(f"  {RED}{msg}{RESET}")
                    else:
                        print(f"  {YELLOW}{msg}{RESET}")
            else:
                print(f"\n{YELLOW}No NPU activity detected{RESET}")
            
            print(f"\n{CYAN}Press Ctrl+C to exit | Updates every 2 seconds{RESET}")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print(f"\n{CYAN}✅ Monitoring stopped{RESET}")

if __name__ == "__main__":
    monitor_npu()
