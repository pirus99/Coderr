import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def authenticated_user(db, django_user_model):
    user = django_user_model.objects.create_user(
        username='testuser',
        password='secret',
        email='testuser@example.com',
        is_active=True,
        type='customer'
    )
    return user

@pytest.fixture
def business_user(db, django_user_model):
    user = django_user_model.objects.create_user(
        username='businessuser',
        password='secret',
        email='businessuser@example.com',
        is_active=True,
        type='business'
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
def test_post_review(authenticated_client, business_user):
    url = reverse('reviews-list')
    data = {
        "business_user": business_user.id,
        "rating": 3,
        "description": "Alles war toll!"
    }
    response = authenticated_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['rating'] == 3

@pytest.mark.django_db
def test_post_review_duplicate(authenticated_client, business_user):
    url = reverse('reviews-list')
    data = {
        "business_user": business_user.id,
        "rating": 4,
        "description": "Alles war toll!"
    }
    authenticated_client.post(url, data, format='json')
    response = authenticated_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN

# Test PATCH /api/reviews/{id}/
@pytest.mark.django_db
def test_patch_review(authenticated_client, business_user):
    # Create a review first and reuse its id for PATCH
    list_url = reverse('reviews-list')
    create_data = {
        "business_user": business_user.id,
        "rating": 3,
        "description": "Initial review"
    }
    create_resp = authenticated_client.post(list_url, create_data, format='json')
    assert create_resp.status_code == status.HTTP_201_CREATED
    review_id = create_resp.json()['id']

    url = reverse('review-detail', args=[review_id])
    data = {
        "rating": 5,
        "description": "Noch besser als erwartet!"
    }
    response = authenticated_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['rating'] == 5

@pytest.mark.django_db
def test_patch_review_unauthorized(client):
    url = reverse('review-detail', args=[1])
    data = {
        "rating": 5,
        "description": "Noch besser als erwartet!"
    }
    response = client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test DELETE /api/reviews/{id}/
@pytest.mark.django_db
def test_delete_review(authenticated_client):
    # Create a review first and then delete it
    # Need a business_user to attach the review to
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # create a business user for the review target
    business = User.objects.create_user(username='tmpbiz', password='tmp', email='tmpbiz@example.com', is_active=True, type='business')
    list_url = reverse('reviews-list')
    create_data = {
        "business_user": business.id,
        "rating": 2,
        "description": "To be deleted"
    }
    create_resp = authenticated_client.post(list_url, create_data, format='json')
    assert create_resp.status_code == status.HTTP_201_CREATED
    review_id = create_resp.json()['id']

    url = reverse('review-detail', args=[review_id])
    response = authenticated_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_delete_review_unauthorized(client):
    url = reverse('review-detail', args=[1])  # Replace 1 with existing review ID
    response = client.delete(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_delete_review_forbidden(authenticated_client, client, django_user_model, business_user):
    # Create another user and post a review as that user
    other_user = django_user_model.objects.create_user(
        username='other',
        password='secret',
        email='other@example.com',
        is_active=True,
        type='customer'
    )
    other_client = APIClient()
    other_client.force_authenticate(user=other_user)

    list_url = reverse('reviews-list')
    create_data = {
        "business_user": business_user.id,
        "rating": 4,
        "description": "Owned by other user"
    }
    create_resp = other_client.post(list_url, create_data, format='json')
    assert create_resp.status_code == status.HTTP_201_CREATED
    review_id = create_resp.json()['id']

    url = reverse('review-detail', args=[review_id])
    response = authenticated_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN