import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Lesson
ghosts = Lesson.objects.filter(student__isnull=True, lead__isnull=True)
count = ghosts.count()
ghosts.delete()
print(f"Deleted {count} ghost bookings.")
