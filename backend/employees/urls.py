from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ContractViewSet,
    DashboardView,
    EmployeeViewSet,
    OnboardingStepViewSet,
    OnboardingTemplateViewSet,
)

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("onboarding-templates", OnboardingTemplateViewSet, basename="onboarding-template")

# Nested routes for contracts under employees
# /api/employees/{employee_pk}/contracts/        → list + create
# /api/employees/{employee_pk}/contracts/{pk}/   → detail + update + delete
contract_list = ContractViewSet.as_view({"get": "list", "post": "create"})
contract_detail = ContractViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})

# Nested routes for onboarding steps under employees
# /api/employees/{employee_pk}/onboarding/       → list (GET) + start onboarding (POST)
# /api/employees/{employee_pk}/onboarding/{pk}/  → toggle step completion (PATCH)
onboarding_list = OnboardingStepViewSet.as_view({"get": "list", "post": "create"})
onboarding_detail = OnboardingStepViewSet.as_view({"patch": "partial_update"})

urlpatterns = [
    path("", include(router.urls)),
    # Dashboard: read-only aggregated stats (APIView, not ViewSet)
    # SQL analogy: SELECT from a reporting view, no CRUD needed
    path("dashboard/stats/", DashboardView.as_view(), name="dashboard-stats"),
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
    path(
        "employees/<int:employee_pk>/onboarding/",
        onboarding_list,
        name="employee-onboarding-list",
    ),
    path(
        "employees/<int:employee_pk>/onboarding/<int:pk>/",
        onboarding_detail,
        name="employee-onboarding-detail",
    ),
]
