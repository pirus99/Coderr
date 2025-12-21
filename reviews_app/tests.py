from django.test import TestCase

# Create your tests here.

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# Fixtures for authenticated client and user
@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def authenticated_user(db, django_user_model):
    user = django_user_model.objects.create_user(
        username='testuser',
        password='secret',
        is_active=True
    )
    return user

@pytest.fixture
def authenticated_client(client, authenticated_user):
    client.force_authenticate(user=authenticated_user)
    return client

# Test GET /api/reviews/
@pytest.mark.django_db
def test_get_reviews(authenticated_client):
    url = reverse('reviews-list')  # Ensure 'reviews-list' corresponds to the defined view name
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

@pytest.mark.django_db
def test_get_reviews_with_query_parameters(authenticated_client):
    url = reverse('reviews-list')
    query_params = {'business_user_id': 2, 'ordering': 'rating'}
    response = authenticated_client.get(url, query_params)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

# Test unauthorized access
@pytest.mark.django_db
def test_reviews_unauthenticated(client):
    url = reverse('reviews-list')
    response = client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test POST /api/reviews/
@pytest.mark.django_db
def test_post_review(authenticated_client):
    url = reverse('reviews-list')
    data = {
        "business_user": 2,
        "rating": 4,
        "description": "Alles war toll!"
    }
    response = authenticated_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['rating'] == 4

@pytest.mark.django_db
def test_post_review_duplicate(authenticated_client):
    url = reverse('reviews-list')
    data = {
        "business_user": 2,
        "rating": 4,
        "description": "Alles war toll!"
    }
    authenticated_client.post(url, data, format='json')
    response = authenticated_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

# Test PATCH /api/reviews/{id}/
@pytest.mark.django_db
def test_patch_review(authenticated_client):
    url = reverse('reviews-detail', args=[1])  # Replace 1 with existing review ID
    data = {
        "rating": 5,
        "description": "Noch besser als erwartet!"
    }
    response = authenticated_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['rating'] == 5

@pytest.mark.django_db
def test_patch_review_unauthorized(client):
    url = reverse('reviews-detail', args=[1])
    data = {
        "rating": 5,
        "description": "Noch besser als erwartet!"
    }
    response = client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test DELETE /api/reviews/{id}/
@pytest.mark.django_db
def test_delete_review(authenticated_client):
    url = reverse('reviews-detail', args=[1])  # Replace 1 with existing review ID
    response = authenticated_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_delete_review_unauthorized(client):
    url = reverse('reviews-detail', args=[1])  # Replace 1 with existing review ID
    response = client.delete(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_delete_review_forbidden(authenticated_client, authenticated_user):
    url = reverse('reviews-detail', args=[2])  # Replace 2 with review ID not owned by the user
    response = authenticated_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN