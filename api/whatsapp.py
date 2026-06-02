import requests
from django.conf import settings

class WhatsAppService:
    @staticmethod
    def send_text_message(phone_number, message):
        """
        Sends a text message using the Evolution API.
        """
        url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE_NAME}"
        
        headers = {
            'apikey': settings.EVOLUTION_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "number": phone_number,
            "text": message
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code not in [200, 201]:
                print(f"Error Evolution API ({response.status_code}): {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    @staticmethod
    def send_button_message(phone_number, text, buttons, title="Détaché CRM"):
        """
        Sends a message with interactive buttons using Evolution API.
        'buttons' should be a list of dicts: [{'displayText': 'Sí', 'buttonId': 'id1'}, ...]
        """
        url = f"{settings.EVOLUTION_API_URL}/message/sendButtons/{settings.EVOLUTION_INSTANCE_NAME}"
        
        headers = {
            'apikey': settings.EVOLUTION_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Evolution API v2 requires 'type': 'reply' for each button
        formatted_buttons = []
        for btn in buttons:
            formatted_buttons.append({
                "buttonId": btn.get("buttonId"),
                "buttonText": {"displayText": btn.get("displayText")},
                "type": "reply"
            })

        payload = {
            "number": phone_number,
            "title": title,
            "description": text,
            "buttons": formatted_buttons
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code not in [200, 201]:
                print(f"Error Evolution API Buttons ({response.status_code}): {response.text}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None
