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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "employee", "created_at", "updated_at"]

    def validate(self, data):
        end_date = data.get("end_date")
        start_date = data.get("start_date")
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "La data di fine non può essere precedente alla data di inizio."})
        return data
