import re
from django.http import HttpRequest


def normalize_phone_number(phone_number: str) -> str:
    """
    نرمال‌سازی شماره تلفن: حذف فاصله‌ها، تغییر فرمت بین‌المللی و اعتبارسنجی اولیه
    """
    phone_number = phone_number.strip()


    phone_number = re.sub(r"[^\d+]", "", phone_number)

   
    if phone_number.startswith("0098"):
        phone_number = "+98" + phone_number[4:]  
    elif phone_number.startswith("98"):
        phone_number = "+98" + phone_number[2:]  
    elif phone_number.startswith("9"):
        phone_number = "+98" + phone_number  


    if not re.match(r"^\+989\d{9}$", phone_number):
        raise ValueError("شماره تلفن نامعتبر است.")

    return phone_number


def get_client_ip(request: HttpRequest) -> str:
    """
    دریافت IP کاربر از درخواست
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  
    else:
        ip = request.META.get('REMOTE_ADDR')  

    return ip
