import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import json
from graphene.test import Client
from core.schema import schema
from api.models import Profesor, Especialidad, Disponibilidad

def setup_test_data():
    prof = Profesor.objects.create(nombre="Juan Perez", status="ACTIVO")
    Especialidad.objects.create(nombre="Piano", profesor=prof)
    Especialidad.objects.create(nombre="Teoría Musical", profesor=prof)
    Disponibilidad.objects.create(dia="LUNES", hora_inicio="09:00", hora_fin="12:00", profesor=prof)
    return prof

def test_queries():
    client = Client(schema)
    
    # Query all professors
    query = """
    {
      allProfesores {
        id
        nombre
        status
        especialidades {
          nombre
        }
        disponibilidades {
          dia
          horaInicio
          horaFin
        }
      }
    }
    """
    executed = client.execute(query)
    print("All Profesores Query Result:")
    print(json.dumps(executed, indent=4))

if __name__ == "__main__":
    setup_test_data()
    test_queries()
