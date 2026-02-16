from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404

from .models import Contract, Employee
from .serializers import ContractSerializer, EmployeeSerializer


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
