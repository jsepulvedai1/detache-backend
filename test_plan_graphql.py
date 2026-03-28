import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import json
from graphene.test import Client
from core.schema import schema
from api.models import Plan

def setup_test_data():
    Plan.objects.create(name="Plan Mensual", price=50.00, duration=1)
    Plan.objects.create(name="Plan Semestral", price=250.00, duration=6)

def test_queries():
    client = Client(schema)
    
    # Query all plans
    query = """
    {
      allPlans {
        id
        name
        price
        duration
      }
    }
    """
    executed = client.execute(query)
    print("All Plans Query Result:")
    print(json.dumps(executed, indent=4))

if __name__ == "__main__":
    setup_test_data()
    test_queries()
