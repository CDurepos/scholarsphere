#!/bin/bash

# ScholarSphere Database Backup Script
# This script creates a MySQL database backup using mysqldump

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Default backup directory
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="scholarsphere"

# Function to print usage
usage() {
    echo -e "${YELLOW}Usage:${NC} $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --database NAME    Database name (default: scholarsphere)"
    echo "  -o, --output DIR       Backup output directory (default: ./backups)"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Example:"
    echo "  $0"
    echo "  $0 -d scholarsphere -o /path/to/backups"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--database)
            DB_NAME="$2"
            shift 2
            ;;
        -o|--output)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Check for .env file
check_env_file() {
    echo -e "\n${YELLOW}Checking .env file...${NC}"
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        echo -e "${RED}.env file not found. Please create it first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}.env file found${NC}"
}

# Load database credentials from .env
load_db_credentials() {
    echo -e "\n${YELLOW}Loading database credentials...${NC}"
    
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
    fi
    
    DB_HOST="${DB_HOST:-127.0.0.1}"
    DB_PORT="${DB_PORT:-3306}"
    DB_USER="${DB_USER:-root}"
    DB_PASS="${DB_PASS:-}"
    
    # Extract username if it contains @ (i.e. "root@localhost" -> "root")
    if [[ "$DB_USER" == *"@"* ]]; then
        DB_USER="${DB_USER%%@*}"
        echo -e "${YELLOW}Note: Extracted username from '${DB_USER}@...' format${NC}"
    fi
    
    if [[ -z "$DB_USER" ]]; then
        echo -e "${RED}DB_USER not set in .env file${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Database credentials loaded${NC}"
    echo -e "${BLUE}  Host: $DB_HOST${NC}"
    echo -e "${BLUE}  Port: $DB_PORT${NC}"
    echo -e "${BLUE}  User: $DB_USER${NC}"
    echo -e "${BLUE}  Database: $DB_NAME${NC}"
}

# Check if mysqldump is available
check_mysqldump() {
    echo -e "\n${YELLOW}Checking for mysqldump...${NC}"
    if ! command -v mysqldump >/dev/null 2>&1; then
        echo -e "${RED}mysqldump not found. Please install MySQL client tools.${NC}"
        exit 1
    fi
    echo -e "${GREEN}mysqldump found${NC}"
}

# Check MySQL connection
check_mysql_connection() {
    echo -e "\n${YELLOW}Checking MySQL connection...${NC}"
    
    # Use MYSQL_PWD environment variable to avoid issues with special characters in password
    if [[ -z "$DB_PASS" ]]; then
        if ! mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -e "SELECT 1;" >/dev/null 2>&1; then
            echo -e "${RED}Cannot connect to MySQL. Please check your credentials in .env${NC}"
            exit 1
        fi
    else
        # Export password as environment variable to handle special characters safely
        export MYSQL_PWD="$DB_PASS"
        if ! mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -e "SELECT 1;" >/dev/null 2>&1; then
            echo -e "${RED}Cannot connect to MySQL. Please check your credentials in .env${NC}"
            unset MYSQL_PWD
            exit 1
        fi
        # Keep MYSQL_PWD set for subsequent commands
    fi
    
    echo -e "${GREEN}MySQL connection successful${NC}"
}

# Check if database exists
check_database_exists() {
    echo -e "\n${YELLOW}Checking if database '$DB_NAME' exists...${NC}"
    
    # MYSQL_PWD should already be set from check_mysql_connection if password exists
    DB_EXISTS=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -e "SHOW DATABASES LIKE '$DB_NAME';" 2>/dev/null | grep -c "$DB_NAME" || true)
    
    if [[ "$DB_EXISTS" -eq 0 ]]; then
        echo -e "${RED}Database '$DB_NAME' does not exist${NC}"
        unset MYSQL_PWD
        exit 1
    fi
    
    echo -e "${GREEN}Database '$DB_NAME' exists${NC}"
}

# Create backup directory
create_backup_dir() {
    echo -e "\n${YELLOW}Creating backup directory...${NC}"
    mkdir -p "$BACKUP_DIR"
    echo -e "${GREEN}Backup directory: $BACKUP_DIR${NC}"
}

# Perform backup
perform_backup() {
    echo -e "\n${YELLOW}Starting database backup...${NC}"
    
    BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql"
    
    echo -e "${BLUE}Backup file: $BACKUP_FILE${NC}"
    
    # MYSQL_PWD should already be set from check_mysql_connection if password exists
    # Use it for mysqldump to avoid issues with special characters
    mysqldump \
        -h "$DB_HOST" \
        -P "$DB_PORT" \
        -u "$DB_USER" \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --add-drop-database \
        --databases "$DB_NAME" \
        > "$BACKUP_FILE"
    
    BACKUP_EXIT_CODE=$?
    
    # Clean up MYSQL_PWD environment variable
    unset MYSQL_PWD
    
    # Check if backup was successful
    if [[ $BACKUP_EXIT_CODE -eq 0 ]] && [[ -f "$BACKUP_FILE" ]] && [[ -s "$BACKUP_FILE" ]]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo -e "\n${GREEN}✓ Backup completed successfully!${NC}"
        echo -e "${GREEN}  File: $BACKUP_FILE${NC}"
        echo -e "${GREEN}  Size: $BACKUP_SIZE${NC}"
        return 0
    else
        echo -e "\n${RED}✗ Backup failed!${NC}"
        if [[ -f "$BACKUP_FILE" ]]; then
            rm -f "$BACKUP_FILE"
        fi
        exit 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  ScholarSphere Database Backup${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    check_env_file
    load_db_credentials
    check_mysqldump
    check_mysql_connection
    check_database_exists
    create_backup_dir
    perform_backup
    
    echo -e "\n${GREEN}Backup process completed!${NC}"
}

# Run main function
main
