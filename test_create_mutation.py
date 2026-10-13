import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from graphene.test import Client
from core.schema import schema

client = Client(schema)
query = """
mutation {
  createTeacher(
    name: "Test Teacher 2",
    description: "",
    status: "ACTIVE",
    phoneNumber: "",
    rut: "",
    address: "",
    email: "",
    specialtyIds: []
  ) {
    teacher {
      id
      name
    }
  }
}
"""
result = client.execute(query)
print("Teacher Create Result:", result)
