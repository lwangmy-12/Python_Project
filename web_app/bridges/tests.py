import pytest
from django.urls import reverse
from bridges.models import Bridge, Feedback

@pytest.mark.django_db
def test_dashboard_view(client):
    url = reverse('dashboard')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_bridge_detail_view(client):
    bridge = Bridge.objects.create(
        state_code="42",
        county_code="001",
        structure_number="TEST001",
        data_year=2025
    )
    url = reverse('bridge_detail', args=[bridge.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "TEST001" in response.content.decode()

@pytest.mark.django_db
def test_feedback_submission(client):
    bridge = Bridge.objects.create(
        state_code="42",
        county_code="001",
        structure_number="TEST002",
        data_year=2025
    )
    url = reverse('bridge_detail', args=[bridge.id])
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'rating': 5,
        'comment': 'Great bridge!'
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirect after success
    assert Feedback.objects.count() == 1
    assert Feedback.objects.first().comment == 'Great bridge!'
