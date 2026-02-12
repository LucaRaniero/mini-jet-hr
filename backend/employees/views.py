from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from .models import Employee
from .serializers import EmployeeSerializer


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
