import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from graphene.test import Client
from core.schema import schema

client = Client(schema)
query = """
mutation {
  createStudent(
    name: "Test Student 3",
    email: null,
    birthDate: null
  ) {
    student {
      id
      name
    }
  }
}
"""
result = client.execute(query)
print("Student Create Result:", result)
