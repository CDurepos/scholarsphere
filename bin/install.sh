#!/bin/bash

# ScholarSphere Installation Script
# This script installs all required dependencies and sets up the development environment

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

# Install MySQL
install_mysql() {
    echo -e "\n${YELLOW}Checking MySQL installation...${NC}"
    if command_exists mysql; then
        MYSQL_VERSION=$(mysql --version)
        echo -e "${GREEN}MySQL is already installed: $MYSQL_VERSION${NC}"
    else
        echo -e "${YELLOW}MySQL not found. Installing...${NC}"
        if [[ "$OS" == "macos" ]]; then
            if command_exists brew; then
                brew install mysql
                brew services start mysql
            else
                echo -e "${RED}Homebrew not found. Please install Homebrew first:${NC}"
                echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
        elif [[ "$OS" == "linux" ]]; then
            sudo apt-get update
            sudo apt-get install -y mysql-server
            sudo systemctl start mysql
            sudo systemctl enable mysql
        fi
        echo -e "${GREEN}MySQL installed successfully${NC}"
    fi
}

# Install Node.js
install_nodejs() {
    echo -e "\n${YELLOW}Checking Node.js installation...${NC}"
    if command_exists node; then
        NODE_VERSION=$(node --version)
        echo -e "${GREEN}Node.js is already installed: $NODE_VERSION${NC}"
    else
        echo -e "${YELLOW}Node.js not found. Installing...${NC}"
        if [[ "$OS" == "macos" ]]; then
            if command_exists brew; then
                brew install node
            else
                echo -e "${RED}Homebrew not found. Please install Homebrew first.${NC}"
                exit 1
            fi
        elif [[ "$OS" == "linux" ]]; then
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt-get install -y nodejs
        fi
        echo -e "${GREEN}Node.js installed successfully${NC}"
    fi
}

# Install Conda
install_conda() {
    echo -e "\n${YELLOW}Checking Conda installation...${NC}"
    if command_exists conda; then
        CONDA_VERSION=$(conda --version)
        echo -e "${GREEN}Conda is already installed: $CONDA_VERSION${NC}"
    else
        echo -e "${YELLOW}Conda not found. Installing Miniconda...${NC}"
        if [[ "$OS" == "macos" ]]; then
            INSTALLER="Miniconda3-latest-MacOSX-x86_64.sh"
        elif [[ "$OS" == "linux" ]]; then
            INSTALLER="Miniconda3-latest-Linux-x86_64.sh"
        fi
        
        DOWNLOAD_URL="https://repo.anaconda.com/miniconda/$INSTALLER"
        INSTALLER_PATH="/tmp/$INSTALLER"
        
        echo "Downloading Miniconda..."
        curl -L "$DOWNLOAD_URL" -o "$INSTALLER_PATH"
        
        echo "Installing Miniconda..."
        bash "$INSTALLER_PATH" -b -p "$HOME/miniconda3"
        
        # Initialize conda for bash
        "$HOME/miniconda3/bin/conda" init bash
        
        # Add conda to PATH for current session
        export PATH="$HOME/miniconda3/bin:$PATH"
        source ~/.bashrc
        
        echo -e "${GREEN}Conda installed successfully${NC}"
    fi
    
    # Ensure conda is in PATH
    if ! command_exists conda; then
        if [[ -d "$HOME/miniconda3/bin" ]]; then
            export PATH="$HOME/miniconda3/bin:$PATH"
        elif [[ -d "$HOME/anaconda3/bin" ]]; then
            export PATH="$HOME/anaconda3/bin:$PATH"
        fi
    fi
}

# Setup Conda environment
setup_conda_env() {
    echo -e "\n${YELLOW}Setting up Conda environment...${NC}"
    
    ENV_NAME="scholarsphere"
    
    # Check if environment already exists
    if conda env list | grep -q "^$ENV_NAME "; then
        echo -e "${YELLOW}Conda environment '$ENV_NAME' already exists.${NC}"
        read -p "Do you want to remove and recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            conda env remove -n "$ENV_NAME" -y
        else
            echo -e "${GREEN}Using existing environment${NC}"
            return
        fi
    fi
    
    # Create conda environment with Python 3.11
    echo "Creating conda environment '$ENV_NAME' with Python 3.11..."
    conda create -n "$ENV_NAME" python=3.11 -y
    
    echo -e "${GREEN}Conda environment created successfully${NC}"
}

