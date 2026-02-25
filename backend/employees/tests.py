import shutil
import tempfile
from datetime import date, timedelta
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from .models import Contract, Employee, OnboardingStep, OnboardingTemplate
from .tasks import send_welcome_email_task

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


class OnboardingTemplateAPITest(TestCase):
    """Tests for /api/onboarding-templates/ endpoint (US-008)."""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/onboarding-templates/"
        self.valid_payload = {
            "name": "Firma contratto",
            "description": "Firmare il contratto di assunzione.",
            "order": 1,
        }

    def test_list_templates_empty(self):
        """GET should return 200 with empty list when no templates exist."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_create_template_returns_201(self):
        """POST with valid payload should return 201 and create the template."""
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OnboardingTemplate.objects.count(), 1)
        self.assertEqual(OnboardingTemplate.objects.first().name, "Firma contratto")

    def test_list_excludes_inactive(self):
        """Soft-deleted templates should not appear in the default list."""
        OnboardingTemplate.objects.create(name="Active", order=1)
        OnboardingTemplate.objects.create(name="Inactive", order=2, is_active=False)
        response = self.client.get(self.url)
        names = [t["name"] for t in response.data["results"]]
        self.assertIn("Active", names)
        self.assertNotIn("Inactive", names)

    def test_delete_soft_deletes(self):
        """DELETE should set is_active=False, not remove from DB."""
        template = OnboardingTemplate.objects.create(name="Test", order=1)
        response = self.client.delete(f"{self.url}{template.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        template.refresh_from_db()
        self.assertFalse(template.is_active)
        self.assertEqual(OnboardingTemplate.objects.count(), 1)

    def test_update_template(self):
        """PATCH should update specified fields."""
        template = OnboardingTemplate.objects.create(name="Old name", order=1)
        response = self.client.patch(
            f"{self.url}{template.id}/",
            {"name": "New name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        template.refresh_from_db()
        self.assertEqual(template.name, "New name")

    def test_list_ordered_by_order_field(self):
        """Templates should be returned ordered by 'order' field."""
        OnboardingTemplate.objects.create(name="Third", order=3)
        OnboardingTemplate.objects.create(name="First", order=1)
        OnboardingTemplate.objects.create(name="Second", order=2)
        response = self.client.get(self.url)
        names = [t["name"] for t in response.data["results"]]
        self.assertEqual(names, ["First", "Second", "Third"])


class OnboardingStepAPITest(TestCase):
    """Tests for /api/employees/{id}/onboarding/ endpoint (US-008)."""

    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        self.url = f"/api/employees/{self.employee.id}/onboarding/"
        # Creiamo 3 template attivi (come INSERT INTO onboarding_templates)
        self.t1 = OnboardingTemplate.objects.create(name="Firma contratto", order=1)
        self.t2 = OnboardingTemplate.objects.create(name="Setup email", order=2)
        self.t3 = OnboardingTemplate.objects.create(name="Training sicurezza", order=3)

    def test_list_empty_before_start(self):
        """GET should return empty list before onboarding is started."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])

    def test_start_onboarding_creates_steps(self):
        """POST should bulk-create one step per active template."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(OnboardingStep.objects.filter(employee=self.employee).count(), 3)

    def test_start_onboarding_idempotent(self):
        """Calling POST twice should not create duplicate steps."""
        self.client.post(self.url)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OnboardingStep.objects.filter(employee=self.employee).count(), 3)

    def test_start_skips_inactive_templates(self):
        """POST should not create steps for inactive templates."""
        self.t3.is_active = False
        self.t3.save()
        response = self.client.post(self.url)
        self.assertEqual(len(response.data), 2)
        template_names = [s["template_name"] for s in response.data]
        self.assertNotIn("Training sicurezza", template_names)

    def test_start_adds_new_templates(self):
        """POST after adding a new template should create only the missing step."""
        self.client.post(self.url)
        self.assertEqual(OnboardingStep.objects.filter(employee=self.employee).count(), 3)

        # Aggiungi un nuovo template
        OnboardingTemplate.objects.create(name="Badge aziendale", order=4)
        response = self.client.post(self.url)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(OnboardingStep.objects.filter(employee=self.employee).count(), 4)

    def test_start_nonexistent_employee_returns_404(self):
        """POST to a non-existent employee should return 404."""
        response = self.client.post("/api/employees/99999/onboarding/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_toggle_step_completed(self):
        """PATCH is_completed=True should set completed_at automatically."""
        self.client.post(self.url)
        step = OnboardingStep.objects.filter(employee=self.employee).first()
        detail_url = f"{self.url}{step.id}/"

        response = self.client.patch(detail_url, {"is_completed": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        step.refresh_from_db()
        self.assertTrue(step.is_completed)
        self.assertIsNotNone(step.completed_at)

    def test_toggle_step_back_to_incomplete(self):
        """PATCH is_completed=False should reset completed_at to None."""
        self.client.post(self.url)
        step = OnboardingStep.objects.filter(employee=self.employee).first()
        detail_url = f"{self.url}{step.id}/"

        # Completa, poi de-completa
        self.client.patch(detail_url, {"is_completed": True}, format="json")
        response = self.client.patch(detail_url, {"is_completed": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        step.refresh_from_db()
        self.assertFalse(step.is_completed)
        self.assertIsNone(step.completed_at)

    def test_steps_include_template_info(self):
        """GET should include denormalized template_name and template_description."""
        self.t1.description = "Firmare tutti i documenti contrattuali."
        self.t1.save()
        self.client.post(self.url)

        response = self.client.get(self.url)
        first_step = response.data["results"][0]
        self.assertEqual(first_step["template_name"], "Firma contratto")
        self.assertEqual(
            first_step["template_description"],
            "Firmare tutti i documenti contrattuali.",
        )

    def test_steps_isolated_by_employee(self):
        """Steps of employee A should not appear under employee B.

        Nota: il signal post_save auto-crea step per il nuovo dipendente
        (i template esistono già nel setUp), ma devono essere step SEPARATI.
        """
        self.client.post(self.url)

        other = Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna.bianchi@example.com",
            role="employee",
            hire_date="2024-06-01",
        )
        other_url = f"/api/employees/{other.id}/onboarding/"
        response = self.client.get(other_url)
        # Il signal crea 3 step anche per il nuovo dipendente
        self.assertEqual(len(response.data["results"]), 3)
        # Ma gli ID devono essere diversi da quelli del dipendente A
        a_step_ids = set(OnboardingStep.objects.filter(employee=self.employee).values_list("id", flat=True))
        other_step_ids = {s["id"] for s in response.data["results"]}
        self.assertEqual(a_step_ids & other_step_ids, set())


class OnboardingSignalTest(TestCase):
    """Tests for the post_save signal that auto-creates onboarding steps.

    Concetto: il signal equivale a un AFTER INSERT trigger su employees.
    Quando si crea un Employee, il signal chiama il service layer che
    crea automaticamente uno step per ogni template attivo.
    """

    def test_new_employee_gets_steps_from_active_templates(self):
        """Creating a new employee should auto-create one step per active template."""
        t1 = OnboardingTemplate.objects.create(name="Firma contratto", order=1)
        t2 = OnboardingTemplate.objects.create(name="Setup email", order=2)

        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )

        steps = OnboardingStep.objects.filter(employee=employee)
        self.assertEqual(steps.count(), 2)
        template_ids = set(steps.values_list("template_id", flat=True))
        self.assertEqual(template_ids, {t1.id, t2.id})

    def test_signal_skips_inactive_templates(self):
        """Inactive templates should not generate onboarding steps."""
        OnboardingTemplate.objects.create(name="Active", order=1)
        OnboardingTemplate.objects.create(name="Inactive", order=2, is_active=False)

        employee = Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna@example.com",
            role="employee",
            hire_date="2024-06-01",
        )

        steps = OnboardingStep.objects.filter(employee=employee)
        self.assertEqual(steps.count(), 1)
        self.assertEqual(steps.first().template.name, "Active")

    def test_signal_does_not_fire_on_update(self):
        """Updating an employee should NOT create new onboarding steps."""
        OnboardingTemplate.objects.create(name="Task", order=1)

        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        initial_count = OnboardingStep.objects.filter(employee=employee).count()

        # Update employee (triggers save, but created=False)
        employee.department = "Engineering"
        employee.save()

        self.assertEqual(
            OnboardingStep.objects.filter(employee=employee).count(),
            initial_count,
        )

    def test_signal_does_not_fire_on_soft_delete(self):
        """Soft-deleting an employee should NOT create new onboarding steps."""
        OnboardingTemplate.objects.create(name="Task", order=1)

        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        initial_count = OnboardingStep.objects.filter(employee=employee).count()

        # Soft delete (is_active = False, then .save() → created=False)
        employee.is_active = False
        employee.save()

        self.assertEqual(
            OnboardingStep.objects.filter(employee=employee).count(),
            initial_count,
        )

    def test_no_active_templates_no_error(self):
        """Creating an employee with zero active templates should not raise."""
        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        self.assertEqual(OnboardingStep.objects.filter(employee=employee).count(), 0)

    def test_signal_is_idempotent(self):
        """Calling the service function again should not create duplicates."""
        OnboardingTemplate.objects.create(name="Task", order=1)

        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        # Signal already created 1 step. Call service again manually:
        from employees.services import create_onboarding_steps_for_employee

        new_steps = create_onboarding_steps_for_employee(employee)
        self.assertEqual(new_steps, [])
        self.assertEqual(OnboardingStep.objects.filter(employee=employee).count(), 1)

    def test_api_create_employee_auto_creates_steps(self):
        """POST /api/employees/ should trigger signal and auto-create steps."""
        OnboardingTemplate.objects.create(name="Firma contratto", order=1)
        OnboardingTemplate.objects.create(name="Setup email", order=2)

        client = APIClient()
        response = client.post(
            "/api/employees/",
            {
                "first_name": "Mario",
                "last_name": "Rossi",
                "email": "mario.rossi@example.com",
                "role": "employee",
                "hire_date": "2024-01-15",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        employee_id = response.data["id"]
        steps = OnboardingStep.objects.filter(employee_id=employee_id)
        self.assertEqual(steps.count(), 2)


class WelcomeEmailTest(TestCase):
    """Tests for the welcome email sent on employee creation (US-007).

    Django TestCase auto-sovrascrive EMAIL_BACKEND con locmem.EmailBackend.
    Ogni send_mail() appende a django.core.mail.outbox (una lista Python).
    Dopo ogni test, outbox viene svuotato automaticamente.

    Analogia SQL: è come avere una tabella dbo.email_log dove
    sp_send_dbmail scrive invece di inviare realmente.
    Poi fai SELECT * FROM email_log per verificare.
    """

    def test_welcome_email_sent_on_creation(self):
        """Creating a new employee should send exactly one welcome email."""
        Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_welcome_email_recipient(self):
        """The welcome email should be sent TO the new employee's email."""
        Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        self.assertEqual(mail.outbox[0].to, ["mario.rossi@example.com"])

    def test_welcome_email_subject_contains_name(self):
        """The subject should include the employee's first name."""
        Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna@example.com",
            role="employee",
            hire_date="2024-06-01",
        )
        self.assertIn("Anna", mail.outbox[0].subject)

    def test_welcome_email_body_contains_role(self):
        """The body should include the employee's role (display label)."""
        Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="manager",
            hire_date="2024-01-15",
        )
        self.assertIn("Manager", mail.outbox[0].body)

    def test_welcome_email_body_contains_hire_date(self):
        """The body should include the hire date in dd/mm/yyyy format."""
        Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        self.assertIn("15/01/2024", mail.outbox[0].body)

    def test_welcome_email_from_address(self):
        """The from address should match DEFAULT_FROM_EMAIL setting."""
        Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        self.assertEqual(mail.outbox[0].from_email, "hr@minijethr.local")

    def test_no_email_on_update(self):
        """Updating an existing employee should NOT send an email."""
        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        mail.outbox.clear()  # Reset dopo email di creazione

        employee.department = "Engineering"
        employee.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_on_soft_delete(self):
        """Soft-deleting an employee should NOT send an email."""
        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        mail.outbox.clear()

        employee.is_active = False
        employee.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_api_create_triggers_email(self):
        """POST /api/employees/ should trigger signal and send welcome email."""
        client = APIClient()
        client.post(
            "/api/employees/",
            {
                "first_name": "Mario",
                "last_name": "Rossi",
                "email": "mario.rossi@example.com",
                "role": "employee",
                "hire_date": "2024-01-15",
            },
            format="json",
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["mario.rossi@example.com"])


