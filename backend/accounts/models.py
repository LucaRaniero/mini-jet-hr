from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager: usa email al posto di username per creare utenti.

    BaseUserManager fornisce normalize_email() e set_password().
    Dobbiamo sovrascrivere create_user/create_superuser perché
    AbstractUser li delega al manager, e il default si aspetta username.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email è obbligatoria.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash della password (mai salvata in chiaro)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User: email come campo di login, nessun username.

    AbstractUser fornisce: password, is_active, is_staff, is_superuser,
    last_login, date_joined, groups, user_permissions.

    Phase 1: solo autenticazione (login/logout/refresh).
    Phase 3 (US-012): aggiunta OneToOneField verso Employee per RBAC.
    """

    username = None  # Rimuove il campo username di AbstractUser
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"  # Campo usato per il login
    REQUIRED_FIELDS = []  # email è già required via USERNAME_FIELD

    objects = UserManager()

    def __str__(self):
        return self.email
