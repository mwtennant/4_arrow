"""
Phase User Comprehensive Test Runner

This script runs all Phase User tests and generates a detailed coverage report.
It includes performance benchmarking and test result summaries.
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Test files to run
PHASE_USER_TEST_FILES = [
    "tests/test_phase_user_comprehensive.py",
    "tests/test_phase_user_auth.py",
    "tests/test_phase_user_profile.py",
    "tests/test_phase_user_merge_list.py",
    "tests/test_phase_user_gui.py",
    "tests/test_phase_user_role.py",
]

# Existing test files from the project
EXISTING_TEST_FILES = [
    "tests/test_auth.py",
    "tests/test_cli.py",
    "tests/test_cli_list_users.py",
    "tests/test_cli_merge.py",
    "tests/test_cli_role_flags.py",
    "tests/test_create_user.py",
    "tests/test_csv_export.py",
    "tests/test_legacy_shim.py",
    "tests/test_list_users.py",
    "tests/test_list_users_enhanced.py",
    "tests/test_merge_profiles.py",
    "tests/test_migration.py",
    "tests/test_models.py",
    "tests/test_profile.py",
    "tests/test_regex_guard.py",
    "tests/test_role_helpers.py",
    "tests/gui/test_gui_routes.py",
    "tests/gui/test_gui_forms.py",
]


class TestRunner:
    """Comprehensive test runner for Phase User functionality."""
    
    def __init__(self, verbose=False, coverage=True, markers=None, parallel=False):
        self.verbose = verbose
        self.coverage = coverage
        self.markers = markers
        self.parallel = parallel
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self):
        """Run all Phase User tests."""
        self.start_time = time.time()
        
        print("\n" + "="*70)
        print("PHASE 1 COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Coverage: {'Enabled' if self.coverage else 'Disabled'}")
        print(f"Parallel: {'Enabled' if self.parallel else 'Disabled'}")
        if self.markers:
            print(f"Markers: {self.markers}")
        print("="*70 + "\n")
        
        # Prepare pytest command
        cmd = ["pytest"]
        
        if self.verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        if self.coverage:
            cmd.extend([
                "--cov=core",
                "--cov=src",
                "--cov=main",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-report=json",
            ])
        
        if self.markers:
            cmd.extend(["-m", self.markers])
        
        if self.parallel:
            cmd.extend(["-n", "auto"])
        
        # Add all test files
        all_test_files = []
        
        # Add new comprehensive test files
        for test_file in PHASE_USER_TEST_FILES:
            if Path(test_file).exists():
                all_test_files.append(test_file)
            else:
                print(f"Warning: Test file not found: {test_file}")
        
        # Add existing test files
        for test_file in EXISTING_TEST_FILES:
            if Path(test_file).exists():
                all_test_files.append(test_file)
        
        if not all_test_files:
            print("Error: No test files found!")
            return False
        
        cmd.extend(all_test_files)
        
        # Run tests
        print(f"Running {len(all_test_files)} test files...\n")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        self.end_time = time.time()
        
        # Process results
        self._process_results(result)
        
        # Print summary
        self._print_summary()
        
        return result.returncode == 0
    
    def run_specific_phase(self, phase):
        """Run tests for a specific phase."""
        phase_mapping = {
            "1a": ["test_auth.py", "test_phase_user_auth.py"],
            "1b": ["test_profile.py", "test_phase_user_profile.py"],
            "1c": ["test_create_user.py"],
            "1d": ["test_merge_profiles.py", "test_phase_user_merge_list.py"],
            "1e": ["test_list_users.py", "test_phase_user_merge_list.py"],
            "1f": ["test_gui.py", "test_phase_user_gui.py"],
            "1h": ["test_cli_merge.py", "test_phase_user_merge_list.py"],
            "1i": ["test_list_users_enhanced.py"],
            "1j": ["test_role_helpers.py", "test_phase_user_role.py"],
        }
        
        test_files = phase_mapping.get(phase.lower(), [])
        if not test_files:
            print(f"Error: Unknown phase '{phase}'")
            return False
        
        print(f"\nRunning tests for Phase {phase.upper()}...")
        
        cmd = ["pytest", "-v"]
        if self.coverage:
            cmd.extend(["--cov=core", "--cov=src", "--cov-report=term"])
        
        # Find existing test files
        existing_files = []
        for test_file in test_files:
            for base_path in ["tests/", ""]:
                full_path = Path(base_path + test_file)
                if full_path.exists():
                    existing_files.append(str(full_path))
                    break
        
        if not existing_files:
            print(f"No test files found for phase {phase}")
            return False
        
        cmd.extend(existing_files)
        
        result = subprocess.run(cmd)
        return result.returncode == 0
    
    def run_performance_tests(self):
        """Run performance benchmarks for Phase User functionality."""
        print("\n" + "="*70)
        print("PERFORMANCE BENCHMARKS")
        print("="*70 + "\n")
        
        benchmarks = {
            "User Creation": "tests.benchmark_user_creation",
            "Profile Query": "tests.benchmark_profile_query",
            "User Listing": "tests.benchmark_user_listing",
            "Profile Merge": "tests.benchmark_profile_merge",
        }
        
        for name, module in benchmarks.items():
            print(f"Running {name} benchmark...")
            cmd = ["pytest", "-v", f"tests/benchmarks/{module}.py::test_performance"]
            
            start = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = time.time() - start
            
            if result.returncode == 0:
                print(f"✓ {name}: {duration:.2f}s")
            else:
                print(f"✗ {name}: Failed")
    
    def _process_results(self, result):
        """Process test results."""
        output = result.stdout + result.stderr
        
        # Extract test statistics
        import re
        
        # Find test summary
        summary_match = re.search(
            r"(\d+) passed|(\d+) failed|(\d+) skipped|(\d+) error",
            output
        )
        
        if summary_match:
            self.results["passed"] = int(summary_match.group(1) or 0)
            self.results["failed"] = int(summary_match.group(2) or 0)
            self.results["skipped"] = int(summary_match.group(3) or 0)
            self.results["errors"] = int(summary_match.group(4) or 0)
        
        # Extract coverage
        if self.coverage:
            coverage_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
            if coverage_match:
                self.results["coverage"] = int(coverage_match.group(1))
        
        # Store full output
        self.results["output"] = output
    
    def _print_summary(self):
        """Print test run summary."""
        duration = self.end_time - self.start_time
        
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        # Test results
        total_tests = sum([
            self.results.get("passed", 0),
            self.results.get("failed", 0),
            self.results.get("skipped", 0),
            self.results.get("errors", 0),
        ])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed:      {self.results.get('passed', 0)} ✓")
        print(f"Failed:      {self.results.get('failed', 0)} ✗")
        print(f"Skipped:     {self.results.get('skipped', 0)} ⚠")
        print(f"Errors:      {self.results.get('errors', 0)} ⚠")
        
        # Coverage
        if self.coverage and "coverage" in self.results:
            print(f"\nCoverage:    {self.results['coverage']}%")
            
            # Coverage threshold check
            threshold = 85
            if self.results['coverage'] >= threshold:
                print(f"             ✓ Meets {threshold}% threshold")
            else:
                print(f"             ✗ Below {threshold}% threshold")
        
        # Duration
        print(f"\nDuration:    {duration:.2f} seconds")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Overall result
        print("\n" + "="*70)
        if self.results.get("failed", 0) == 0 and self.results.get("errors", 0) == 0:
            print("RESULT: ALL TESTS PASSED ✓")
        else:
            print("RESULT: TESTS FAILED ✗")
        print("="*70 + "\n")
        
        # Coverage report location
        if self.coverage:
            print("Coverage reports generated:")
            print("  - HTML: htmlcov/index.html")
            print("  - JSON: coverage.json")
            print("")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Phase User comprehensive test suite"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    
    parser.add_argument(
        "-m", "--markers",
        help="Run tests matching given mark expression"
    )
    
    parser.add_argument(
        "-p", "--phase",
        help="Run tests for specific phase (e.g., 1a, 1b, 1c)"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance benchmarks"
    )
    
    parser.add_argument(
        "--create-missing",
        action="store_true",
        help="Create missing test files"
    )
    
    args = parser.parse_args()
    
    # Create missing test files if requested
    if args.create_missing:
        for test_file in PHASE_USER_TEST_FILES:
            path = Path(test_file)
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f'"""Tests for {path.stem}"""\n\nimport pytest\n\n\n')
                print(f"Created: {test_file}")
    
    # Initialize runner
    runner = TestRunner(
        verbose=args.verbose,
        coverage=not args.no_coverage,
        markers=args.markers,
        parallel=args.parallel
    )
    
    # Run tests
    if args.phase:
        success = runner.run_specific_phase(args.phase)
    elif args.performance:
        runner.run_performance_tests()
        success = True
    else:
        success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
