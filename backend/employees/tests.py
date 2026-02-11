from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Employee


class EmployeeAPITest(TestCase):
    """Tests for GET /api/employees/ endpoint (US-001)."""

    def setUp(self):
        """Create test data: one active employee, one inactive."""
        self.client = APIClient()
        self.mario = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        self.inactive = Employee.objects.create(
            first_name="Luigi",
            last_name="Verdi",
            email="luigi.verdi@example.com",
            role="manager",
            hire_date="2023-06-01",
            is_active=False,
        )

    def test_list_employees_returns_200(self):
        """GET /api/employees/ should return HTTP 200."""
        response = self.client.get("/api/employees/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_excludes_inactive(self):
        """Inactive employees should not appear in the default list (US-004)."""
        response = self.client.get("/api/employees/")
        emails = [e["email"] for e in response.data["results"]]
        self.assertIn("mario.rossi@example.com", emails)
        self.assertNotIn("luigi.verdi@example.com", emails)

    def test_filter_by_role(self):
        """?role=manager should return only managers."""
        Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna.bianchi@example.com",
            role="manager",
            hire_date="2024-03-01",
        )
        response = self.client.get("/api/employees/?role=manager")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["role"], "manager")

    def test_ordering_by_hire_date(self):
        """?ordering=hire_date should sort by hire date ascending."""
        Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna.bianchi@example.com",
            role="employee",
            hire_date="2025-01-01",
        )
        response = self.client.get("/api/employees/?ordering=hire_date")
        dates = [e["hire_date"] for e in response.data["results"]]
        self.assertEqual(dates, sorted(dates))
