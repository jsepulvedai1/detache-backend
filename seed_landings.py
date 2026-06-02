import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import LandingPage

LANDING_DATA = {
  'piano-ninos': {
    'title': 'Piano para Niños',
    'subtitle': 'Desarrolla su talento y confianza desde temprana edad.',
    'problem': 'Muchos niños ven la música como una obligación aburrida y terminan abandonando a los pocos meses.',
    'solution': 'Nuestra metodología lúdica y técnica asegura que amen el piano mientras construyen una base técnica profesional sólida.',
    'benefits': [
      'Desarrollo cognitivo y concentración mejorada.',
      'Método sin frustraciones adaptado a su edad.',
      'Presentaciones semestrales para ganar confianza.',
      'Profesores especializados en pedagogía infantil.'
    ],
    'image': '/images/piano-kids.png',
    'cta': 'Agendar Clase de Prueba Gratis'
  },
  'piano-adultos': {
    'title': 'Piano para Adultos',
    'subtitle': 'Nunca es tarde para cumplir tu sueño musical.',
    'problem': 'La rutina y la falta de tiempo suelen postergar nuestros deseos de aprender un instrumento.',
    'solution': 'Clases flexibles y enfocadas en tus gustos musicales, eliminando la teoría excesiva y priorizando el placer de tocar.',
    'benefits': [
      'Horarios flexibles para gente que trabaja.',
      'Aprende tus canciones favoritas desde la primera semana.',
      'Reducción de estrés y mejora del bienestar mental.',
      'Sin presiones, a tu propio ritmo.'
    ],
    'image': '/images/piano-adults.png',
    'cta': 'Comenzar mi Viaje Musical'
  },
  'canto': {
    'title': 'Clases de Canto',
    'subtitle': 'Libera tu voz y domina tu técnica vocal.',
    'problem': 'Cantar con tensión o sin control puede dañar tus cuerdas vocales y limitar tu rango.',
    'solution': 'Entrenamiento profesional para potenciar tu voz, mejorar la respiración y ganar seguridad en el escenario.',
    'benefits': [
      'Control respiratorio y apoyo diafragmático.',
      'Ampliación del rango vocal sin esfuerzo.',
      'Interpretación y manejo escénico.',
      'Grabaciones en estudio para evaluar tu progreso.'
    ],
    'image': '/images/canto.png',
    'cta': 'Reservar Evaluación Vocal'
  },
  'clases-grupales': {
    'title': 'Clases Grupales',
    'subtitle': 'La magia de hacer música en comunidad.',
    'problem': 'Aprender solo puede ser solitario y nos priva de la experiencia de ensamble.',
    'solution': 'Grupos reducidos donde compartes tu pasión, aprendes de otros y desarrollas el oído musical colectivo.',
    'benefits': [
      'Aprendizaje social y colaborativo.',
      'Menor costo por sesión con la misma calidad.',
      'Práctica de ensamble y ritmo grupal.',
      'Amistades unidas por la música.'
    ],
    'image': '/images/method.png',
    'cta': 'Consultar Disponibilidad de Grupos'
  },
  'clase-prueba': {
    'title': 'Clase de Prueba',
    'subtitle': 'Tu primer paso sin compromisos.',
    'problem': '¿No sabes si el instrumento es para ti o si te gustará el profesor?',
    'solution': 'Una sesión de 45 minutos para conocernos, evaluar tu nivel y que experimentes nuestra metodología premium.',
    'benefits': [
      'Diagnóstico de nivel gratuito.',
      'Conoce nuestras instalaciones de primer nivel.',
      'Recibe una hoja de ruta para tu aprendizaje.',
      'Sin compromisos de permanencia.'
    ],
    'image': '/images/piano-hero.png',
    'cta': 'Agendar mi Clase de Prueba ahora'
  }
}

print("Iniciando migración de datos de landings...")

for slug, data in LANDING_DATA.items():
    page, created = LandingPage.objects.update_or_create(
        slug=slug,
        defaults={
            'title': data['title'],
            'subtitle': data['subtitle'],
            'problem': data['problem'],
            'solution': data['solution'],
            'benefits': data['benefits'],
            'image_url': data['image'],
            'cta': data['cta']
        }
    )
    if created:
        print(f"✅ Creada landing: {slug}")
    else:
        print(f"🔄 Actualizada landing: {slug}")

print("Migración completada.")
