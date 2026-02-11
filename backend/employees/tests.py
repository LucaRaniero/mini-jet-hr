from datetime import date, timedelta

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


class EmployeeCreateAPITest(TestCase):
    """Tests for POST /api/employees/ endpoint (US-002)."""

    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "first_name": "Anna",
            "last_name": "Bianchi",
            "email": "anna.bianchi@example.com",
            "role": "employee",
            "hire_date": "2024-06-01",
        }

    def test_create_employee_returns_201(self):
        """POST with valid data should return HTTP 201 and create the employee."""
        response = self.client.post("/api/employees/", self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.first().email, "anna.bianchi@example.com")

    def test_duplicate_email_returns_400(self):
        """POST with an already-existing email should return HTTP 400."""
        Employee.objects.create(**self.valid_payload)
        response = self.client.post("/api/employees/", self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_future_hire_date_returns_400(self):
        """POST with a future hire_date should return HTTP 400."""
        future_date = date.today() + timedelta(days=30)
        self.valid_payload["hire_date"] = future_date.isoformat()
        response = self.client.post("/api/employees/", self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("hire_date", response.data)

    def test_missing_required_fields_returns_400(self):
        """POST without required fields should return HTTP 400."""
        response = self.client.post("/api/employees/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ["first_name", "last_name", "email", "hire_date"]:
            self.assertIn(field, response.data)
