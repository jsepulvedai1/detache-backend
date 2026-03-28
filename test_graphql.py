import os
import django
import json
from graphene.test import Client
from core.schema import schema

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_graphql():
    client = Client(schema)
    executed = client.execute('{ hello }')
    print(json.dumps(executed, indent=4))

if __name__ == "__main__":
    test_graphql()
