from celery import shared_task
from kavenegar import KavenegarAPI, APIException, HTTPException
from django.core.mail import send_mail
from django.conf import settings
@shared_task
def send_sms_task(phone_number, message):
    """Task to send an SMS message."""
    try:
        api_key = '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D'  # Replace with a secure method
        api = KavenegarAPI(api_key)
        params = {'sender': '90009809', 'receptor': phone_number, 'message': str(message)}
        api.sms_send(params)
    except (APIException, HTTPException) as e:
        print(f"Error sending SMS: {str(e)}")


# @shared_task
# def send_email_task(to, subject, message):
#     send_mail(
#         subject=subject,
#         message=message,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[to],
#         fail_silently=False,
#     )

@shared_task
def send_email_task(to_email, subject, message):
    """Send an email asynchronously."""
    from_email = settings.DEFAULT_FROM_EMAIL
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return "Email sent successfully"
    except Exception as e:
        return f"Failed to send email: {str(e)}"