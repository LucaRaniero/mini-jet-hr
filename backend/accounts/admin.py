from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin per il Custom User model (email al posto di username).

    BaseUserAdmin fornisce l'interfaccia standard di Django per gestire utenti.
    Dobbiamo adattare fieldsets e display perché abbiamo rimosso username.
    """

    ordering = ["email"]
    list_display = ["email", "is_staff", "is_active"]
    search_fields = ["email"]

    # Fieldsets per la pagina di modifica utente
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permessi",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Date", {"fields": ("last_login", "date_joined")}),
    )

    # Fieldsets per la pagina di creazione utente
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
