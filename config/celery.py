import os
from celery import Celery

# تنظیم مسیر فایل settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# ساخت اپ celery با نام پروژه اصلی (دلخواه)
app = Celery('nava')

# بارگذاری تنظیمات از settings با پیشوند CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# لود خودکار فایل‌های tasks.py از همه‌ی اپ‌ها
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
