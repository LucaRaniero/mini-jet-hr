from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Contract, Employee, OnboardingStep, OnboardingTemplate
from .serializers import (
    ContractSerializer,
    EmployeeSerializer,
    OnboardingStepSerializer,
    OnboardingTemplateSerializer,
)
from .services import create_onboarding_steps_for_employee


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Employee CRUD operations.

    Supports:
    - Filtering: ?role=manager
    - Ordering: ?ordering=hire_date, ?ordering=-hire_date
    - Pagination: ?page=2 (configured globally in settings.py)

    Only active employees are returned by default (soft delete support).
    """

    serializer_class = EmployeeSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["last_name", "first_name", "hire_date"]
    ordering = ["last_name", "first_name"]

    def get_queryset(self):
        qs = Employee.objects.filter(is_active=True)

        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)

        return qs

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class ContractViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Contract CRUD, nested under an Employee.

    URL: /api/employees/{employee_pk}/contracts/
    - GET list:   all contracts for this employee (newest first)
    - POST:       create contract, employee taken from URL
    - GET detail: single contract
    - PATCH:      partial update (e.g. close contract by setting end_date)
    - DELETE:     hard delete (contracts are not soft-deleted)
    """

    serializer_class = ContractSerializer

    def get_queryset(self):
        # Filtra contratti solo per l'employee nella URL
        # Come: SELECT * FROM contracts WHERE employee_id = @employee_pk
        return Contract.objects.filter(employee_id=self.kwargs["employee_pk"])

    def perform_create(self, serializer):
        # Prende l'employee dalla URL e lo inietta nel contratto
        # Come: INSERT INTO contracts (employee_id, ...) VALUES (@employee_pk, ...)
        employee = get_object_or_404(Employee, pk=self.kwargs["employee_pk"])
        serializer.save(employee=employee)


class OnboardingTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD for onboarding task templates (the lookup table).

    HR uses this to define which tasks every new hire must complete.
    Soft delete: DELETE sets is_active=False, listing only shows active templates.

    SQL analogy: this is like managing rows in a lookup/dimension table.
    """

    serializer_class = OnboardingTemplateSerializer

    def get_queryset(self):
        # Solo template attivi — come: SELECT * FROM templates WHERE is_active = 1
        return OnboardingTemplate.objects.filter(is_active=True)

    def perform_destroy(self, instance):
        # Soft delete — come Employee: UPDATE SET is_active = 0
        instance.is_active = False
        instance.save()


class OnboardingStepViewSet(viewsets.ModelViewSet):
    """
    Onboarding progress for a specific employee.

    URL: /api/employees/{employee_pk}/onboarding/
    - GET list:     all steps for this employee (ordered by template.order)
    - POST create:  "start onboarding" — bulk creates one step per active template
    - PATCH detail: toggle step completion (is_completed + auto-set completed_at)

    The create() override is the most interesting part:
    instead of creating ONE resource from request body,
    it bulk-creates N resources from the active templates.

    SQL analogy for create():
        INSERT INTO onboarding_steps (employee_id, template_id)
        SELECT @employee_pk, id FROM onboarding_templates
        WHERE is_active = 1
        AND id NOT IN (SELECT template_id FROM onboarding_steps
                       WHERE employee_id = @employee_pk);
    """

    serializer_class = OnboardingStepSerializer
    # Limitiamo i metodi HTTP: no PUT (solo PATCH), no DELETE
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        # select_related("template") → fa un JOIN invece di N query separate.
        # Senza: 1 query per lista + N query per leggere ogni template.name
        # Con: 1 sola query con JOIN. Ottimizzazione critica per liste.
        return OnboardingStep.objects.filter(employee_id=self.kwargs["employee_pk"]).select_related("template")

    def create(self, request, *args, **kwargs):
        """Start/sync onboarding: crea step mancanti dai template attivi.

        Delega la business logic al service layer (DRY).
        Utile anche per "sincronizzare" quando si aggiungono nuovi template
        dopo la creazione del dipendente.
        """
        employee = get_object_or_404(Employee, pk=self.kwargs["employee_pk"])
        create_onboarding_steps_for_employee(employee)

        # Ritorna la lista completa (nuovi + esistenti)
        steps = self.get_queryset()
        serializer = self.get_serializer(steps, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        """Auto-manage completed_at when is_completed changes.

        Business logic:
        - is_completed: False → True  → completed_at = now()
        - is_completed: True → False  → completed_at = None (reset)
        - is_completed unchanged      → don't touch completed_at
        """
        instance = serializer.instance
        new_completed = serializer.validated_data.get("is_completed")

        if new_completed is not None and new_completed != instance.is_completed:
            if new_completed:
                serializer.save(completed_at=timezone.now())
            else:
                serializer.save(completed_at=None)
        else:
            serializer.save()
