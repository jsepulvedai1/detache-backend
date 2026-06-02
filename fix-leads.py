import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Lead

valid_services = [choice[0] for choice in Lead.SERVICE_CHOICES]
valid_sources = [choice[0] for choice in Lead.SOURCE_CHOICES]
valid_statuses = [choice[0] for choice in Lead.STATUS_CHOICES]

print(f"Valid Services: {valid_services}")

leads = Lead.objects.all()
fixed_count = 0

for lead in leads:
    needs_save = False
    if lead.servicio not in valid_services:
        print(f"Fixing lead {lead.id} ({lead.nombre}): invalid service '{lead.servicio}' -> 'CLASE_PRUEBA'")
        lead.servicio = 'CLASE_PRUEBA'
        needs_save = True
    
    if lead.fuente not in valid_sources:
        print(f"Fixing lead {lead.id} ({lead.nombre}): invalid source '{lead.fuente}' -> 'WEB'")
        lead.fuente = 'WEB'
        needs_save = True
        
    if lead.estado not in valid_statuses:
        print(f"Fixing lead {lead.id} ({lead.nombre}): invalid status '{lead.estado}' -> 'NUEVO'")
        lead.estado = 'NUEVO'
        needs_save = True
        
    if needs_save:
        lead.save()
        fixed_count += 1

print(f"Done. Fixed {fixed_count} leads.")
