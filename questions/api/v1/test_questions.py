import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from questions.models import Question
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def question(user):
    return Question.objects.create(
        user=user,
        question_text="This is a test question."
    )

@pytest.mark.django_db
def test_question_list(client):
    url = reverse('question-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_question_create(client, user):
    url = reverse('question-create')
    data = {
        'user': user.id,
        'question_text': 'New Question'
    }
    response = client.post(url, data, format='json')
    if response.status_code != status.HTTP_201_CREATED:
        print(response.data)
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_question_detail(client, question):
    url = reverse('question-detail', kwargs={'pk': question.pk})
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_question_delete(client, question):
    url = reverse('question-delete', kwargs={'pk': question.pk})
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_question_update(client, question):
    url = reverse('question-update', kwargs={'pk': question.pk})
    data = {
        'user': question.user.id,
        'question_text': 'Updated Question'
    }
    response = client.put(url, data, format='json')
    if response.status_code != status.HTTP_200_OK:
        print(response.data)
    assert response.status_code == status.HTTP_200_OK
    question.refresh_from_db()
    assert question.question_text == 'Updated Question'
