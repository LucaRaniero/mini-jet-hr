"""Tests for JWT authentication endpoints (EPIC 5 Phase 1).

Testa il flusso completo JWT:
- Login: POST {email, password} → {access, refresh}
- Refresh: POST {refresh} → {access, refresh} (token rotation)
- Logout: POST {refresh} → blacklist (il token non è più usabile)
- Protected endpoints: senza token → 401, con token → 200

SQL analogy:
- Login = CREATE SESSION con credenziali
- Refresh = rinnovo della sessione senza re-autenticarsi
- Logout = DELETE FROM active_sessions
- 401 = DENY su endpoint protetto
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class JWTLoginTest(TestCase):
    """Tests for POST /api/auth/login/ (token obtain)."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="admin@minijethr.local",
            password="securepass123",
        )
        self.url = "/api/auth/login/"

    def test_login_success_returns_tokens(self):
        """Valid credentials return both access and refresh tokens."""
        response = self.client.post(
            self.url,
            {"email": "admin@minijethr.local", "password": "securepass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password_returns_401(self):
        """Wrong password should be rejected."""
        response = self.client.post(
            self.url,
            {"email": "admin@minijethr.local", "password": "wrongpassword"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user_returns_401(self):
        """Non-existent email should be rejected (same status as wrong password)."""
        response = self.client.post(
            self.url,
            {"email": "nobody@minijethr.local", "password": "whatever"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields_returns_400(self):
        """Empty payload should return 400 (missing required fields)."""
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTRefreshTest(TestCase):
    """Tests for POST /api/auth/refresh/ (token refresh)."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="admin@minijethr.local",
            password="securepass123",
        )
        # Login per ottenere i token
        response = self.client.post(
            "/api/auth/login/",
            {"email": "admin@minijethr.local", "password": "securepass123"},
            format="json",
        )
        self.refresh_token = response.data["refresh"]
        self.url = "/api/auth/refresh/"

    def test_refresh_returns_new_access_token(self):
        """Valid refresh token should return a new access token."""
        response = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_with_invalid_token_returns_401(self):
        """Invalid refresh token should be rejected."""
        response = self.client.post(self.url, {"refresh": "invalid.token.here"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_token(self):
        """With ROTATE_REFRESH_TOKENS=True, refresh should return a new refresh token."""
        response = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        # Il nuovo refresh token deve essere diverso dal vecchio
        self.assertNotEqual(response.data["refresh"], self.refresh_token)


class JWTLogoutTest(TestCase):
    """Tests for POST /api/auth/logout/ (token blacklist)."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="admin@minijethr.local",
            password="securepass123",
        )
        response = self.client.post(
            "/api/auth/login/",
            {"email": "admin@minijethr.local", "password": "securepass123"},
            format="json",
        )
        self.refresh_token = response.data["refresh"]
        self.url = "/api/auth/logout/"

    def test_logout_blacklists_refresh_token(self):
        """After logout, the refresh token should be unusable.

        Flusso: logout (blacklist) → tentativo di refresh → 401.
        SQL analogy: DELETE FROM sessions → SELECT con vecchio session_id → nessun risultato.
        """
        # Logout (blacklist il refresh token)
        response = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Il refresh token blacklistato non deve più funzionare
        response = self.client.post(
            "/api/auth/refresh/",
            {"refresh": self.refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class JWTProtectedEndpointTest(TestCase):
    """Tests that API endpoints require authentication."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_request_returns_401(self):
        """Without a token, protected endpoints return 401."""
        response = self.client.get("/api/employees/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_request_with_bearer_token(self):
        """With a valid Bearer token, endpoints are accessible."""
        user = User.objects.create_user(
            email="admin@minijethr.local",
            password="securepass123",
        )
        # Ottieni il token via login
        login_response = self.client.post(
            "/api/auth/login/",
            {"email": "admin@minijethr.local", "password": "securepass123"},
            format="json",
        )
        access_token = login_response.data["access"]

        # Usa il token nell'header Authorization
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get("/api/employees/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
