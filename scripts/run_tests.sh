#!/bin/bash

# Comprehensive Test Suite for Internship Management System
# This script runs all test categories with proper reporting

echo "🧪 Starting Internship Management System Test Suite"
echo "=================================================="

# Set test environment
export DJANGO_SETTINGS_MODULE="config.settings"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run tests with timing
run_test_category() {
    local category=$1
    local description=$2
    
    echo ""
    echo -e "${BLUE}🔹 Testing: $description${NC}"
    echo "----------------------------------------"
    
    start_time=$(date +%s)
    
    if docker-compose exec web python manage.py test tests.test_$category --verbosity=1; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo -e "${GREEN}✅ $description tests passed ($duration seconds)${NC}"
        return 0
    else
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo -e "${RED}❌ $description tests failed ($duration seconds)${NC}"
        return 1
    fi
}

# Test categories
total_tests=0
passed_tests=0

# Model Tests
if run_test_category "models" "Model Validation & Relationships"; then
    ((passed_tests++))
fi
((total_tests++))

# View Tests
if run_test_category "views" "View Logic & Permissions"; then
    ((passed_tests++))
fi
((total_tests++))

# Form Tests
if run_test_category "forms" "Form Validation & Processing"; then
    ((passed_tests++))
fi
((total_tests++))

# Admin Tests
if run_test_category "admin" "Admin Interface & Security"; then
    ((passed_tests++))
fi
((total_tests++))

# Integration Tests
if run_test_category "integration" "System Integration & Workflows"; then
    ((passed_tests++))
fi
((total_tests++))

# Summary
echo ""
echo "=================================================="
echo "🏁 Test Suite Summary"
echo "=================================================="
echo -e "Total Test Categories: $total_tests"
echo -e "Passed: ${GREEN}$passed_tests${NC}"
echo -e "Failed: ${RED}$((total_tests - passed_tests))${NC}"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "${GREEN}🎉 All test categories passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check output above.${NC}"
    exit 1
fi