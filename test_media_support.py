import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import json
from graphene.test import Client
from core.schema import schema
from api.models import Teacher
from django.core.files.uploadedfile import SimpleUploadedFile

def setup_test_data():
    # Create a dummy image file
    image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    photo_file = SimpleUploadedFile("test_teacher.gif", image_content, content_type="image/gif")
    
    teacher = Teacher.objects.create(
        name="Carlos Ruiz",
        description="Experto en violoncello.",
        photo=photo_file,
        status="ACTIVE"
    )
    return teacher

def test_queries():
    client = Client(schema)
    
    # Query teacher with ImageField
    query = """
    {
      allTeachers {
        id
        name
        photo
      }
    }
    """
    executed = client.execute(query)
    print("All Teachers with ImageField Result:")
    print(json.dumps(executed, indent=4))

if __name__ == "__main__":
    setup_test_data()
    test_queries()
