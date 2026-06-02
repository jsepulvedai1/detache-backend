import os
import requests
import json
from django.conf import settings
from .models import Teacher, Specialty, Instrument, Room

class AIService:
    @staticmethod
    def get_business_context():
        """
        Builds a text context based on the current database state.
        """
        teachers = Teacher.objects.all()
        specialties = Specialty.objects.all()
        instruments = Instrument.objects.all()
        rooms = Room.objects.all()

        context = "Eres el asistente inteligente de 'Détaché Music Academy'.\n"
        context += "Tu objetivo es ayudar a los alumnos con dudas sobre clases, profesores y disponibilidad.\n\n"
        
        context += "INFORMACIÓN DE LA ACADEMIA:\n"
        context += "- Instrumentos disponibles: " + ", ".join([i.name for i in instruments]) + "\n"
        context += "- Especialidades: " + ", ".join([s.name for s in specialties]) + "\n"
        
        context += "\nNUESTROS PROFESORES:\n"
        for t in teachers:
            specs = ", ".join([s.name for s in t.specialties.all()])
            context += f"- {t.name}: Especialista en {specs}.\n"
        
        context += "\nSALA Y ESPACIOS:\n"
        context += "- Contamos con las siguientes salas: " + ", ".join([r.name for r in rooms]) + "\n"
        
        context += "\nREGLAS DE RESPUESTA:\n"
        context += "1. Responde de forma amable y profesional.\n"
        context += "2. Si no sabes algo, invita al alumno a esperar a que un humano lo contacte.\n"
        context += "3. Mantén las respuestas breves para WhatsApp.\n"
        
        return context

    @staticmethod
    def get_response(user_text):
        url = getattr(settings, 'OLLAMA_URL', 'http://host.docker.internal:11434/api/generate')
        model = getattr(settings, 'OLLAMA_MODEL', 'qwen2.5-coder:32b')
        
        context = AIService.get_business_context()
        prompt = f"{context}\n\nPregunta del alumno: {user_text}\nRespuesta:"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get('response', 'Lo siento, no pude generar una respuesta.')
        except Exception as e:
            print(f"Error Ollama: {e}")
            return "Lo siento, tuve un problema al conectar con mi cerebro local. ¿Podrías intentar más tarde?"
