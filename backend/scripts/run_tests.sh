#!/bin/bash
# =====================================================
# PED Majevica 1988 - Test Runner Script
# =====================================================
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh coverage     # Run with coverage report
#   ./run_tests.sh verbose      # Run with verbose output
#   ./run_tests.sh quick        # Run only fast tests
#   ./run_tests.sh api          # Run only API tests
#   ./run_tests.sh frontend     # Run only frontend tests
#   ./run_tests.sh auth         # Run only auth tests
#   ./run_tests.sh admin        # Run only admin tests
#   ./run_tests.sh production   # Run production tests
# =====================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to backend directory
cd "$(dirname "$0")"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PED Majevica 1988 - Test Runner      ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-dev.txt
fi

# Activate virtual environment
source venv/bin/activate

# Install test dependencies if needed
pip install -q pytest pytest-cov pytest-flask 2>/dev/null

# Default test options
TEST_OPTIONS=""
TEST_PATH="tests/"

# Parse arguments
case "$1" in
    coverage)
        echo -e "${YELLOW}Running tests with coverage report...${NC}"
        TEST_OPTIONS="--cov=app --cov-report=term-missing --cov-report=html:htmlcov"
        ;;
    verbose)
        echo -e "${YELLOW}Running tests with verbose output...${NC}"
        TEST_OPTIONS="-v -s"
        ;;
    quick)
        echo -e "${YELLOW}Running only fast tests (excluding slow tests)...${NC}"
        TEST_OPTIONS="-m \"not slow\""
        ;;
    api)
        echo -e "${YELLOW}Running only API tests...${NC}"
        TEST_PATH="tests/test_api.py"
        ;;
    frontend)
        echo -e "${YELLOW}Running only frontend tests...${NC}"
        TEST_PATH="tests/test_routes.py"
        ;;
    auth)
        echo -e "${YELLOW}Running only authentication tests...${NC}"
        TEST_PATH="tests/test_auth.py tests/test_auth_extended.py"
        ;;
    admin)
        echo -e "${YELLOW}Running only admin tests...${NC}"
        TEST_PATH="tests/test_admin.py"
        ;;
    production)
        echo -e "${YELLOW}Running production tests...${NC}"
        TEST_PATH="tests/test_production.py"
        ;;
    all)
        echo -e "${YELLOW}Running all tests...${NC}"
        TEST_PATH="tests/"
        ;;
    help)
        echo -e "${YELLOW}Usage:${NC}"
        echo "  ./run_tests.sh              # Run all tests"
        echo "  ./run_tests.sh coverage     # Run with coverage report"
        echo "  ./run_tests.sh verbose      # Run with verbose output"
        echo "  ./run_tests.sh quick        # Run only fast tests"
        echo "  ./run_tests.sh api          # Run only API tests"
        echo "  ./run_tests.sh frontend     # Run only frontend tests"
        echo "  ./run_tests.sh auth         # Run only auth tests"
        echo "  ./run_tests.sh admin        # Run only admin tests"
        echo "  ./run_tests.sh production   # Run production tests"
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Running all tests...${NC}"
        TEST_PATH="tests/"
        ;;
esac

echo ""
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${BLUE}  Starting Test Suite                   ${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo ""

# Run tests
START_TIME=$(date +%s)

python -m pytest $TEST_OPTIONS $TEST_PATH

EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${BLUE}----------------------------------------${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed!${NC}"
fi

echo -e "${BLUE}Duration: ${DURATION}s${NC}"
echo -e "${BLUE}----------------------------------------${NC}"

# Generate coverage report if coverage was run
if [ "$1" == "coverage" ]; then
    echo ""
    echo -e "${YELLOW}Coverage report generated in htmlcov/ folder${NC}"
    echo -e "${YELLOW}Open with: open htmlcov/index.html${NC}"
fi

exit $EXIT_CODE
