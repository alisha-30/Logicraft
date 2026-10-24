"""
LogiCraft Root Integration & Smoke Test Suite
----------------------------------------------
Runs end-to-end integration tests verifying cross-app data integrity,
authentication flows (login, register, logout), and baseline endpoints.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from logistics.models import Warehouse, InventoryItem, Vehicle, Shipment
from transit.models import TransitRoute, TransitSchedule, TicketBooking


class SystemSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_dashboard_endpoint_loads(self):
        """Verify home operations dashboard returns HTTP 200."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LogiCraft")

    def test_inventory_catalog_endpoint_loads(self):
        """Verify inventory catalog page returns HTTP 200."""
        response = self.client.get(reverse('inventory_catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Warehouse Inventory Catalog")

    def test_public_cargo_tracking_endpoint_loads(self):
        """Verify tracking search page returns HTTP 200."""
        response = self.client.get(reverse('track_shipment'))
        self.assertEqual(response.status_code, 200)

    def test_transit_schedules_endpoint_loads(self):
        """Verify transit schedule page returns HTTP 200."""
        response = self.client.get(reverse('transit_schedules'))
        self.assertEqual(response.status_code, 200)

    def test_admin_login_endpoint_loads(self):
        """Verify Django admin login page returns HTTP 200."""
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)


class AuthSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='staff_test',
            email='staff_test@example.com',
            password='Password123'
        )

    def test_login_page_renders(self):
        """Verify GET /accounts/login/ returns 200 with form."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Staff Portal Sign-In")
        self.assertContains(response, "passwordEyeIcon")

    def test_login_success(self):
        """Verify valid credentials authenticate and redirect to home."""
        response = self.client.post(reverse('login'), {
            'username': 'staff_test',
            'password': 'Password123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back, staff_test!")

    def test_login_invalid_credentials_preserves_username(self):
        """Verify failed login displays error and preserves username."""
        response = self.client.post(reverse('login'), {
            'username': 'staff_test',
            'password': 'WrongPassword999'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")
        self.assertContains(response, 'value="staff_test"')

    def test_register_page_renders(self):
        """Verify GET /accounts/register/ returns 200 with role selection."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register Staff Account")
        self.assertContains(response, "Fleet Dispatcher")

    def test_register_success(self):
        """Verify new staff user creation succeeds and redirects."""
        response = self.client.post(reverse('register'), {
            'username': 'new_dispatcher',
            'email': 'new_disp@example.com',
            'role': 'DISPATCHER',
            'password': 'SecurePassword123',
            'confirm_password': 'SecurePassword123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='new_dispatcher').exists())
        user = User.objects.get(username='new_dispatcher')
        self.assertTrue(user.is_staff)
        self.assertContains(response, "Account successfully created for new_dispatcher")

    def test_register_password_mismatch(self):
        """Verify password mismatch raises error and prevents user creation."""
        response = self.client.post(reverse('register'), {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'role': 'SUPERVISOR',
            'password': 'Password123',
            'confirm_password': 'DifferentPassword456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")
        self.assertFalse(User.objects.filter(username='mismatch_user').exists())

    def test_logout_redirects_to_home(self):
        """Verify logging out clears session and redirects with flash message."""
        self.client.login(username='staff_test', password='Password123')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You have been securely signed out")
