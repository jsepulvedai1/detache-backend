import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import json
from graphene.test import Client
from core.schema import schema
from api.models import Teacher

def setup_test_data():
    teacher = Teacher.objects.create(
        name="Elena Garcia",
        description="Profesora de violín con 10 años de experiencia.",
        photo="https://example.com/elena.jpg",
        status="ACTIVE"
    )
    return teacher

def test_queries():
    client = Client(schema)
    
    # Query teacher with extra fields
    query = """
    {
      allTeachers {
        id
        name
        description
        photo
        status
      }
    }
    """
    executed = client.execute(query)
    print("All Teachers with Extra Fields Result:")
    print(json.dumps(executed, indent=4))

if __name__ == "__main__":
    setup_test_data()
    test_queries()
