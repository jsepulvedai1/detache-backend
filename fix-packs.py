import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Student, StudentPack

for student in Student.objects.all():
    active_packs = list(StudentPack.objects.filter(student=student, is_active=True).order_by('-purchase_date', '-id'))
    if len(active_packs) > 1:
        latest_pack = active_packs[0]
        older_packs = active_packs[1:]
        
        rolled_over = sum([p.remaining_classes for p in older_packs])
        
        if rolled_over > 0:
            latest_pack.total_classes += rolled_over
            latest_pack.remaining_classes += rolled_over
            latest_pack.save(update_fields=['total_classes', 'remaining_classes'])
            print(f"Student {student.name}: Consolidated {rolled_over} classes into Pack ID {latest_pack.id}")
            
        for p in older_packs:
            p.is_active = False
            p.save(update_fields=['is_active'])
            print(f"Student {student.name}: Marked older Pack ID {p.id} as inactive.")

print("Finished consolidating packs.")
