import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

pytestmark = pytest.mark.django_db

User = get_user_model()


def create_user(username="user", email=None, password="strong-password", type="customer", **kwargs):
    email = email or f"{username}@example.com"
    user = User.objects.create_user(username=username, email=email, password=password, type=type, **kwargs)
    Token.objects.get_or_create(user=user)
    return user

def get_token_for(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token.key

def test_registration_success():
    client = APIClient()
    url = reverse("registration")
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "verysecure123",
        "repeated_password": "verysecure123",
        "type": "customer",
    }
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "user_id" in data

def test_registration_password_mismatch_returns_400():
    client = APIClient()
    url = reverse("registration")
    payload = {
        "username": "baduser",
        "email": "baduser@example.com",
        "password": "abc12345",
        "repeated_password": "different",
        "type": "customer",
    }
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400

def test_login_returns_token():
    pw = "login-pass-123"
    user = create_user("loginuser", password=pw)
    client = APIClient()
    url = reverse("login")
    resp = client.post(url, {"username": user.username, "password": pw}, format="json")
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert "user_id" in data

def test_profiles_list_requires_authentication():
    client = APIClient()
    url = reverse("userprofile-customer-list")
    resp = client.get(url)
    assert resp.status_code in (401, 403)  # configured default requires auth

def test_profiles_list_authenticated_returns_200():
    user = create_user("listuser")
    token = get_token_for(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    url = reverse("userprofile-customer-list")
    resp = client.get(url)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_user_detail_edit_permissions_owner():
    owner = create_user("owneruser")
    owner_token = get_token_for(owner)

    other = create_user("otheruser")
    other_token = get_token_for(other)

    detail_url = reverse("userprofile-detail", args=[owner.user])

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {other_token}")
    resp = client.patch(detail_url, {"username": "changed-by-other"}, format="json")
    assert resp.status_code == 403

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {owner_token}")
    resp = client.patch(detail_url, {"username": "owner-changed"}, format="json")
    assert resp.status_code in (200, 202)
    assert resp.json().get("username") == "owner-changed"
