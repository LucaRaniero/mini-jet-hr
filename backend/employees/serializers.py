from datetime import date

from rest_framework import serializers

from .models import Employee


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
