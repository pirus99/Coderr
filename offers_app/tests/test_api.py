# tests/test_offers_api.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from offers_app.models import Offer, OfferDetail

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def business_user():
    return User.objects.create_user(
        username='business_user',
        email='business@example.com',
        password='testpass123',
        user_type='business'
    )

@pytest.fixture
def customer_user():
    return User.objects.create_user(
        username='customer_user',
        email='customer@example.com',
        password='testpass123',
        user_type='customer'
    )

@pytest.fixture
def offer(business_user):
    offer = Offer.objects.create(
        user=business_user,
        title="Test Offer",
        description="Test Description"
    )
    OfferDetail.objects.create(
        offer=offer,
        title="Basic",
        revisions=2,
        delivery_time_in_days=5,
        price=100,
        features=["Feature 1"],
        offer_type="basic"
    )
    OfferDetail.objects.create(
        offer=offer,
        title="Standard",
        revisions=5,
        delivery_time_in_days=7,
        price=200,
        features=["Feature 1", "Feature 2"],
        offer_type="standard"
    )
    OfferDetail.objects.create(
        offer=offer,
        title="Premium",
        revisions=10,
        delivery_time_in_days=10,
        price=500,
        features=["Feature 1", "Feature 2", "Feature 3"],
        offer_type="premium"
    )
    return offer

@pytest.fixture
def offer_details(offer):
    return offer.details.all()

# GET /api/offers/ Tests
class TestOffersList:
    def test_list_offers_unauthenticated(self, api_client):
        url = reverse('offer-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_list_offers_with_creator_filter(self, api_client, business_user, offer):
        url = reverse('offer-list')
        response = api_client.get(url, {'creator_id': business_user.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['user'] == business_user.id

    def test_list_offers_with_min_price_filter(self, api_client, offer):
        url = reverse('offer-list')
        response = api_client.get(url, {'min_price': 200})
        assert response.status_code == status.HTTP_200_OK
        assert all(offer['min_price'] >= 200 for offer in response.data['results'])

    def test_list_offers_with_max_delivery_time_filter(self, api_client, offer):
        url = reverse('offer-list')
        response = api_client.get(url, {'max_delivery_time': 7})
        assert response.status_code == status.HTTP_200_OK
        assert all(offer['min_delivery_time'] <= 7 for offer in response.data['results'])

    def test_list_offers_with_ordering(self, api_client, offer):
        url = reverse('offer-list')
        response = api_client.get(url, {'ordering': 'min_price'})
        assert response.status_code == status.HTTP_200_OK
        prices = [offer['min_price'] for offer in response.data['results']]
        assert prices == sorted(prices)

    def test_list_offers_with_search(self, api_client, offer):
        url = reverse('offer-list')
        response = api_client.get(url, {'search': 'Test'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_list_offers_with_pagination(self, api_client, offer):
        url = reverse('offer-list')
        response = api_client.get(url, {'page_size': 1})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['count'] == 1

    def test_list_offers_invalid_params(self, api_client):
        url = reverse('offer-list')
        response = api_client.get(url, {'min_price': 'invalid'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

# POST /api/offers/ Tests
class TestOfferCreate:
    def test_create_offer_authenticated_business(self, api_client, business_user):
        api_client.force_authenticate(user=business_user)
        url = reverse('offer-list')
        data = {
            "title": "New Offer",
            "description": "New Description",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Feature 1"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Feature 1", "Feature 2"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Feature 1", "Feature 2", "Feature 3"],
                    "offer_type": "premium"
                }
            ]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Offer.objects.count() == 1
        assert OfferDetail.objects.count() == 3

    def test_create_offer_missing_details(self, api_client, business_user):
        api_client.force_authenticate(user=business_user)
        url = reverse('offer-list')
        data = {
            "title": "Incomplete Offer",
            "description": "Missing details",
            "details": [
                {
                    "title": "Basic",
                    "offer_type": "basic"
                }
            ]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_offer_not_enough_details(self, api_client, business_user):
        api_client.force_authenticate(user=business_user)
        url = reverse('offer-list')
        data = {
            "title": "Incomplete Offer",
            "description": "Not enough details",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Feature 1"],
                    "offer_type": "basic"
                }
            ]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_offer_unauthenticated(self, api_client):
        url = reverse('offer-list')
        data = {
            "title": "Unauthenticated Offer",
            "description": "Should fail",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Feature 1"],
                    "offer_type": "basic"
                }
            ]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_offer_customer_user(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        url = reverse('offer-list')
        data = {
            "title": "customer User Offer",
            "description": "Should fail",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Feature 1"],
                    "offer_type": "basic"
                }
            ]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

# GET /api/offers/{id}/ Tests
class TestOfferRetrieve:
    def test_retrieve_offer_authenticated(self, api_client, customer_user, offer):
        api_client.force_authenticate(user=customer_user)
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == offer.id

    def test_retrieve_offer_unauthenticated(self, api_client, offer):
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_nonexistent_offer(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        url = reverse('offer-detail', kwargs={'pk': 999})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

# PATCH /api/offers/{id}/ Tests
class TestOfferUpdate:
    def test_update_offer_owner(self, api_client, business_user, offer):
        api_client.force_authenticate(user=business_user)
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        data = {
            "title": "Updated Title",
            "details": [
                {
                    "id": offer.details.first().id,
                    "title": "Updated Basic",
                    "revisions": 3,
                    "offer_type": "basic"
                }
            ]
        }
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Updated Title"
        assert response.data['details'][0]['title'] == "Updated Basic"

    def test_update_offer_non_owner(self, api_client, customer_user, offer):
        api_client.force_authenticate(user=customer_user)
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        data = {"title": "Should Fail"}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_offer_unauthenticated(self, api_client, offer):
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        data = {"title": "Should Fail"}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_nonexistent_offer(self, api_client, business_user):
        api_client.force_authenticate(user=business_user)
        url = reverse('offer-detail', kwargs={'pk': 999})
        data = {"title": "Should Fail"}
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_offer_invalid_data(self, api_client, business_user, offer):
        api_client.force_authenticate(user=business_user)
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        data = {"title": ""}  # Empty title should fail
        response = api_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

# DELETE /api/offers/{id}/ Tests
class TestOfferDelete:
    def test_delete_offer_owner(self, api_client, business_user, offer):
        api_client.force_authenticate(user=business_user)
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Offer.objects.count() == 0

    def test_delete_offer_non_owner(self, api_client, customer_user, offer):
        api_client.force_authenticate(user=customer_user)
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_offer_unauthenticated(self, api_client, offer):
        url = reverse('offer-detail', kwargs={'pk': offer.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_nonexistent_offer(self, api_client, business_user):
        api_client.force_authenticate(user=business_user)
        url = reverse('offer-detail', kwargs={'pk': 999})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

# GET /api/offerdetails/{id}/ Tests
class TestOfferDetailRetrieve:
    def test_retrieve_offer_detail_authenticated(self, api_client, customer_user, offer_details):
        api_client.force_authenticate(user=customer_user)
        detail = offer_details.first()
        url = reverse('offerdetail-detail', kwargs={'pk': detail.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == detail.id

    def test_retrieve_offer_detail_unauthenticated(self, api_client, offer_details):
        detail = offer_details.first()
        url = reverse('offerdetail-detail', kwargs={'pk': detail.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_nonexistent_offer_detail(self, api_client, customer_user):
        api_client.force_authenticate(user=customer_user)
        url = reverse('offerdetail-detail', kwargs={'pk': 999})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND