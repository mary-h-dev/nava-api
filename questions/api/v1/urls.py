
from django.urls import path
from questions.api.v1.views  import (
    QuestionList, QuestionCreate, QuestionDetail, QuestionDelete, QuestionUpdate,
    AnswerList, AnswerCreate, AnswerDetail, AnswerDelete, AnswerUpdate
)



urlpatterns = [
    # URLs for Question
    path('questions/', QuestionList.as_view(), name='question-list'),
    path('questions/create/', QuestionCreate.as_view(), name='question-create'),
    path('questions/<int:pk>/', QuestionDetail.as_view(), name='question-detail'),
    path('questions/<int:pk>/delete/', QuestionDelete.as_view(), name='question-delete'),
    path('questions/<int:pk>/update/', QuestionUpdate.as_view(), name='question-update'),

    # URLs for Answer
    path('answers/', AnswerList.as_view(), name='answer-list'),
    path('answers/create/', AnswerCreate.as_view(), name='answer-create'),
    path('answers/<int:pk>/', AnswerDetail.as_view(), name='answer-detail'),
    path('answers/<int:pk>/delete/', AnswerDelete.as_view(), name='answer-delete'),
    path('answers/<int:pk>/update/', AnswerUpdate.as_view(), name='answer-update'),
]
