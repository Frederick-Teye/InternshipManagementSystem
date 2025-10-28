"""
Test configuration and utilities
"""

from django.test.runner import DiscoverRunner
from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.test.utils import setup_test_environment, teardown_test_environment
import logging


class CustomTestRunner(DiscoverRunner):
    """Custom test runner with additional setup"""

    def setup_test_environment(self, **kwargs):
        """Set up test environment"""
        super().setup_test_environment(**kwargs)

        # Disable logging during tests to reduce noise
        logging.disable(logging.CRITICAL)

        # Additional test-specific settings
        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        settings.CELERY_TASK_ALWAYS_EAGER = True

    def teardown_test_environment(self, **kwargs):
        """Clean up test environment"""
        super().teardown_test_environment(**kwargs)

        # Re-enable logging
        logging.disable(logging.NOTSET)


def run_specific_tests():
    """Helper function to run specific test categories"""
    test_categories = {
        "models": "tests.test_models",
        "views": "tests.test_views",
        "forms": "tests.test_forms",
        "admin": "tests.test_admin",
        "integration": "tests.test_integration",
    }

    return test_categories


def create_test_data():
    """Create minimal test data for manual testing"""
    from django.contrib.auth import get_user_model
    from apps.interns.models import InternType, InternProfile
    from apps.branches.models import Branch
    from apps.schools.models import School
    from apps.supervisors.models import Supervisor
    from datetime import date, timedelta

    User = get_user_model()

    # Create intern types
    intern_types = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("remote", "Remote"),
    ]

    for name, display_name in intern_types:
        InternType.objects.get_or_create(
            name=name, defaults={"display_name": display_name}
        )

    print("Test data created successfully!")


# Test data fixtures for consistent testing
TEST_USER_DATA = {
    "admin": {
        "username": "test_admin",
        "email": "admin@test.com",
        "password": "testpass123",
        "is_staff": True,
        "is_superuser": True,
    },
    "supervisor": {
        "username": "test_supervisor",
        "email": "supervisor@test.com",
        "password": "testpass123",
    },
    "intern": {
        "username": "test_intern",
        "email": "intern@test.com",
        "password": "testpass123",
    },
}

TEST_INTERN_TYPES = [
    {"name": "full_time", "display_name": "Full Time"},
    {"name": "part_time", "display_name": "Part Time"},
    {"name": "remote", "display_name": "Remote"},
]
