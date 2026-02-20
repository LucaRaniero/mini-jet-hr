from datetime import date

from rest_framework import serializers

from .models import Contract, Employee, OnboardingStep, OnboardingTemplate


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "department",
            "hire_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_email(self, value):
        if self.instance and value != self.instance.email:
            raise serializers.ValidationError("L'email non può essere modificata.")
        return value

    def validate_hire_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("La data di assunzione non può essere futura.")
        return value


class ContractSerializer(serializers.ModelSerializer):
    # SerializerMethodField: campo calcolato (read-only), come una computed column.
    # Serve al frontend per avere l'URL completo del file senza doverlo costruire.
    document_url = serializers.SerializerMethodField()
    is_expiring = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            "id",
            "employee",
            "contract_type",
            "ccnl",
            "ral",
            "start_date",
            "end_date",
            "document",
            "document_url",
            "is_expiring",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "employee", "created_at", "updated_at"]

    def get_document_url(self, obj):
        """Build absolute URL for the document file.

        Returns None if no document is uploaded — the frontend checks this
        to decide whether to show preview/download buttons.
        """
        if not obj.document:
            return None
        request = self.context.get("request")
        if request:
            # request.build_absolute_uri() turns relative path into full URL:
            # '/media/contracts/2026/02/file.pdf' → 'http://localhost:8000/media/contracts/2026/02/file.pdf'
            return request.build_absolute_uri(obj.document.url)
        return obj.document.url

    def get_is_expiring(self, obj):
        """Check if the contract is expiring in the next 30 days."""
        if not obj.end_date:
            return False
        if obj.end_date < date.today():
            return False
        return (obj.end_date - date.today()).days <= 30

    def validate_document(self, value):
        """Validate uploaded file: only PDF, max 5 MB."""
        if value is None:
            return value

        # 1. Check file extension
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Solo file PDF sono accettati.")

        # 2. Check content type (security: a .exe renamed to .pdf won't pass)
        if value.content_type != "application/pdf":
            raise serializers.ValidationError("Il file non è un PDF valido.")

        # 3. Check file size (5 MB limit)
        max_size = 5 * 1024 * 1024  # 5 MB
        if value.size > max_size:
            raise serializers.ValidationError("Il file non può superare 5 MB.")

        return value

    def validate(self, data):
        end_date = data.get("end_date")
        start_date = data.get("start_date")
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "La data di fine non può essere precedente alla data di inizio."})
        return data


class OnboardingTemplateSerializer(serializers.ModelSerializer):
    """Serializer for onboarding task templates (the lookup table).

    Simple CRUD — no computed fields, no cross-field validation.
    HR uses this to define what tasks every new employee must complete.
    """

    class Meta:
        model = OnboardingTemplate
        fields = [
            "id",
            "name",
            "description",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OnboardingStepSerializer(serializers.ModelSerializer):
    """Serializer for an employee's onboarding progress.

    Includes denormalized fields from the template (via source="template.field").
    This is the DRF equivalent of a SQL JOIN — the ORM follows the FK
    and reads the attribute from the related model.
    """

    # source="template.name" → segue la FK template, legge .name
    # Come: SELECT t.name AS template_name FROM steps s JOIN templates t ...
    template_name = serializers.CharField(source="template.name", read_only=True)
    template_description = serializers.CharField(source="template.description", read_only=True)

    class Meta:
        model = OnboardingStep
        fields = [
            "id",
            "employee",
            "template",
            "template_name",
            "template_description",
            "is_completed",
            "completed_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "employee",
            "template",
            "completed_at",
            "created_at",
            "updated_at",
        ]
