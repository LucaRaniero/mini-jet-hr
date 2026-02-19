import shutil
import tempfile
from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .models import Contract, Employee

# Directory temporanea per i media files nei test — evita di sporcare MEDIA_ROOT reale
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


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


class EmployeeUpdateAPITest(TestCase):
    """Tests for PUT/PATCH /api/employees/{id}/ endpoint (US-003)."""

    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )

    def test_patch_updates_field(self):
        """PATCH should update only the specified fields."""
        response = self.client.patch(
            f"/api/employees/{self.employee.id}/",
            {"department": "Engineering"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.department, "Engineering")

    def test_patch_email_rejected(self):
        """PATCH should not allow changing email (immutable field)."""
        response = self.client.patch(
            f"/api/employees/{self.employee.id}/",
            {"email": "new.email@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_patch_same_email_allowed(self):
        """PATCH with the same email value should be accepted (no actual change)."""
        response = self.client.patch(
            f"/api/employees/{self.employee.id}/",
            {"email": "mario.rossi@example.com", "department": "HR"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EmployeeDeleteAPITest(TestCase):
    """Tests for DELETE /api/employees/{id}/ endpoint (US-004)."""

    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )

    def test_delete_soft_deletes(self):
        """DELETE should set is_active=False, not remove from DB."""
        response = self.client.delete(f"/api/employees/{self.employee.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.employee.refresh_from_db()
        self.assertFalse(self.employee.is_active)
        self.assertEqual(Employee.objects.count(), 1)

    def test_deleted_employee_excluded_from_list(self):
        """A soft-deleted employee should not appear in GET /api/employees/."""
        self.client.delete(f"/api/employees/{self.employee.id}/")
        response = self.client.get("/api/employees/")
        emails = [e["email"] for e in response.data["results"]]
        self.assertNotIn("mario.rossi@example.com", emails)


class ContractAPITest(TestCase):
    """Tests for /api/employees/{id}/contracts/ endpoint (US-005)."""

    def setUp(self):
        self.client = APIClient()
        # Creare l'employee "padre" — come INSERT INTO employees prima di INSERT INTO contracts
        self.employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        # URL base per i contratti di questo employee
        self.url = f"/api/employees/{self.employee.id}/contracts/"
        # Payload valido riusabile (come @valid_payload in EmployeeCreateAPITest)
        self.valid_payload = {
            "contract_type": "indeterminato",
            "ccnl": "metalmeccanico",
            "ral": "35000.00",
            "start_date": "2026-01-15",
        }

    def test_list_contracts_empty(self):
        """GET should return 200 with empty list when no contracts exist."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_create_contract_returns_201(self):
        """POST with valid payload should return 201 and create the contract."""
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contract.objects.count(), 1)
        self.assertEqual(Contract.objects.first().employee, self.employee)
        self.assertEqual(Contract.objects.first().contract_type, "indeterminato")

    def test_contract_employee_from_url(self):
        """POST should set employee from URL, not from request body."""
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["employee"], self.employee.id)

    def test_create_contract_end_date_before_start_date_returns_400(self):
        """POST with end_date < start_date should return 400."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["end_date"] = "2025-12-31"
        response = self.client.post(self.url, invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_date", response.data)

    def test_missing_required_fields_returns_400(self):
        """POST with missing required fields should return 400."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ["contract_type", "ccnl", "ral", "start_date"]:
            self.assertIn(field, response.data)

    def test_create_contract_nonexistent_employee_returns_404(self):
        """POST to a non-existent employee should return 404."""
        # Come: EXEC sp_CreateContract @employee_id = 99999 → "Employee not found"
        url = "/api/employees/99999/contracts/"
        response = self.client.post(url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_close_contract(self):
        """PATCH with end_date should close an active contract."""
        # Prima creiamo un contratto attivo (end_date=NULL)
        self.client.post(self.url, self.valid_payload, format="json")
        contract = Contract.objects.first()
        detail_url = f"{self.url}{contract.id}/"

        # Chiudiamo il contratto con PATCH (come UPDATE SET end_date = @date WHERE id = @id)
        response = self.client.patch(detail_url, {"end_date": "2026-12-31"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contract.refresh_from_db()
        self.assertEqual(str(contract.end_date), "2026-12-31")

    def test_delete_contract_hard_deletes(self):
        """DELETE should permanently remove contract from DB (not soft delete)."""
        self.client.post(self.url, self.valid_payload, format="json")
        contract = Contract.objects.first()
        detail_url = f"{self.url}{contract.id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Hard delete: il record NON esiste più nel DB
        self.assertEqual(Contract.objects.count(), 0)

    def test_contracts_isolated_by_employee(self):
        """Contracts of employee A should not appear under employee B."""
        # Creiamo un contratto per employee A
        self.client.post(self.url, self.valid_payload, format="json")

        # Creiamo employee B
        other = Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna.bianchi@example.com",
            role="employee",
            hire_date="2024-06-01",
        )
        # GET contratti di employee B → deve essere vuoto
        other_url = f"/api/employees/{other.id}/contracts/"
        response = self.client.get(other_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ContractDocumentAPITest(TestCase):
    """Tests for PDF upload on /api/employees/{id}/contracts/ (US-005 Phase 2)."""

    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        self.url = f"/api/employees/{self.employee.id}/contracts/"
        # Payload base per multipart — i campi vanno come stringhe singole
        self.base_fields = {
            "contract_type": "indeterminato",
            "ccnl": "metalmeccanico",
            "ral": "35000.00",
            "start_date": "2026-01-15",
        }

    @classmethod
    def tearDownClass(cls):
        # Pulizia della directory temporanea dopo tutti i test
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def _make_pdf(self, name="contratto.pdf", size=1024):
        """Helper: crea un SimpleUploadedFile con content-type PDF."""
        return SimpleUploadedFile(name, b"%PDF-" + b"x" * size, content_type="application/pdf")

    def test_create_contract_with_pdf_returns_201(self):
        """POST multipart with PDF should return 201 and save the file."""
        data = {**self.base_fields, "document": self._make_pdf()}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        contract = Contract.objects.first()
        # Il campo document contiene il path relativo (non vuoto)
        self.assertTrue(contract.document.name)
        self.assertIn("contracts/", contract.document.name)

    def test_create_contract_without_pdf_returns_201(self):
        """POST without document should still work (document is optional)."""
        response = self.client.post(self.url, self.base_fields, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        contract = Contract.objects.first()
        self.assertFalse(contract.document.name)

    def test_document_url_present_when_file_uploaded(self):
        """GET should return document_url with absolute URL when file exists."""
        data = {**self.base_fields, "document": self._make_pdf()}
        self.client.post(self.url, data, format="multipart")
        contract = Contract.objects.first()

        response = self.client.get(f"{self.url}{contract.id}/")
        self.assertIsNotNone(response.data["document_url"])
        self.assertIn("/media/contracts/", response.data["document_url"])

    def test_document_url_null_when_no_file(self):
        """GET should return document_url: null when no file uploaded."""
        self.client.post(self.url, self.base_fields, format="json")
        contract = Contract.objects.first()

        response = self.client.get(f"{self.url}{contract.id}/")
        self.assertIsNone(response.data["document_url"])

    def test_reject_non_pdf_file(self):
        """POST with a non-PDF file should return 400."""
        fake_txt = SimpleUploadedFile("notes.txt", b"hello", content_type="text/plain")
        data = {**self.base_fields, "document": fake_txt}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("document", response.data)

    def test_reject_oversized_file(self):
        """POST with a file > 5 MB should return 400."""
        big_pdf = self._make_pdf(size=6 * 1024 * 1024)
        data = {**self.base_fields, "document": big_pdf}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("document", response.data)

    def test_patch_add_document_to_existing_contract(self):
        """PATCH should allow adding a PDF to a contract created without one."""
        self.client.post(self.url, self.base_fields, format="json")
        contract = Contract.objects.first()
        self.assertFalse(contract.document.name)

        detail_url = f"{self.url}{contract.id}/"
        response = self.client.patch(detail_url, {"document": self._make_pdf()}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contract.refresh_from_db()
        self.assertTrue(contract.document.name)


class ContractExpirationAPITest(TestCase):
    """Tests for is_expiring computed field on contract API responses."""

    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        self.url = f"/api/employees/{self.employee.id}/contracts/"

    def _create_contract(self, end_date=None):
        """Helper: create a contract via API and return the GET response data."""
        payload = {
            "contract_type": "determinato",
            "ccnl": "metalmeccanico",
            "ral": "30000.00",
            "start_date": "2024-01-01",
        }
        if end_date:
            payload["end_date"] = str(end_date)
        response = self.client.post(self.url, payload, format="json")
        contract_id = response.data["id"]
        return self.client.get(f"{self.url}{contract_id}/").data

    def test_no_end_date_not_expiring(self):
        """Contract without end_date (indeterminato) should NOT be expiring."""
        data = self._create_contract(end_date=None)
        self.assertFalse(data["is_expiring"])

    def test_past_end_date_not_expiring(self):
        """Contract with end_date in the past should NOT be expiring."""
        past = date.today() - timedelta(days=30)
        data = self._create_contract(end_date=past)
        self.assertFalse(data["is_expiring"])

    def test_end_date_within_30_days_is_expiring(self):
        """Contract with end_date within 30 days should be expiring."""
        soon = date.today() + timedelta(days=15)
        data = self._create_contract(end_date=soon)
        self.assertTrue(data["is_expiring"])

    def test_end_date_far_future_not_expiring(self):
        """Contract with end_date > 30 days away should NOT be expiring."""
        far = date.today() + timedelta(days=90)
        data = self._create_contract(end_date=far)
        self.assertFalse(data["is_expiring"])
