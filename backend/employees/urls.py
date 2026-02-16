from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContractViewSet, EmployeeViewSet

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")

# Nested routes for contracts under employees
# /api/employees/{employee_pk}/contracts/        → list + create
# /api/employees/{employee_pk}/contracts/{pk}/   → detail + update + delete
contract_list = ContractViewSet.as_view({"get": "list", "post": "create"})
contract_detail = ContractViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})

urlpatterns = [
    path("", include(router.urls)),
    path(
        "employees/<int:employee_pk>/contracts/",
        contract_list,
        name="employee-contract-list",
    ),
    path(
        "employees/<int:employee_pk>/contracts/<int:pk>/",
        contract_detail,
        name="employee-contract-detail",
    ),
]
