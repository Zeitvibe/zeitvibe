#!/usr/bin/env python3
"""
ZeitVibe Command Guardian - Enhanced with Git Intelligence
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
BLUE = '\033[94m'
PURPLE = '\033[95m'
RESET = '\033[0m'

DB_PATH = os.path.expanduser("~/zeitvibe_guardian.db")

# Git aliases to watch
GIT_ALIASES = {
    "gs": "git status - Show working tree status",
    "ga": "git add - Stage files for commit",
    "gc": "git commit -m - Commit staged changes with message",
    "gp": "git push - Upload local commits to remote",
    "gl": "git log --oneline --graph - View commit history",
    "gd": "git diff - Show changes not yet staged",
    "gco": "git checkout - Switch branches or restore files",
    "gb": "git branch - List, create, or delete branches",
    "gpl": "git pull - Fetch and merge from remote",
}

# Files/folders that should NEVER be committed
DANGEROUS_FILES = [
    "venv/", ".venv/", "__pycache__/", "*.pyc", ".DS_Store",
    ".env", ".pytest_cache/", "node_modules/", "*.log", "*.db"
]

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

def is_in_git_repo():
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                               capture_output=True, text=True, cwd=os.getcwd())
        return result.returncode == 0
    except:
        return False

def scan_git_projects():
    """Find all git repos in projects directory"""
    projects_base = os.path.expanduser("~/projects")
    if not os.path.exists(projects_base):
        return []
    
    projects = []
    for item in os.listdir(projects_base):
        path = os.path.join(projects_base, item)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, ".git")):
            projects.append(path)
    return projects

def check_git_add(command):
    """Check if 'git add' might include dangerous files"""
    if "git add" not in command:
        return None
    
    # Check if adding everything
    if ". " in command or " -A" in command or " --all" in command:
        return "⚠️ Adding ALL files! Check for venv/__pycache__ before committing."
    
    return None

def check_dangerous_files():
    """Check for dangerous files in current directory"""
    dangerous_found = []
    for pattern in DANGEROUS_FILES:
        if pattern.endswith('/'):
            # Directory check
            if os.path.exists(pattern):
                dangerous_found.append(pattern)
        elif pattern.startswith('*'):
            # Wildcard check (simplified)
            ext = pattern[1:]
            for f in os.listdir('.'):
                if f.endswith(ext):
                    dangerous_found.append(f)
    return dangerous_found[:5]  # Limit to 5

def show_git_tutorial(command):
    """Show mini tutorial for git commands"""
    cmd_parts = command.split()
    if not cmd_parts:
        return None
    
    base_cmd = cmd_parts[0]
    
    # Check aliases
    if base_cmd in GIT_ALIASES:
        return GIT_ALIASES[base_cmd]
    
    # Check full git commands
    if base_cmd == "git" and len(cmd_parts) > 1:
        git_cmd = cmd_parts[1]
        tutorials = {
            "status": "📊 git status - Shows which files are staged, modified, or untracked",
            "add": "📦 git add <file> - Stages files for the next commit",
            "commit": "💾 git commit -m 'message' - Saves staged changes with a message",
            "push": "🚀 git push - Uploads commits to GitHub/remote",
            "pull": "📥 git pull - Downloads and merges remote changes",
            "log": "📜 git log - Shows commit history",
            "diff": "🔍 git diff - Shows changes not yet staged",
            "branch": "🌿 git branch - Lists or creates branches",
            "checkout": "🔄 git checkout <branch> - Switches branches",
        }
        if git_cmd in tutorials:
            return tutorials[git_cmd]
    
    return None

def check_risky_command(command):
    patterns = [
        (r"rm\s+-rf\s+/", "⚠️ DANGEROUS: This could delete your system!"),
        (r"rm\s+-rf\s+~", "⚠️ DANGEROUS: This could delete your home directory!"),
        (r"sudo\s+rm", "⚠️ Sudo + rm: Double-check what you're deleting!"),
        (r"git\s+push\s+--force", "⚠️ Force push can overwrite remote history!"),
        (r"git\s+reset\s+--hard", "⚠️ Hard reset will delete uncommitted changes!"),
    ]
    for pattern, warning in patterns:
        if re.search(pattern, command):
            return warning
    return None

def check_venv_warning(command, venv_status):
    if "pip install" in command and venv_status == "inactive":
        return "pip install outside virtual environment! Packages will install globally."
    return None

def handle_git_outside_repo(command):
    """Handle git commands outside a git repo"""
    cmd_parts = command.split()
    if not cmd_parts:
        return False
    
    base_cmd = cmd_parts[0]
    is_git_alias = base_cmd in GIT_ALIASES
    is_git_cmd = base_cmd == "git" and len(cmd_parts) > 1
    
    if not (is_git_alias or is_git_cmd):
        return False
    
    if is_in_git_repo():
        return False
    
    print(f"\n{YELLOW}⚠️  Not in a git repository!{RESET}")
    projects = scan_git_projects()
    
    if not projects:
        print(f"{YELLOW}   No git projects found in ~/projects{RESET}")
        return False
    
    print(f"\n{CYAN}📁 Your git projects:{RESET}")
    for i, proj in enumerate(projects, 1):
        print(f"   {GREEN}{i}.{RESET} {os.path.basename(proj)}")
    print(f"   {YELLOW}0.{RESET} Cancel")
    
    try:
        choice = input(f"\n{CYAN}Choose project (1-{len(projects)}): {RESET}")
        if choice == "0":
            print(f"{CYAN}   Command cancelled.{RESET}")
            return True  # Block the command
        idx = int(choice) - 1
        if 0 <= idx < len(projects):
            target = projects[idx]
            print(f"{GREEN}✅ Changing to {target}{RESET}")
            # We'll need to change directory and run command
            # This requires shell integration - for now just warn
            print(f"{YELLOW}💡 Run: cd {target} && {command}{RESET}")
            return True  # Block the original command
    except:
        pass
    
    return False

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

    # Show git tutorial if applicable
    tutorial = show_git_tutorial(command)
    if tutorial:
        print(f"\n{PURPLE}📖 Git Tip: {tutorial}{RESET}")

    # Check risky commands
    warning = check_risky_command(command)
    if warning:
        print(f"\n{CYAN}🛡️  ZeitVibe Guardian: {warning}{RESET}")
        print(f"{CYAN}   Command: {command}{RESET}")
        print()
        colored_countdown(3)

    # Check venv warning
    venv_warning = check_venv_warning(command, venv)
    if venv_warning:
        print(f"\n{CYAN}🐍  ZeitVibe Guardian: {venv_warning}{RESET}")
        print(f"{CYAN}   Command: {command}{RESET}")
        print(f"{CYAN}   Current venv status: {venv}{RESET}")
        print()
        colored_countdown(3)

    # Check git add for dangerous files
    git_warning = check_git_add(command)
    if git_warning:
        dangerous = check_dangerous_files()
        if dangerous:
            print(f"\n{YELLOW}{git_warning}{RESET}")
            print(f"{CYAN}   Found: {', '.join(dangerous)}{RESET}")
            print(f"{CYAN}   Add to .gitignore? (y/n): {RESET}", end='')
            choice = input().lower()
            if choice == 'y':
                with open(".gitignore", "a") as f:
                    for item in dangerous:
                        f.write(f"\n{item}")
                print(f"{GREEN}   ✅ Added to .gitignore{RESET}")
            print()

    # Handle git commands outside repo
    if handle_git_outside_repo(command):
        # Command was blocked or redirected
        return

    # Log the command
    log_command(command, cwd, venv)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CYAN}   ✅ Command cancelled.{RESET}")
        sys.exit(1)
