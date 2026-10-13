import os
import django
from dateutil.relativedelta import relativedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import StudentPack

count = 0
for pack in StudentPack.objects.filter(expiration_date__isnull=True):
    if pack.plan and pack.plan.duration:
        pack.expiration_date = pack.purchase_date + relativedelta(months=pack.plan.duration)
        pack.save(update_fields=['expiration_date'])
        count += 1
print(f"Updated {count} packs.")
