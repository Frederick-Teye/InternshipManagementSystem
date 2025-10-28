"""
Management command to run comprehensive tests with reporting
"""

from django.core.management.base import BaseCommand
from django.test.utils import get_runner
from django.conf import settings
from django.core.management import call_command
import sys
import time


class Command(BaseCommand):
    help = "Run comprehensive tests with detailed reporting"

    def add_arguments(self, parser):
        parser.add_argument(
            "--category",
            type=str,
            choices=["models", "views", "forms", "admin", "integration", "all"],
            default="all",
            help="Test category to run",
        )
        parser.add_argument(
            "--coverage", action="store_true", help="Run tests with coverage reporting"
        )
        parser.add_argument(
            "--verbose", action="store_true", help="Verbose test output"
        )
        parser.add_argument(
            "--fast",
            action="store_true",
            help="Skip integration tests for faster execution",
        )

    def handle(self, *args, **options):
        """Run tests based on specified options"""

        self.stdout.write(
            self.style.SUCCESS("🧪 Starting Internship Management System Tests\n")
        )

        start_time = time.time()

        # Determine which tests to run
        test_labels = self.get_test_labels(options["category"], options["fast"])

        if options["coverage"]:
            self.run_with_coverage(test_labels, options["verbose"])
        else:
            self.run_tests(test_labels, options["verbose"])

        end_time = time.time()
        duration = end_time - start_time

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Tests completed in {duration:.2f} seconds")
        )

    def get_test_labels(self, category, fast=False):
        """Get test labels based on category"""

        test_categories = {
            "models": ["tests.test_models"],
            "views": ["tests.test_views"],
            "forms": ["tests.test_forms"],
            "admin": ["tests.test_admin"],
            "integration": ["tests.test_integration"],
            "all": [
                "tests.test_models",
                "tests.test_views",
                "tests.test_forms",
                "tests.test_admin",
            ],
        }

        if not fast and category == "all":
            test_categories["all"].append("tests.test_integration")

        return test_categories.get(category, ["tests"])

    def run_tests(self, test_labels, verbose=False):
        """Run tests without coverage"""

        self.stdout.write("📋 Running test categories:")
        for label in test_labels:
            self.stdout.write(f"  • {label}")
        self.stdout.write("")

        # Configure test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2 if verbose else 1, interactive=False)

        # Run tests
        failures = test_runner.run_tests(test_labels)

        if failures:
            self.stdout.write(self.style.ERROR(f"❌ {failures} test(s) failed"))
            sys.exit(1)
        else:
            self.stdout.write(self.style.SUCCESS("✅ All tests passed!"))

    def run_with_coverage(self, test_labels, verbose=False):
        """Run tests with coverage reporting"""

        try:
            import coverage
        except ImportError:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Coverage package not installed. Install with: pip install coverage"
                )
            )
            return

        self.stdout.write("📊 Running tests with coverage analysis...\n")

        # Start coverage
        cov = coverage.Coverage()
        cov.start()

        try:
            # Run tests
            TestRunner = get_runner(settings)
            test_runner = TestRunner(verbosity=2 if verbose else 1, interactive=False)
            failures = test_runner.run_tests(test_labels)

            # Stop coverage and generate report
            cov.stop()
            cov.save()

            self.stdout.write("\n📈 Coverage Report:")
            self.stdout.write("-" * 50)
            cov.report()

            # Generate HTML report
            cov.html_report(directory="htmlcov")
            self.stdout.write(
                self.style.SUCCESS(
                    "\n📄 HTML coverage report generated in htmlcov/ directory"
                )
            )

            if failures:
                self.stdout.write(self.style.ERROR(f"❌ {failures} test(s) failed"))
                sys.exit(1)
            else:
                self.stdout.write(
                    self.style.SUCCESS("✅ All tests passed with coverage analysis!")
                )

        except Exception as e:
            cov.stop()
            self.stdout.write(self.style.ERROR(f"❌ Error running coverage: {e}"))

    def print_test_summary(self):
        """Print a summary of available tests"""

        self.stdout.write(self.style.SUCCESS("📚 Available Test Categories:\n"))

        categories = {
            "models": "Model validation, relationships, and constraints",
            "views": "View permissions, responses, and business logic",
            "forms": "Form validation, cleaning, and error handling",
            "admin": "Admin interface, permissions, and custom functionality",
            "integration": "End-to-end workflows and system integration",
        }

        for category, description in categories.items():
            self.stdout.write(f"  🔹 {category}: {description}")

        self.stdout.write("\n💡 Usage Examples:")
        self.stdout.write("  python manage.py run_tests --category models")
        self.stdout.write("  python manage.py run_tests --coverage")
        self.stdout.write("  python manage.py run_tests --fast --verbose")
        self.stdout.write("")


# Additional test utilities
def run_quick_tests():
    """Run a quick subset of tests for development"""
    call_command("run_tests", category="models", fast=True)


def run_full_test_suite():
    """Run complete test suite with coverage"""
    call_command("run_tests", coverage=True, verbose=True)
