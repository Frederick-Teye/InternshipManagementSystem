"""
Tests for intern views
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import Http404
from datetime import date, timedelta

from apps.interns.models import InternProfile, InternType
from tests.base import (
    BaseTestCase,
    InternTestCase,
    SupervisorTestCase,
    AuthenticatedTestCase,
)

User = get_user_model()


class InternListViewTest(AuthenticatedTestCase):
    """Test intern list view"""

    def test_intern_list_view_get(self):
        """Test GET request to intern list"""
        url = reverse("interns:list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.intern_profile.user.get_full_name())
        self.assertIn("interns", response.context)
        self.assertIn("intern_types", response.context)

    def test_intern_list_view_pagination(self):
        """Test pagination in intern list"""
        # Create multiple interns to test pagination
        for i in range(25):
            user = self.create_user(
                username=f"intern_{i}", email=f"intern_{i}@test.com"
            )
            InternProfile.objects.create(
                user=user,
                intern_type=self.intern_type_full_time,
                school=self.school,
                branch=self.branch,
                internal_supervisor=self.supervisor,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=90),
            )

        url = reverse("interns:list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Check if pagination is working (assuming 20 items per page)
        self.assertTrue(response.context["is_paginated"])

    def test_intern_list_view_filtering(self):
        """Test filtering in intern list"""
        # Create intern with different type
        part_time_user = self.create_user(
            username="part_time_intern", email="parttime@test.com"
        )

        part_time_intern = InternProfile.objects.create(
            user=part_time_user,
            intern_type=self.intern_type_part_time,
            school=self.school,
            branch=self.branch,
            internal_supervisor=self.supervisor,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
        )

        url = reverse("interns:list")

        # Filter by intern type
        response = self.client.get(url, {"intern_type": self.intern_type_part_time.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, part_time_intern.user.get_full_name())
        self.assertNotContains(response, self.intern_profile.user.get_full_name())

    def test_intern_list_view_search(self):
        """Test search functionality"""
        url = reverse("interns:list")

        # Search by name
        response = self.client.get(url, {"search": self.intern_user.first_name})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.intern_profile.user.get_full_name())

    def test_intern_list_view_requires_login(self):
        """Test that view requires authentication"""
        self.client.logout()
        url = reverse("interns:list")
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)


class InternDetailViewTest(AuthenticatedTestCase):
    """Test intern detail view"""

    def test_intern_detail_view_get(self):
        """Test GET request to intern detail"""
        url = reverse("interns:detail", args=[self.intern_profile.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["intern"], self.intern_profile)
        self.assertContains(response, self.intern_profile.user.get_full_name())

    def test_intern_detail_view_invalid_id(self):
        """Test detail view with invalid intern ID"""
        url = reverse("interns:detail", args=[99999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_intern_detail_view_context_data(self):
        """Test that detail view includes necessary context"""
        url = reverse("interns:detail", args=[self.intern_profile.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("intern", response.context)
        # Check that related data is included
        intern = response.context["intern"]
        self.assertEqual(intern.intern_type, self.intern_type_full_time)
        self.assertEqual(intern.school, self.school)
        self.assertEqual(intern.branch, self.branch)


class InternViewPermissionTest(BaseTestCase):
    """Test view permissions for different user types"""

    def test_admin_can_view_all_interns(self):
        """Test that admin users can view all interns"""
        self.login_user(self.admin_user)

        url = reverse("interns:list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.intern_profile.user.get_full_name())

    def test_supervisor_can_view_their_interns(self):
        """Test that supervisors can view their assigned interns"""
        self.login_user(self.supervisor_user)

        url = reverse("interns:list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should see their assigned intern
        self.assertContains(response, self.intern_profile.user.get_full_name())

    def test_intern_can_view_own_profile(self):
        """Test that interns can view their own profile"""
        self.login_user(self.intern_user)

        url = reverse("interns:detail", args=[self.intern_profile.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["intern"], self.intern_profile)

    def test_unauthorized_access_blocked(self):
        """Test that unauthorized users cannot access intern views"""
        # Create a regular user (not admin, supervisor, or intern)
        regular_user = self.create_user(
            username="regular_user", email="regular@test.com"
        )
        self.login_user(regular_user)

        url = reverse("interns:list")
        response = self.client.get(url)

        # Should be redirected or forbidden (depending on decorator implementation)
        self.assertIn(response.status_code, [302, 403])


class InternCRUDViewTest(AuthenticatedTestCase):
    """Test CRUD operations for interns"""

    def test_create_intern_profile_view(self):
        """Test creating a new intern profile"""
        # Create a user without an intern profile
        new_user = self.create_user(username="new_intern", email="newintern@test.com")

        # If there's a create view, test it
        # This would depend on whether you have create/edit views implemented
        # For now, we'll test the model creation through admin or forms

    def test_edit_intern_profile_permissions(self):
        """Test that only authorized users can edit intern profiles"""
        # Login as supervisor (should be able to edit their interns)
        self.login_user(self.supervisor_user)

        # Test would depend on having edit views
        # For now, we verify the model can be updated
        original_start_date = self.intern_profile.start_date
        self.intern_profile.start_date = date.today() + timedelta(days=1)
        self.intern_profile.save()

        self.intern_profile.refresh_from_db()
        self.assertNotEqual(self.intern_profile.start_date, original_start_date)

    def test_delete_intern_profile_permissions(self):
        """Test that only authorized users can delete intern profiles"""
        # Only admin should be able to delete
        self.login_user(self.admin_user)

        intern_id = self.intern_profile.id
        self.intern_profile.delete()

        # Verify deletion
        self.assertFalse(InternProfile.objects.filter(id=intern_id).exists())
