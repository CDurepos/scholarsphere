#!/usr/bin/env python3
"""
ScholarSphere Database Backup Demonstration Script

This script demonstrates the MySQL database backup feature by:
1. Showing how to use the backup script
2. Creating a test backup
3. Verifying the backup file was created
4. Displaying backup information
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{'=' * 50}{Colors.NC}")
    print(f"{Colors.BLUE}{text:^50}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.NC}\n")

def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")

def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")

def print_info(text):
    """Print an info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.NC}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")

def get_project_root():
    """Get the project root directory."""
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent

def check_backup_script():
    """Check if the backup script exists and is executable."""
    project_root = get_project_root()
    backup_script = project_root / "bin" / "backup.sh"
    
    if not backup_script.exists():
        print_error(f"Backup script not found: {backup_script}")
        return False
    
    # Make script executable if it isn't already
    if not os.access(backup_script, os.X_OK):
        print_info(f"Making backup script executable...")
        os.chmod(backup_script, 0o755)
        print_success("Backup script is now executable")
    
    return True

def check_env_file():
    """Check if .env file exists."""
    project_root = get_project_root()
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print_warning(".env file not found. Backup may fail if database credentials are not set.")
        return False
    
    print_success(f".env file found: {env_file}")
    return True

def run_backup():
    """Run the backup script."""
    project_root = get_project_root()
    backup_script = project_root / "bin" / "backup.sh"
    
    print_info("Running backup script...")
    print(f"{Colors.CYAN}Command: {backup_script}{Colors.NC}\n")
    
    try:
        # Run the backup script
        result = subprocess.run(
            [str(backup_script)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Backup script failed with exit code {e.returncode}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        print_error("Backup script not found or not executable")
        return False

def find_backup_files():
    """Find all backup files in the backups directory."""
    project_root = get_project_root()
    backup_dir = project_root / "backups"
    
    if not backup_dir.exists():
        return []
    
    backup_files = sorted(
        backup_dir.glob("scholarsphere_backup_*.sql"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    return backup_files

def display_backup_info():
    """Display information about backup files."""
    backup_files = find_backup_files()
    
    if not backup_files:
        print_warning("No backup files found in backups directory")
        return
    
    print_header("Backup Files")
    
    for i, backup_file in enumerate(backup_files[:5], 1):
        file_size = backup_file.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        mod_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        print(f"{Colors.CYAN}{i}. {backup_file.name}{Colors.NC}")
        print(f"   Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
        print(f"   Created: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Path: {backup_file}")
        print()

def verify_latest_backup():
    """Verify the latest backup file."""
    backup_files = find_backup_files()
    
    if not backup_files:
        print_error("No backup files found to verify")
        return False
    
    latest_backup = backup_files[0]
    
    print_header("Verifying Latest Backup")
    print_info(f"Checking: {latest_backup.name}")
    
    # Check if file exists and has content
    if not latest_backup.exists():
        print_error("Backup file does not exist")
        return False
    
    file_size = latest_backup.stat().st_size
    if file_size == 0:
        print_error("Backup file is empty")
        return False
    
    # Check if it's a valid SQL file
    try:
        with open(latest_backup, 'r', encoding='utf-8') as f:
            first_lines = ''.join(f.readlines()[:10])
            if 'CREATE' in first_lines.upper() or '--' in first_lines or 'DROP' in first_lines.upper():
                print_success("Backup file appears to be valid SQL")
                return True
            else:
                print_warning("Backup file may not be valid SQL")
                return False
    except Exception as e:
        print_error(f"Error reading backup file: {e}")
        return False

def show_usage_examples():
    """Show usage examples for the backup script."""
    print_header("Backup Script Usage Examples")
    
    examples = [
        ("Basic backup (uses defaults)", "./bin/backup.sh"),
        ("Custom database name", "./bin/backup.sh -d my_database"),
        ("Custom output directory", "./bin/backup.sh -o /path/to/backups"),
        ("Full custom options", "./bin/backup.sh -d scholarsphere -o ./my_backups"),
        ("Show help", "./bin/backup.sh -h"),
    ]
    
    for desc, cmd in examples:
        print(f"{Colors.CYAN}{desc}:{Colors.NC}")
        print(f"  {Colors.YELLOW}{cmd}{Colors.NC}\n")

def main():
    """Main demonstration function."""
    print_header("ScholarSphere Database Backup Demonstration")
    
    print_info("This script demonstrates the MySQL database backup feature")
    print()
    
    print_header("Checking Prerequisites")
    
    if not check_backup_script():
        sys.exit(1)
    
    check_env_file()
    
    show_usage_examples()
    
    print_header("Creating Database Backup")
    
    if not run_backup():
        print_error("Failed to create backup")
        sys.exit(1)

    print_header("Verifying Backup")
    
    if verify_latest_backup():
        print_success("Backup verification passed!")
    else:
        print_warning("Backup verification had issues")

    display_backup_info()

    print_header("Demonstration Complete")
    print_success("Backup feature demonstration completed successfully!")
    print()
    print_info("To restore a backup, use:")
    print(f"  {Colors.YELLOW}mysql -u <user> -p <database> < backups/<backup_file>.sql{Colors.NC}")
    print()
    print_info("To schedule automatic backups, add to crontab:")
    print(f"  {Colors.YELLOW}0 2 * * * /path/to/scholarsphere/bin/backup.sh{Colors.NC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demonstration interrupted by user{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