# Activate conda environment and install dependencies
install_dependencies() {
    echo -e "\n${YELLOW}Installing dependencies...${NC}"
    
    ENV_NAME="scholarsphere"
    
    # Get the conda environment's Python and pip paths
    CONDA_ENV_PATH=$(conda env list | grep "^$ENV_NAME " | awk '{print $2}' 2>/dev/null)
    if [[ -z "$CONDA_ENV_PATH" ]]; then
        echo -e "${RED}Conda environment path not found${NC}"
        exit 1
    fi
    
    CONDA_PYTHON="$CONDA_ENV_PATH/bin/python"
    CONDA_PIP="$CONDA_ENV_PATH/bin/pip"
    
    # Install backend dependencies
    echo -e "\n${YELLOW}Installing backend dependencies...${NC}"
    cd "$PROJECT_ROOT/backend"
    # Use the conda environment's pip directly
    "$CONDA_PIP" install -r requirements.txt
    
    # Install scraping dependencies
    echo -e "\n${YELLOW}Installing scraping dependencies...${NC}"
    cd "$PROJECT_ROOT/scraping"
    # Use the conda environment's pip directly
    "$CONDA_PIP" install -r requirements.txt
    
    # Install frontend dependencies
    echo -e "\n${YELLOW}Installing frontend dependencies...${NC}"
    cd "$PROJECT_ROOT/frontend"
    npm install
    
    cd "$PROJECT_ROOT"
    echo -e "${GREEN}All dependencies installed successfully${NC}"
}

# Check for .env file
check_env_file() {
    echo -e "\n${YELLOW}Checking .env file...${NC}"
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        echo -e "${YELLOW}.env file not found. Creating template...${NC}"
        exit 1;
    fi
}

# Run SQL scripts
run_sql_scripts() {
    echo -e "\n${YELLOW}Setting up the database...${NC}"
    
    # Source .env to get database credentials
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
    fi
    
    DB_USER="${DB_USER:-root}"
    DB_PASS="${DB_PASS:-scholarsphere123}"
    DB_NAME="${DB_NAME:-scholarsphere}"
    
    # Check if MySQL is accessible
    if ! mysql -u "$DB_USER" -p"$DB_PASS" -e "SELECT 1;" >/dev/null 2>&1; then
        echo -e "${RED}Cannot connect to MySQL. Please check your credentials in .env${NC}"
        echo -e "${YELLOW}You may need to set up MySQL root password first${NC}"
        exit 1
    fi
    
    # Run init scripts in order
    echo -e "\n${YELLOW}Running initialization scripts...${NC}"
    INIT_DIR="$PROJECT_ROOT/db/init"
    for script in "$INIT_DIR"/*.sql; do
        if [[ -f "$script" ]]; then
            script_name=$(basename "$script")
            echo "Running $script_name..."
            # First script creates the database, others need to specify it
            if [[ "$script_name" == "000_create_database.sql" ]]; then
                mysql -u "$DB_USER" -p"$DB_PASS" < "$script"
            else
                mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$script"
            fi
            echo -e "${GREEN}✓ $script_name completed${NC}"
        fi
    done
    
    # Run migration scripts in order
    # echo -e "\n${YELLOW}Running migration scripts...${NC}"
    # MIGRATIONS_DIR="$PROJECT_ROOT/db/migrations"
    # for script in "$MIGRATIONS_DIR"/*.sql; do
    #     if [[ -f "$script" ]]; then
    #         script_name=$(basename "$script")
    #         echo "Running $script_name..."
    #         mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$script"
    #         echo -e "${GREEN}✓ $script_name completed${NC}"
    #     fi
    # done
    
    echo -e "${GREEN}All database scripts executed successfully${NC}"
}

# Main installation flow
main() {
    detect_os
    install_mysql
    install_nodejs
    install_conda
    setup_conda_env
    check_env_file
    install_dependencies
    run_sql_scripts
    
    echo -e "\n${GREEN}Installation complete!${NC}"
}

# Run main function
main
