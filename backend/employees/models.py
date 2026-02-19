from django.db import models


class Employee(models.Model):
    """Core employee model for Mini Jet HR.

    Supports soft delete (US-004): employees are marked inactive
    rather than physically deleted, preserving historical data.
    """

    class Role(models.TextChoices):
        EMPLOYEE = "employee", "Employee"
        MANAGER = "manager", "Manager"
        ADMIN = "admin", "Admin"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    department = models.CharField(max_length=100, blank=True, default="")
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Contract(models.Model):
    """Contract associated to an employee (US-005).

    A single employee can have multiple contracts over time.
    The active contract is the one with end_date IS NULL.
    """

    class ContractType(models.TextChoices):
        DETERMINATO = "determinato", "Determinato"
        INDETERMINATO = "indeterminato", "Indeterminato"
        STAGISTA = "stagista", "Stagista"

    class CCNL(models.TextChoices):
        METALMECCANICO = "metalmeccanico", "Metalmeccanico"
        COMMERCIO = "commercio", "Commercio"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="contracts")
    contract_type = models.CharField(max_length=50, choices=ContractType.choices)
    ccnl = models.CharField(max_length=50, choices=CCNL.choices)
    ral = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    document = models.FileField(upload_to="contracts/%Y/%m/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee", "-start_date"]

    def __str__(self):
        return f"{self.employee} - {self.contract_type}"
