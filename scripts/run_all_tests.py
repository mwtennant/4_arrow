#!/usr/bin/env python3
"""Comprehensive test runner for 4th Arrow Tournament Control.

This script runs all tests with proper configuration, reporting, and coverage analysis.
It handles different test categories and provides detailed output for debugging.
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import os


class TestRunner:
    """Manages test execution and reporting."""
    
    def __init__(self, verbose: bool = False, coverage: bool = False, fast: bool = False):
        self.verbose = verbose
        self.coverage = coverage
        self.fast = fast
        self.project_root = Path(__file__).parent
        self.venv_python = self.project_root / "venv" / "bin" / "python"
        
    def run_command(self, cmd: list, description: str) -> tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr.
        
        Args:
            cmd: Command and arguments as list
            description: Human-readable description of the command
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if self.verbose:
            print(f"🔄 {description}")
            print(f"   Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if self.verbose and result.returncode != 0:
                print(f"   ❌ Failed with exit code {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
            elif self.verbose:
                print(f"   ✅ Success")
                
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout after 5 minutes")
            return 124, "", "Command timed out"
        except Exception as e:
            print(f"   💥 Exception: {e}")
            return 1, "", str(e)
    
    def check_environment(self) -> bool:
        """Check that the test environment is properly set up.
        
        Returns:
            True if environment is ready
        """
        print("🔍 Checking test environment...")
        
        # Check virtual environment
        if not self.venv_python.exists():
            print("   ❌ Virtual environment not found. Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
            return False
        
        # Check pytest installation
        exit_code, _, _ = self.run_command([str(self.venv_python), "-m", "pytest", "--version"], "Check pytest")
        if exit_code != 0:
            print("   ❌ pytest not installed in virtual environment")
            return False
        
        # Check database exists
        db_path = self.project_root / "tournament_control.db"
        if not db_path.exists():
            print("   ⚠️  Database file not found - tests will create temporary databases")
        
        print("   ✅ Environment ready")
        return True
    
    def run_role_tests(self) -> dict:
        """Run role terminology refactor tests.
        
        Returns:
            Dict with test results
        """
        print("\n📋 Running Role Terminology Tests...")
        
        role_test_files = [
            "tests/test_role_helpers.py",
            "tests/test_cli_role_flags.py", 
            "tests/test_legacy_shim.py",
            "tests/test_regex_guard.py"
        ]
        
        # Check that all files exist
        missing_files = [f for f in role_test_files if not (self.project_root / f).exists()]
        if missing_files:
            print(f"   ❌ Missing test files: {missing_files}")
            return {"status": "error", "missing_files": missing_files}
        
        cmd = [str(self.venv_python), "-m", "pytest"] + role_test_files
        if self.verbose:
            cmd.append("-v")
        if self.fast:
            cmd.extend(["-x", "--tb=short"])
        if self.coverage:
            cmd.extend(["--cov=core", "--cov=utils", "--cov=src"])
        
        exit_code, stdout, stderr = self.run_command(cmd, "Role terminology tests")
        
        return {
            "status": "pass" if exit_code == 0 else "fail",
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr
        }
    
    def run_core_tests(self) -> dict:
        """Run core functionality tests.
        
        Returns:
            Dict with test results
        """
        print("\n🔧 Running Core Functionality Tests...")
        
        core_test_files = [
            "tests/test_create_user.py",
            "tests/test_migration.py"
        ]
        
        # Check files exist
        existing_files = [f for f in core_test_files if (self.project_root / f).exists()]
        if not existing_files:
            print("   ⚠️  No core test files found")
            return {"status": "skip", "reason": "No test files found"}
        
        cmd = [str(self.venv_python), "-m", "pytest"] + existing_files
        if self.verbose:
            cmd.append("-v")
        if self.fast:
            cmd.extend(["-x", "--tb=short"])
        
        exit_code, stdout, stderr = self.run_command(cmd, "Core functionality tests")
        
        return {
            "status": "pass" if exit_code == 0 else "fail",
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr,
            "files_tested": existing_files
        }
    
    def run_all_available_tests(self) -> dict:
        """Run all available tests in the tests directory.
        
        Returns:
            Dict with test results
        """
        print("\n🧪 Running All Available Tests...")
        
        cmd = [str(self.venv_python), "-m", "pytest", "tests/"]
        if self.verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        if self.fast:
            cmd.extend(["-x", "--tb=short"])
        
        if self.coverage:
            cmd.extend([
                "--cov=core",
                "--cov=src",
                "--cov=utils", 
                "--cov=scripts",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov"
            ])
        
        exit_code, stdout, stderr = self.run_command(cmd, "All available tests")
        
        return {
            "status": "pass" if exit_code == 0 else "fail",
            "exit_code": exit_code,
            "output": stdout,
            "errors": stderr
        }
    
    def generate_report(self, results: dict) -> None:
        """Generate a comprehensive test report.
        
        Args:
            results: Dictionary of test results
        """
        print("\n" + "="*60)
        print("📊 TEST EXECUTION REPORT")
        print("="*60)
        
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Configuration: verbose={self.verbose}, coverage={self.coverage}, fast={self.fast}")
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        
        for test_name, result in results.items():
            print(f"\n📋 {test_name.replace('_', ' ').title()}:")
            
            status = result.get("status", "unknown")
            if status == "pass":
                print("   ✅ PASSED")
                passed_tests += 1
            elif status == "fail":
                print("   ❌ FAILED")
                failed_tests += 1
                if result.get("errors"):
                    print(f"   Error: {result['errors'][:200]}...")
            elif status == "skip":
                print("   ⏭️  SKIPPED")
                skipped_tests += 1
                if result.get("reason"):
                    print(f"   Reason: {result['reason']}")
            else:
                print(f"   ❓ {status.upper()}")
            
            if result.get("exit_code") is not None:
                print(f"   Exit code: {result['exit_code']}")
                
            total_tests += 1
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total test suites: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Skipped: {skipped_tests}")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed_tests} test suite(s) failed")
        
        if self.coverage and "all_tests" in results and results["all_tests"]["status"] == "pass":
            print("\n📈 Coverage report generated in htmlcov/index.html")
    
    def run_tests(self, test_type: str) -> int:
        """Run the specified test type.
        
        Args:
            test_type: Type of tests to run ('role', 'core', 'all')
            
        Returns:
            Exit code (0 for success)
        """
        if not self.check_environment():
            return 1
        
        results = {}
        
        if test_type == "role":
            results["role_tests"] = self.run_role_tests()
        elif test_type == "core":
            results["core_tests"] = self.run_core_tests()
        elif test_type == "all":
            results["all_tests"] = self.run_all_available_tests()
        elif test_type == "comprehensive":
            results["role_tests"] = self.run_role_tests()
            results["core_tests"] = self.run_core_tests()
            # Run full test suite last to get comprehensive coverage
            results["all_tests"] = self.run_all_available_tests()
        
        self.generate_report(results)
        
        # Return non-zero if any tests failed
        failed = any(r.get("status") == "fail" for r in results.values())
        return 1 if failed else 0


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Run tests for 4th Arrow Tournament Control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py                    # Run all tests quietly
  python run_all_tests.py --verbose          # Run with detailed output
  python run_all_tests.py --coverage         # Run with coverage analysis
  python run_all_tests.py --fast             # Stop on first failure
  python run_all_tests.py role --verbose     # Run only role tests
  python run_all_tests.py comprehensive      # Run all test categories
        """
    )
    
    parser.add_argument(
        "test_type",
        choices=["all", "role", "core", "comprehensive"],
        nargs="?",
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output with detailed test information"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true", 
        help="Run with coverage analysis and generate HTML report"
    )
    
    parser.add_argument(
        "-f", "--fast",
        action="store_true",
        help="Fast mode: stop on first failure, short tracebacks"
    )
    
    args = parser.parse_args()
    
    print("🧪 4th Arrow Tournament Control - Test Runner")
    print(f"Running {args.test_type} tests...")
    
    runner = TestRunner(
        verbose=args.verbose,
        coverage=args.coverage,
        fast=args.fast
    )
    
    exit_code = runner.run_tests(args.test_type)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()