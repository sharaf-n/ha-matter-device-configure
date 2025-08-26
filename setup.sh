#!/bin/bash

# Matter Configuration Tool Setup Script
# Creates a virtual environment and installs required dependencies

# Note: Don't use 'set -e' when script is meant to be sourced
# as it will exit the parent shell on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        print_error "Please install Python 3.9 or later"
        return 1
    fi

    # Check Python version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    if [ $? -ne 0 ]; then
        print_error "Failed to check Python version"
        return 1
    fi

    print_status "Found Python $python_version"

    # Check if version is 3.9 or later
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
        print_error "Python 3.9 or later is required (found $python_version)"
        return 1
    fi

    return 0
}

# Create virtual environment if it doesn't exist
create_venv() {
    if [ -d ".venv" ]; then
        print_status "Virtual environment already exists at .venv"
        return 0
    else
        print_status "Creating virtual environment at .venv..."
        if python3 -m venv .venv; then
            print_success "Virtual environment created"
            return 0
        else
            print_error "Failed to create virtual environment"
            return 1
        fi
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        print_success "Virtual environment activated"
        return 0
    else
        print_error "Virtual environment activation script not found"
        return 1
    fi
}

# Upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    if python -m pip install --upgrade pip --quiet; then
        print_success "Pip upgraded"
        return 0
    else
        print_warning "Failed to upgrade pip, continuing anyway..."
        return 0  # Don't fail the whole setup for this
    fi
}

# Install required packages
install_dependencies() {
    print_status "Installing required dependencies..."

    # Required packages for matter_config.py
    packages=(
        "python-matter-server"
        "aiohttp"
    )

    local failed_packages=()

    for package in "${packages[@]}"; do
        print_status "Installing $package..."
        if python -m pip install "$package" --quiet; then
            print_success "$package installed successfully"
        else
            print_error "Failed to install $package"
            failed_packages+=("$package")
        fi
    done

    if [ ${#failed_packages[@]} -eq 0 ]; then
        print_success "All dependencies installed"
        return 0
    else
        print_error "Failed to install: ${failed_packages[*]}"
        return 1
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."

    # Test imports
    if python -c "
import sys
try:
    from matter_server.client import MatterClient
    print('✓ python-matter-server imported successfully')
except ImportError as e:
    print(f'✗ Failed to import python-matter-server: {e}')
    sys.exit(1)

try:
    import aiohttp
    print('✓ aiohttp imported successfully')
except ImportError as e:
    print(f'✗ Failed to import aiohttp: {e}')
    sys.exit(1)

print('✓ All dependencies verified')
" 2>/dev/null; then
        print_success "Installation verification passed"
        return 0
    else
        print_error "Installation verification failed"
        return 1
    fi
}

# Check if matter_config.py exists
check_script() {
    if [ ! -f "matter_config.py" ]; then
        print_warning "matter_config.py not found in current directory"
        print_warning "Make sure to download the script to this directory"
    else
        print_success "Found matter_config.py"
    fi
}



# Main setup function
main() {
    echo "=================================================="
    echo "  Matter Configuration Tool Setup"
    echo "=================================================="
    echo

    # Check prerequisites
    if ! check_python; then
        print_error "Python check failed"
        return 1
    fi

    # Setup virtual environment
    if ! create_venv; then
        print_error "Virtual environment creation failed"
        return 1
    fi

    if ! activate_venv; then
        print_error "Virtual environment activation failed"
        return 1
    fi

    # Install dependencies
    upgrade_pip  # This won't fail the setup

    if ! install_dependencies; then
        print_error "Dependency installation failed"
        return 1
    fi

    # Verify everything works
    if ! verify_installation; then
        print_error "Installation verification failed"
        return 1
    fi

    # Check for script
    check_script

    echo
    echo "=================================================="
    print_success "Setup completed successfully!"
    echo "=================================================="
    echo
    echo "Usage:"
    echo "  Run this setup script each time before using the tool:"
    echo "  source ./setup.sh"
    echo
    echo "  Then use the Matter configuration tool:"
    echo "  python matter_config.py 3 1 1030 3 30"
    echo
    print_warning "Note: The virtual environment is activated in this session"
    print_warning "Run 'source ./setup.sh' each time you want to use the tool"

    return 0
}

# Run main function
if ! main "$@"; then
    print_error "Setup failed!"
    print_error "Please check the error messages above and try again"
    return 1 2>/dev/null || exit 1  # Use return if sourced, exit if executed
fi