class DashboardAPITest(TestCase):
    """Tests for GET /api/dashboard/stats/ endpoint (US-009).

    This endpoint aggregates data across multiple tables — like a SQL
    reporting view. Each test creates controlled data and verifies
    a specific metric in the response.

    SQL analogy: testing a stored procedure that returns a result set
    from multiple JOINs and GROUP BYs.
    """

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/dashboard/stats/"

    def test_dashboard_returns_200(self):
        """GET /api/dashboard/stats/ should return HTTP 200."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_response_structure(self):
        """Response should contain all expected top-level keys."""
        response = self.client.get(self.url)
        data = response.data
        self.assertIn("employees", data)
        self.assertIn("contracts", data)
        self.assertIn("onboarding", data)
        self.assertIn("charts", data)
        self.assertIn("headcount_trend", data["charts"])
        self.assertIn("department_distribution", data["charts"])

    def test_empty_state_returns_zeroes(self):
        """With no data, all counts should be zero and chart arrays empty."""
        response = self.client.get(self.url)
        data = response.data
        self.assertEqual(data["employees"]["active"], 0)
        self.assertEqual(data["employees"]["inactive"], 0)
        self.assertEqual(data["employees"]["new_hires"], 0)
        self.assertEqual(data["contracts"]["expiring"], 0)
        self.assertEqual(data["onboarding"]["in_progress"], 0)
        self.assertEqual(data["charts"]["headcount_trend"], [])
        self.assertEqual(data["charts"]["department_distribution"], [])

    def test_employee_active_inactive_counts(self):
        """Should count active and inactive employees separately.

        SQL: SELECT COUNT(*) FILTER (WHERE is_active = TRUE/FALSE) FROM employees
        """
        Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario@example.com",
            hire_date="2024-01-15",
        )
        Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna@example.com",
            hire_date="2024-06-01",
        )
        Employee.objects.create(
            first_name="Luigi",
            last_name="Verdi",
            email="luigi@example.com",
            hire_date="2023-01-01",
            is_active=False,
        )

        response = self.client.get(self.url)
        self.assertEqual(response.data["employees"]["active"], 2)
        self.assertEqual(response.data["employees"]["inactive"], 1)

    def test_new_hires_this_month(self):
        """Should count only active employees hired this month.

        SQL: COUNT(*) FILTER (WHERE hire_date >= DATE_TRUNC('month', NOW()))
        """
        today = date.today()
        first_of_month = today.replace(day=1)

        # Hired this month → counts as new hire
        Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario@example.com",
            hire_date=first_of_month,
        )
        # Hired last month → does NOT count
        last_month = first_of_month - timedelta(days=1)
        Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna@example.com",
            hire_date=last_month,
        )
        # Hired this month but inactive → does NOT count
        Employee.objects.create(
            first_name="Luigi",
            last_name="Verdi",
            email="luigi@example.com",
            hire_date=first_of_month,
            is_active=False,
        )

        response = self.client.get(self.url)
        self.assertEqual(response.data["employees"]["new_hires"], 1)

    def test_expiring_contracts(self):
        """Should count contracts with end_date within next 30 days.

        SQL: COUNT(*) WHERE end_date BETWEEN NOW() AND NOW() + 30
        """
        today = date.today()
        emp = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario@example.com",
            hire_date="2024-01-15",
        )
        # Expiring in 15 days → counts
        Contract.objects.create(
            employee=emp,
            contract_type="determinato",
            ccnl="metalmeccanico",
            ral="30000.00",
            start_date="2024-01-01",
            end_date=today + timedelta(days=15),
        )
        # Expiring in 90 days → does NOT count
        Contract.objects.create(
            employee=emp,
            contract_type="determinato",
            ccnl="commercio",
            ral="28000.00",
            start_date="2024-01-01",
            end_date=today + timedelta(days=90),
        )
        # Already expired → does NOT count
        Contract.objects.create(
            employee=emp,
            contract_type="determinato",
            ccnl="metalmeccanico",
            ral="25000.00",
            start_date="2023-01-01",
            end_date=today - timedelta(days=10),
        )
        # No end_date (indeterminato) → does NOT count
        Contract.objects.create(
            employee=emp,
            contract_type="indeterminato",
            ccnl="metalmeccanico",
            ral="40000.00",
            start_date="2024-01-01",
        )

        response = self.client.get(self.url)
        self.assertEqual(response.data["contracts"]["expiring"], 1)

    def test_onboarding_in_progress(self):
        """Should count employees with at least one incomplete onboarding step.

        SQL: SELECT COUNT(DISTINCT employee_id)
             FROM onboarding_steps WHERE is_completed = FALSE
        """
        t1 = OnboardingTemplate.objects.create(name="Task 1", order=1)
        t2 = OnboardingTemplate.objects.create(name="Task 2", order=2)

        # Employee A: has incomplete steps → counts
        emp_a = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario@example.com",
            hire_date="2024-01-15",
        )
        # Signal auto-created steps; they are incomplete by default

        # Employee B: all steps completed → does NOT count
        emp_b = Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna@example.com",
            hire_date="2024-06-01",
        )
        OnboardingStep.objects.filter(employee=emp_b).update(is_completed=True)

        # Employee C: no onboarding steps at all → does NOT count
        # (create employee with no active templates — deactivate them first, then create)
        t1.is_active = False
        t2.is_active = False
        t1.save()
        t2.save()
        Employee.objects.create(
            first_name="Luigi",
            last_name="Verdi",
            email="luigi@example.com",
            hire_date="2024-03-01",
        )

        response = self.client.get(self.url)
        self.assertEqual(response.data["onboarding"]["in_progress"], 1)

    def test_headcount_trend_groups_by_month(self):
        """Should group active employees by hire month.

        SQL: SELECT DATE_TRUNC('month', hire_date) AS month, COUNT(*)
             FROM employees WHERE is_active = TRUE
             GROUP BY month ORDER BY month
        """
        Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario@example.com",
            hire_date="2024-01-15",
        )
        Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna@example.com",
            hire_date="2024-01-20",
        )
        Employee.objects.create(
            first_name="Luigi",
            last_name="Verdi",
            email="luigi@example.com",
            hire_date="2024-03-01",
        )
        # Inactive employee → should NOT appear in trend
        Employee.objects.create(
            first_name="Sara",
            last_name="Neri",
            email="sara@example.com",
            hire_date="2024-03-15",
            is_active=False,
        )

        response = self.client.get(self.url)
        trend = response.data["charts"]["headcount_trend"]

        # Two groups: Jan 2024 (2 employees) and Mar 2024 (1 active)
        self.assertEqual(len(trend), 2)
        self.assertEqual(trend[0], {"month": "2024-01", "count": 2})
        self.assertEqual(trend[1], {"month": "2024-03", "count": 1})

    def test_department_distribution(self):
        """Should group active employees by department, excluding blanks.

        SQL: SELECT department, COUNT(*)
             FROM employees WHERE is_active = TRUE AND department != ''
             GROUP BY department ORDER BY count DESC
        """
        Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario@example.com",
            hire_date="2024-01-15",
            department="Engineering",
        )
        Employee.objects.create(
            first_name="Anna",
            last_name="Bianchi",
            email="anna@example.com",
            hire_date="2024-06-01",
            department="Engineering",
        )
        Employee.objects.create(
            first_name="Luigi",
            last_name="Verdi",
            email="luigi@example.com",
            hire_date="2024-03-01",
            department="HR",
        )
        # No department → excluded
        Employee.objects.create(
            first_name="Sara",
            last_name="Neri",
            email="sara@example.com",
            hire_date="2024-04-01",
        )
        # Inactive → excluded
        Employee.objects.create(
            first_name="Paolo",
            last_name="Blu",
            email="paolo@example.com",
            hire_date="2024-05-01",
            department="Engineering",
            is_active=False,
        )

        response = self.client.get(self.url)
        dist = response.data["charts"]["department_distribution"]

        # Engineering=2, HR=1, ordered by count DESC
        self.assertEqual(len(dist), 2)
        self.assertEqual(dist[0], {"department": "Engineering", "count": 2})
        self.assertEqual(dist[1], {"department": "HR", "count": 1})


class CeleryTaskTest(TestCase):
    """Tests for Celery async tasks (EPIC 3 Phase 4).

    Con CELERY_TASK_ALWAYS_EAGER=True (conftest.py), i task vengono
    eseguiti subito nel processo di test — nessun Redis necessario.
    Equivale a: testare una stored procedure chiamandola direttamente
    invece di schedulare un job SQL Agent.
    """

    def test_send_welcome_email_task_sends_email(self):
        """Task should send exactly one email when called with valid employee PK."""
        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        mail.outbox.clear()  # Reset: signal already sent one email

        send_welcome_email_task(employee.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["mario.rossi@example.com"])

    def test_send_welcome_email_task_nonexistent_employee(self):
        """Task should silently skip if employee PK doesn't exist in DB."""
        send_welcome_email_task(99999)  # PK inesistente

        self.assertEqual(len(mail.outbox), 0)

    def test_send_welcome_email_task_retries_on_smtp_failure(self):
        """Task should call self.retry() when send_mail raises an exception."""
        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )
        mail.outbox.clear()

        with patch("employees.services.send_mail", side_effect=ConnectionError("SMTP down")):
            with patch.object(send_welcome_email_task, "retry", side_effect=ConnectionError) as mock_retry:
                with self.assertRaises(ConnectionError):
                    send_welcome_email_task(employee.pk)

                mock_retry.assert_called_once()

    def test_signal_queues_task_on_employee_creation(self):
        """Signal should call send_welcome_email_task.delay() on new employee."""
        with patch("employees.signals.send_welcome_email_task") as mock_task:
            Employee.objects.create(
                first_name="Mario",
                last_name="Rossi",
                email="mario.rossi@example.com",
                role="employee",
                hire_date="2024-01-15",
            )
            mock_task.delay.assert_called_once()

    def test_signal_does_not_queue_task_on_update(self):
        """Updating an employee should NOT queue the email task."""
        employee = Employee.objects.create(
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            role="employee",
            hire_date="2024-01-15",
        )

        with patch("employees.signals.send_welcome_email_task") as mock_task:
            employee.department = "Engineering"
            employee.save()

            mock_task.delay.assert_not_called()
