import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from questions.models import Answer, Question
from doctors.models import Doctor
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')

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

@pytest.fixture
def question(user):
    return Question.objects.create(
        user=user,
        question_text="This is a test question."
    )

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def answer(question, doctor):
    return Answer.objects.create(
        question=question,
        doctor=doctor,
        answer_text="This is a test answer."
    )

@pytest.mark.django_db
def test_answer_list(client):
    url = reverse('answer-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_answer_create(client, question, doctor):
    url = reverse('answer-create')
    data = {
        'question': question.id,
        'doctor': doctor.id,
        'answer_text': 'New Answer'
    }
    response = client.post(url, data, format='json')
    if response.status_code != status.HTTP_201_CREATED:
        print(response.data)
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_answer_detail(client, answer):
    url = reverse('answer-detail', kwargs={'pk': answer.pk})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_answer_delete(client, answer):
    url = reverse('answer-delete', kwargs={'pk': answer.pk})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_answer_update(client, answer):
    url = reverse('answer-update', kwargs={'pk': answer.pk})
    data = {
        'question': answer.question.id,
        'doctor': answer.doctor.id,
        'answer_text': 'Updated Answer'
    }
    response = client.put(url, data, format='json')
    if response.status_code != status.HTTP_200_OK:
        print(response.data)
    assert response.status_code == status.HTTP_200_OK
    answer.refresh_from_db()
    assert answer.answer_text == 'Updated Answer'
