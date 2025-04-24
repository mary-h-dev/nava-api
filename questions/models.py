from django.db import models
from django.db import models
from django.contrib.auth import get_user_model
from doctors.models import Doctor
User = get_user_model()
# Create your models here.


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question by {self.user} at {self.created_at}"




class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    answer_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.doctor.full_name} at {self.created_at}"
