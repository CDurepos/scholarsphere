#!/bin/bash

# ScholarSphere Run Script
# This script starts the backend and frontend development servers

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'        # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    else
        echo -e "${RED}Unsupported OS: $OSTYPE${NC}"
        exit 1
    fi
    echo -e "${GREEN}Detected OS: $OS${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for .env file
check_env_file() {
    echo -e "\n${YELLOW}Checking .env file...${NC}"
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        echo -e "${RED}.env file not found. Please create it first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}.env file found${NC}"
}

# Check conda environment
check_conda_env() {
    echo -e "\n${YELLOW}Checking conda environment...${NC}"
    
    ENV_NAME="scholarsphere"
    
    # Ensure conda is in PATH
    if ! command_exists conda; then
        if [[ -d "$HOME/miniconda3/bin" ]]; then
            export PATH="$HOME/miniconda3/bin:$PATH"
        elif [[ -d "$HOME/anaconda3/bin" ]]; then
            export PATH="$HOME/anaconda3/bin:$PATH"
        else
            echo -e "${RED}Conda not found. Please run bin/install.sh first.${NC}"
            exit 1
        fi
    fi
    
    # Check if environment exists
    if ! conda env list | grep -q "^$ENV_NAME "; then
        echo -e "${RED}Conda environment '$ENV_NAME' not found. Please run bin/install.sh first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Conda environment '$ENV_NAME' found${NC}"
}

# Activate conda environment
activate_conda_env() {
    echo -e "\n${YELLOW}Activating conda environment...${NC}"
    
    ENV_NAME="scholarsphere"
    
    # Initialize conda for bash
    eval "$(conda shell.bash hook)"
    conda activate "$ENV_NAME"
    
    echo -e "${GREEN}Conda environment activated${NC}"
}

# Check MySQL connection
check_mysql() {
    echo -e "\n${YELLOW}Checking MySQL connection...${NC}"
    
    # Source .env to get database credentials
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
    fi
    
    DB_USER="${DB_USER:-root}"
    DB_PASS="${DB_PASS:-scholarsphere123}"
    
    # Check if MySQL is accessible
    if ! mysql -u "$DB_USER" -p"$DB_PASS" -e "SELECT 1;" >/dev/null 2>&1; then
        echo -e "${RED}Cannot connect to MySQL. Please check your credentials in .env${NC}"
        echo -e "${YELLOW}Make sure MySQL is running${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}MySQL connection successful${NC}"
}

# Start backend server
start_backend() {
    echo -e "\n${YELLOW}Starting backend server...${NC}"

    cd "$PROJECT_ROOT/backend"
    echo -e "${GREEN}Backend server starting on http://127.0.0.1:5000${NC}"

    # Use the conda environment's Python directly
    python run.py > /tmp/scholarsphere_backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/scholarsphere_backend.pid
    
    echo -e "${GREEN}Backend server started (PID: $BACKEND_PID)${NC}"
    echo -e "${YELLOW}Backend logs: tail -f /tmp/scholarsphere_backend.log${NC}"
}

# Start frontend server
start_frontend() {
    echo -e "\n${YELLOW}Starting frontend server...${NC}"
    
    cd "$PROJECT_ROOT/frontend"
    
    echo -e "${GREEN}Frontend server starting...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/scholarsphere_frontend.pid
    
    echo -e "${GREEN}Frontend server started (PID: $FRONTEND_PID)${NC}"
}

# Stop servers
stop_servers() {
    echo -e "\n${YELLOW}Stopping servers...${NC}"
    
    if [[ -f /tmp/scholarsphere_backend.pid ]]; then
        BACKEND_PID=$(cat /tmp/scholarsphere_backend.pid)
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            # Kill the process and its process group to handle conda run wrapper
            kill -TERM -"$BACKEND_PID" 2>/dev/null || kill "$BACKEND_PID" 2>/dev/null
            echo -e "${GREEN}Backend server stopped${NC}"
        fi
        rm -f /tmp/scholarsphere_backend.pid
    fi
    
    if [[ -f /tmp/scholarsphere_frontend.pid ]]; then
        FRONTEND_PID=$(cat /tmp/scholarsphere_frontend.pid)
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            kill "$FRONTEND_PID"
            echo -e "${GREEN}Frontend server stopped${NC}"
        fi
        rm -f /tmp/scholarsphere_frontend.pid
    fi
}

# Handle script termination
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    stop_servers
    exit 0
}

trap cleanup SIGINT SIGTERM

# Main run flow
main() {
    echo -e "${GREEN}Starting ScholarSphere...${NC}\n"
    
    detect_os
    check_env_file
    check_conda_env
    activate_conda_env
    check_mysql
    
    # Parse command line arguments
    RUN_BACKEND=true
    RUN_FRONTEND=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                RUN_FRONTEND=false
                shift
                ;;
            --frontend-only)
                RUN_BACKEND=false
                shift
                ;;
            --stop)
                stop_servers
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                echo "Usage: $0 [--backend-only|--frontend-only|--stop]"
                exit 1
                ;;
        esac
    done
    
    if [[ "$RUN_BACKEND" == true ]]; then
        start_backend
    fi
    
    if [[ "$RUN_FRONTEND" == true ]]; then
        start_frontend
    fi
    
    echo -e "\n${GREEN}=== Servers Running ===${NC}"
    if [[ "$RUN_BACKEND" == true ]]; then
        echo -e "${GREEN}Backend: http://127.0.0.1:5000${NC}"
    fi
    if [[ "$RUN_FRONTEND" == true ]]; then
        echo -e "${GREEN}Frontend: Check terminal output for Vite dev server URL${NC}"
    fi
    echo -e "\n${YELLOW}Press Ctrl+C to stop all servers${NC}"
    
    # Wait for user interrupt
    wait
}

# Run main function
main "$@"
