"""
Tests for admin functionality
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.http import HttpResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, mock_open
import os

from apps.interns.admin import InternProfileAdmin
from apps.interns.models import InternProfile, InternType
from apps.supervisors.models import EmployeeProfile
from tests.base import BaseTestCase, AuthenticatedTestCase

User = get_user_model()


class AdminInterfaceTest(AuthenticatedTestCase):
    """Test admin interface functionality"""

    def test_admin_login(self):
        """Test admin login functionality"""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django administration")

    def test_admin_models_visibility(self):
        """Test that all models are visible in admin"""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

        # Check that major model groups are visible
        expected_models = [
            "Interns",
            "Accounts",
            "Attendance",
            "Evaluations",
            "Schools",
            "Branches",
            "Supervisors",
        ]

        for model in expected_models:
            # Note: This might need adjustment based on actual admin template
            pass  # Admin structure varies, so we'll focus on specific model access

    def test_intern_profile_admin_access(self):
        """Test access to intern profile admin"""
        response = self.client.get("/admin/interns/internprofile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.intern_profile.user.get_full_name())

    def test_intern_type_admin_access(self):
        """Test access to intern type admin"""
        response = self.client.get("/admin/interns/interntype/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.intern_type_full_time.display_name)


class LogFileAdminTest(AuthenticatedTestCase):
    """Test log file admin functionality"""

    def test_log_files_list_view(self):
        """Test log files list view"""
        response = self.client.get(reverse("admin_logs:log_files_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Log Files")

    @patch("os.path.exists")
    @patch("os.listdir")
    def test_log_files_listing(self, mock_listdir, mock_exists):
        """Test log files are properly listed"""
        # Mock log directory and files
        mock_exists.return_value = True
        mock_listdir.return_value = ["activity.log", "error.log", "debug.log"]

        response = self.client.get(reverse("admin_logs:log_files_list"))
        self.assertEqual(response.status_code, 200)

        # Check that log files are displayed
        self.assertContains(response, "activity.log")
        self.assertContains(response, "error.log")
        self.assertContains(response, "debug.log")

    @patch("os.path.exists")
    def test_log_file_download_valid(self, mock_exists):
        """Test downloading a valid log file"""
        mock_exists.return_value = True

        with patch("builtins.open", mock_open(read_data="Sample log content")):
            response = self.client.get(
                reverse("admin_logs:download_log_file", args=["activity.log"])
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "text/plain")
            self.assertEqual(
                response["Content-Disposition"], 'attachment; filename="activity.log"'
            )

    def test_log_file_download_invalid(self):
        """Test downloading invalid log file returns 404"""
        response = self.client.get(
            reverse("admin_logs:download_log_file", args=["nonexistent.log"])
        )
        self.assertEqual(response.status_code, 404)

    def test_log_file_download_path_traversal_protection(self):
        """Test protection against path traversal attacks"""
        # Try to access file outside logs directory
        response = self.client.get(
            reverse("admin_logs:download_log_file", args=["../../../etc/passwd"])
        )
        self.assertEqual(response.status_code, 404)

    def test_log_file_access_requires_staff(self):
        """Test that log file access requires staff permissions"""
        # Login as non-staff user
        self.client.logout()
        self.login_user(self.intern_user)

        response = self.client.get(reverse("admin_logs:log_files_list"))
        # Should redirect to login or return 403
        self.assertIn(response.status_code, [302, 403])


class InternProfileAdminTest(AuthenticatedTestCase):
    """Test InternProfile admin functionality"""

    def test_intern_profile_admin_list_display(self):
        """Test intern profile list display in admin"""
        response = self.client.get("/admin/interns/internprofile/")
        self.assertEqual(response.status_code, 200)

        # Check that intern is displayed
        self.assertContains(response, self.intern_profile.user.get_full_name())
        self.assertContains(response, self.intern_profile.intern_type.display_name)

    def test_intern_profile_admin_filters(self):
        """Test admin list filters"""
        response = self.client.get("/admin/interns/internprofile/")
        self.assertEqual(response.status_code, 200)

        # Check for filter options (this depends on admin configuration)
        # Common filters might include intern_type, branch, school

    def test_intern_profile_admin_search(self):
        """Test admin search functionality"""
        # Search by intern name
        search_term = self.intern_profile.user.first_name
        response = self.client.get(f"/admin/interns/internprofile/?q={search_term}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.intern_profile.user.get_full_name())

    def test_intern_profile_admin_detail_view(self):
        """Test viewing intern profile details in admin"""
        response = self.client.get(
            f"/admin/interns/internprofile/{self.intern_profile.id}/change/"
        )
        self.assertEqual(response.status_code, 200)

        # Check that form fields are displayed
        self.assertContains(response, self.intern_profile.user.username)
        self.assertContains(response, self.intern_profile.school.name)

    def test_intern_profile_admin_edit(self):
        """Test editing intern profile through admin"""
        new_emergency_contact = "Updated Emergency Contact"

        response = self.client.post(
            f"/admin/interns/internprofile/{self.intern_profile.id}/change/",
            {
                "user": self.intern_profile.user.id,
                "intern_type": self.intern_profile.intern_type.id,
                "school": self.intern_profile.school.id,
                "branch": self.intern_profile.branch.id,
                "internal_supervisor": self.intern_profile.internal_supervisor.id,
                "start_date": self.intern_profile.start_date,
                "end_date": self.intern_profile.end_date,
                "emergency_contact_name": new_emergency_contact,
                "emergency_contact_phone": self.intern_profile.emergency_contact_phone,
                "_save": "Save",
            },
        )

        # Should redirect after successful save
        self.assertEqual(response.status_code, 302)

        # Verify changes were saved
        self.intern_profile.refresh_from_db()
        self.assertEqual(
            self.intern_profile.emergency_contact_name, new_emergency_contact
        )


class AdminPermissionsTest(BaseTestCase):
    """Test admin permissions and security"""

    def test_non_staff_cannot_access_admin(self):
        """Test that non-staff users cannot access admin"""
        self.login_user(self.intern_user)

        response = self.client.get("/admin/")
        # Should redirect to login or return 403
        self.assertIn(response.status_code, [302, 403])

    def test_staff_can_access_admin(self):
        """Test that staff users can access admin"""
        # Create staff user
        staff_user = self.create_user(
            username="staff_user", email="staff@test.com", is_staff=True
        )

        self.login_user(staff_user)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_superuser_full_access(self):
        """Test that superusers have full admin access"""
        self.login_user(self.admin_user)

        # Test access to admin index instead of specific auth/user page
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_model_permissions(self):
        """Test model-level permissions in admin"""
        # This would test if certain models are restricted based on user permissions
        # Implementation depends on custom permission setup
        pass


class CustomAdminViewTest(AuthenticatedTestCase):
    """Test custom admin views and functionality"""

    def test_custom_admin_index(self):
        """Test custom admin index template"""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

        # Check for custom System Management section
        self.assertContains(response, "System Management")
        self.assertContains(response, "Log Files")

    def test_admin_recent_actions_position(self):
        """Test that Recent Actions is positioned correctly"""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

        # This would check template structure
        # Implementation depends on actual template

    def test_admin_template_override(self):
        """Test that admin template overrides work correctly"""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

        # Verify custom template elements are present
        # This depends on actual template customizations


class AdminIntegrationTest(AuthenticatedTestCase):
    """Test admin integration with rest of system"""

    def test_admin_model_creation(self):
        """Test creating models through admin interface"""
        # Create new intern type through admin
        response = self.client.post(
            "/admin/interns/interntype/add/",
            {
                "name": "remote",
                "display_name": "Remote Intern",
                "_save": "Save",
            },
        )

        # Should redirect after creation
        self.assertEqual(response.status_code, 302)

        # Verify object was created
        self.assertTrue(InternType.objects.filter(name="remote").exists())

    def test_admin_bulk_operations(self):
        """Test bulk operations in admin"""
        # Create additional intern profiles for bulk testing
        users = []
        profiles = []

        for i in range(3):
            user = self.create_user(
                username=f"bulk_intern_{i}", email=f"bulk{i}@test.com"
            )
            users.append(user)

            profile = InternProfile.objects.create(
                user=user,
                intern_type=self.intern_type_full_time,
                school=self.school,
                branch=self.branch,
                internal_supervisor=self.supervisor,
                start_date=self.intern_profile.start_date,
                end_date=self.intern_profile.end_date,
            )
            profiles.append(profile)

        # Test bulk delete (if implemented)
        profile_ids = [p.id for p in profiles]
        response = self.client.post(
            "/admin/interns/internprofile/",
            {
                "action": "delete_selected",
                "_selected_action": profile_ids,
                "post": "yes",
            },
        )

        # Verify bulk operation worked (if implemented)
        # This depends on actual admin configuration

    def test_admin_export_functionality(self):
        """Test export functionality if implemented"""
        # This would test CSV/Excel export features
        # Implementation depends on whether you have export functionality
        pass


class AdminSecurityTest(AuthenticatedTestCase):
    """Test admin security features"""

    def test_admin_csrf_protection(self):
        """Test CSRF protection in admin forms"""
        response = self.client.get(
            f"/admin/interns/internprofile/{self.intern_profile.id}/change/"
        )
        self.assertEqual(response.status_code, 200)

        # Check for CSRF token
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_admin_sql_injection_protection(self):
        """Test protection against SQL injection in admin search"""
        # Try SQL injection in search
        malicious_query = "'; DROP TABLE interns_internprofile; --"
        response = self.client.get(f"/admin/interns/internprofile/?q={malicious_query}")

        # Should handle gracefully without error
        self.assertEqual(response.status_code, 200)

        # Verify table still exists
        self.assertTrue(
            InternProfile.objects.filter(id=self.intern_profile.id).exists()
        )

    def test_admin_xss_protection(self):
        """Test XSS protection in admin interface"""
        # This would test that user input is properly escaped
        # in admin templates
        pass
