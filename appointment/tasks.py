# tasks.py
from celery import shared_task
from accounts.models import Notification
from kavenegar import KavenegarAPI, APIException, HTTPException
@shared_task
def send_sms(phone_number, message):
    api_key = '31512B64597262546273776B5A546A6D553971522F65626875632F347730593976517647473775376856493D'  # Use a secure method to store your API key
    api = KavenegarAPI(api_key)
    params = {'sender': '90009809', 'receptor': phone_number, 'message': str(message)}
    api.sms_send(params)


@shared_task
def send_sms_task(phone_number, message):
    """ارسال پیامک به صورت غیرهمزمان."""
    try:
        api_key = 'YOUR_API_KEY'  # کلید API کافن‌گار
        api = KavenegarAPI(api_key)
        params = {
            'sender': '90009809',
            'receptor': phone_number,
            'message': message
        }
        api.sms_send(params)
    except (APIException, HTTPException) as e:
        print(f"Error sending SMS: {str(e)}")

@shared_task
def send_notification_task(user_id, message):
    """ایجاد نوتیفیکیشن در دیتابیس به صورت غیرهمزمان."""
    try:
        Notification.objects.create(
            user_id=user_id,
            message=message
        )
    except Exception as e:
        print(f"Error creating notification: {str(e)}")