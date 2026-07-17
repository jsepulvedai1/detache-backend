import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import json
import requests
from django.test import RequestFactory
from api.views import MercadoPagoWebhookView

def run_simulation(payment_id):
    print(f"Simulating Mercado Pago webhook locally for Payment ID: {payment_id}...")
    
    # Create mock request body
    payload = {
        "action": "payment.created",
        "type": "payment",
        "data": {
            "id": str(payment_id)
        }
    }
    
    # Initialize request factory
    factory = RequestFactory()
    request = factory.post(
        '/api/mercadopago/webhook/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    # Call the view
    view = MercadoPagoWebhookView.as_view()
    response = view(request)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content.decode('utf-8')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scratch/trigger_webhook.py <PAYMENT_ID>")
        sys.exit(1)
    
    run_simulation(sys.argv[1])
