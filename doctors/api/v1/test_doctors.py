import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from doctors.models import Doctor
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def doctor(user):
    return Doctor.objects.create(
        user=user,
        full_name="Test Doctor",
        gender="مذکر",
        specialization="روان شناس بالینی",
        degree="دکتری",
        medical_license_number="123456789",
        cooperation_kind='حضوری'
    )

@pytest.mark.django_db
def test_doctor_list(client):
    url = reverse('doctor-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_doctor_create(client, user):
    url = reverse('doctor-create')
    data = {
        'user': user.id,
        'full_name': 'New Doctor',
        'gender': 'مونث',
        'specialization': 'روان شناسی کودک و نوجوان',
        'degree': 'کارشناسی ارشد',
        'medical_license_number': '987654321',
        'cooperation_kind': 'آنلاین'
    }
    response = client.post(url, data, format='json')
    if response.status_code != status.HTTP_201_CREATED:
        print(response.data)
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_doctor_detail(client, doctor):
    url = reverse('doctor-detail', kwargs={'pk': doctor.pk})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_doctor_delete(client, doctor):
    url = reverse('doctor-delete', kwargs={'pk': doctor.pk})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_doctor_update(client, doctor):
    url = reverse('doctor-update', kwargs={'pk': doctor.pk})
    data = {
        'user': doctor.user.id,
        'full_name': 'Updated Doctor',
        'gender': 'مذکر',
        'specialization': 'روان شناس بالینی',
        'degree': 'دکتری',
        'medical_license_number': '123456789',
        'cooperation_kind': 'حضوری'
    }
    response = client.put(url, data, format='json')
    if response.status_code != status.HTTP_200_OK:
        print(response.data)
    assert response.status_code == status.HTTP_200_OK
    doctor.refresh_from_db()
    assert doctor.full_name == 'Updated Doctor'
