# Directrices de Seguridad y Permisos para el Asistente

## 🔒 Prohibición Estricta de Git Push
- **PROHIBIDO ejecutar `git push` automáticamente.**
- Cualquier intento o necesidad de sincronizar hacia repositorios remotos (`git push`, `git push origin`, etc.) **debe ser consultado y autorizado explícitamente por el usuario antes de ejecutarse**.

## ⚡ Permisos de Ejecución Local
- El asistente tiene permiso total para ejecutar comandos locales de compilación, gestión de paquetes, servidores de desarrollo, migraciones y administración de base de datos (`npm`, `python manage.py`, `docker`, `curl`, `lsof`, `kill`, etc.).

## 📋 Reglas de Negocio: Reservas y Clases de Prueba
- **Sin reservas con adelanto:** Ya no existe la modalidad de reserva parcial o con adelanto.
- **Clase de prueba pagada vía Mercado Pago:** Si el alumno paga por Mercado Pago, la clase de prueba queda confirmada y pagada en su totalidad inmediatamente.
- **Clase de prueba vía Transferencia Bancaria:** Si se selecciona transferencia, la reserva/clase queda en estado **pendiente** hasta que el equipo de staff la verifique y valide manualmente.
