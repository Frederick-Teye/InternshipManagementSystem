"""
Base test classes and utilities for the Internship Management System
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

from apps.accounts.models import User
from apps.interns.models import InternProfile, InternType
from apps.branches.models import Branch
from apps.schools.models import School
from apps.supervisors.models import EmployeeProfile

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup and utilities"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test intern types
        self.intern_type_full_time = InternType.objects.create(
            name="full_time", display_name="Full Time"
        )
        self.intern_type_part_time = InternType.objects.create(
            name="part_time", display_name="Part Time"
        )

        # Create test school
        self.school = School.objects.create(
            name="Test University",
            contact_email="test@university.edu",
            contact_phone="+1234567890",
        )

        # Create test branch
        self.branch = Branch.objects.create(
            name="Engineering Department", code="ENG001"
        )

        # Create test users
        self.admin_user = self.create_user(
            username="admin", email="admin@test.com", is_staff=True, is_superuser=True
        )

        self.supervisor_user = self.create_user(
            username="supervisor1", email="supervisor@test.com"
        )

        self.intern_user = self.create_user(username="intern1", email="intern@test.com")

        # Create test supervisor
        self.supervisor = EmployeeProfile.objects.create(
            user=self.supervisor_user,
            job_title="Senior Developer",
            department="Engineering",
        )

        # Create test intern profile
        self.intern_profile = InternProfile.objects.create(
            user=self.intern_user,
            intern_type=self.intern_type_full_time,
            school=self.school,
            branch=self.branch,
            internal_supervisor=self.supervisor,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
        )

    def create_user(
        self,
        username,
        email,
        password="testpass123",
        first_name=None,
        last_name=None,
        **extra_fields,
    ):
        """Create a test user with profile"""
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name or f"Test {username}",
            last_name=last_name or "User",
            **extra_fields,
        )

        return user

    def login_user(self, user):
        """Login a user for testing"""
        self.client.force_login(user)
        return user

    def assertMessageContains(self, response, message_text):
        """Assert that response contains a specific message"""
        messages = list(response.context.get("messages", []))
        message_texts = [str(msg) for msg in messages]
        self.assertIn(message_text, " ".join(message_texts))


class AuthenticatedTestCase(BaseTestCase):
    """Base test case with authenticated user"""

    def setUp(self):
        super().setUp()
        self.login_user(self.admin_user)


class InternTestCase(BaseTestCase):
    """Base test case for intern-related tests"""

    def setUp(self):
        super().setUp()
        self.login_user(self.intern_user)


class SupervisorTestCase(BaseTestCase):
    """Base test case for supervisor-related tests"""

    def setUp(self):
        super().setUp()
        self.login_user(self.supervisor_user)
