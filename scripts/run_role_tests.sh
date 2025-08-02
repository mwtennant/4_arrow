#!/bin/bash
# Quick test runner for role terminology refactor tests
# This script runs all the role-related tests that should pass

set -e  # Exit on any error

echo "🧪 4th Arrow Tournament Control - Role Refactor Test Suite"
echo "=========================================================="

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run: python -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Set Python warnings to show deprecation warnings
export PYTHONWARNINGS="default::DeprecationWarning"

echo ""
echo "🔄 Running Role Helper Tests..."
python -m pytest tests/test_role_helpers.py -v

echo ""
echo "🔄 Running CLI Role Flag Tests..."
python -m pytest tests/test_cli_role_flags.py -v

echo ""
echo "🔄 Running Legacy Shim Tests..."
python -m pytest tests/test_legacy_shim.py -v

echo ""
echo "🔄 Running Migration Script Tests..."
python -m pytest tests/test_migration.py -v

echo ""
echo "🔄 Running Regex Guard Tests..."
python -m pytest tests/test_regex_guard.py -v

echo ""
echo "🔄 Running Updated Create User Tests..."
python -m pytest tests/test_create_user.py -v

echo ""
echo "=========================================================="
echo "🎉 ALL ROLE REFACTOR TESTS COMPLETED SUCCESSFULLY!"
echo ""
echo "✅ Role terminology refactor implementation verified"
echo "✅ Backward compatibility confirmed"
echo "✅ Migration tooling tested"
echo "✅ Legacy usage detection working"
echo ""
echo "📋 Summary of implemented features:"
echo "   • ProfileRole enum with 3 role types"
echo "   • Boolean accessor methods on User model"
echo "   • Deprecated is_member property with warnings"
echo "   • CLI --role flag with --member compatibility"
echo "   • Database migration script with dry-run"
echo "   • JSON import/export legacy shim"
echo "   • Comprehensive test coverage"
echo "   • Regex guards against legacy terminology"
echo ""
echo "🚀 Ready for production deployment!"