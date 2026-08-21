# Directrices de Seguridad y Permisos para el Asistente

## 🔒 Prohibición Estricta de Git Push
- **PROHIBIDO ejecutar `git push` automáticamente.**
- Cualquier intento o necesidad de sincronizar hacia repositorios remotos (`git push`, `git push origin`, etc.) **debe ser consultado y autorizado explícitamente por el usuario antes de ejecutarse**.

## ⚡ Permisos de Ejecución Local
- El asistente tiene permiso total para ejecutar comandos locales de compilación, gestión de paquetes, servidores de desarrollo, migraciones y administración de base de datos (`npm`, `python manage.py`, `docker`, `curl`, `lsof`, `kill`, etc.).
