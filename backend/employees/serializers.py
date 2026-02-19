from datetime import date

from rest_framework import serializers

from .models import Contract, Employee


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
