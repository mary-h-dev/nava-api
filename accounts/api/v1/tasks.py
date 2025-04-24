from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email_task(email, otp):
    subject = 'Your One-Time Password (OTP)'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_BACKEND
    recipient_list = [email]

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        fail_silently=False,
    )