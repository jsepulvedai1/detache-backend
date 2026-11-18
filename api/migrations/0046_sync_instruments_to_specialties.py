from django.db import migrations

def sync_instruments_to_specialties(apps, schema_editor):
    Instrument = apps.get_model('api', 'Instrument')
    Specialty = apps.get_model('api', 'Specialty')
    for inst in Instrument.objects.all():
        name = inst.name.strip() if inst.name else ""
        if name and not Specialty.objects.filter(name__iexact=name).exists():
            Specialty.objects.create(name=name)

def reverse_sync(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0045_alter_lead_estado'),
    ]

    operations = [
        migrations.RunPython(sync_instruments_to_specialties, reverse_sync),
    ]
