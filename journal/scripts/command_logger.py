#!/usr/bin/env python3
"""
ZeitVibe Command Guardian
"""

import os
import sys
import sqlite3
from datetime import datetime
import re
import time
import subprocess

CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

DB_PATH = os.path.expanduser("~/zeitvibe_guardian.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            cwd TEXT,
            venv TEXT,
            npu_status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_npu_status():
    try:
        result = subprocess.run(['lsmod'], capture_output=True, text=True)
        driver = "loaded" if "galcore" in result.stdout else "not_loaded"
        device = "present" if os.path.exists('/dev/galcore') else "missing"
        return f"driver:{driver}|device:{device}"
    except:
        return "driver:unknown|device:unknown"

def get_venv_status():
    if "VIRTUAL_ENV" in os.environ:
        return "active"
    return "inactive"

def clean_command(command):
    lines = command.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            return line
    return command.strip()

def check_risky_command(command):
    patterns = [
        (r"rm\s+-rf\s+/", "⚠️ DANGEROUS: This could delete your system!"),
        (r"rm\s+-rf\s+~", "⚠️ DANGEROUS: This could delete your home directory!"),
        (r"sudo\s+rm", "⚠️ Sudo + rm: Double-check what you're deleting!"),
    ]
    for pattern, warning in patterns:
        if re.search(pattern, command):
            return warning
    return None

def check_venv_warning(command, venv_status):
    if "pip install" in command and venv_status == "inactive":
        return "pip install outside virtual environment! Packages will install globally."
    return None

def log_command(command, cwd, venv):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    npu = get_npu_status()
    cursor.execute('''
        INSERT INTO commands (command, cwd, venv, npu_status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (command, cwd, venv, npu, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def colored_countdown(seconds):
    for i in range(seconds, 0, -1):
        if i == 3:
            color = GREEN
        elif i == 2:
            color = YELLOW
        else:
            color = RED
        print(f"\r{CYAN}   {color}{i}...{RESET}", end='', flush=True)
        time.sleep(2)
    print(f"\r{CYAN}   Continuing...{RESET}")

def main():
    if len(sys.argv) < 2:
        return

    raw_command = " ".join(sys.argv[1:])
    command = clean_command(raw_command)

    if not command:
        return

    cwd = os.getcwd()
    venv = get_venv_status()

    init_db()

    warning = check_risky_command(command)
    if warning:
        print(f"\n{CYAN}🛡️  ZeitVibe Guardian: {warning}{RESET}")
        print(f"{CYAN}   Command: {command}{RESET}")
        print()
        colored_countdown(3)

    venv_warning = check_venv_warning(command, venv)
    if venv_warning:
        print(f"\n{CYAN}🐍  ZeitVibe Guardian: {venv_warning}{RESET}")
        print(f"{CYAN}   Command: {command}{RESET}")
        print(f"{CYAN}   Current venv status: {venv}{RESET}")
        print()
        colored_countdown(3)

    log_command(command, cwd, venv)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CYAN}   ✅ Command cancelled.{RESET}")
        sys.exit(1)
