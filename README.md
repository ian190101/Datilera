# Datilera

Datilera es una plataforma multi-sede para gestión educativa infantil. Incluye alumnos, tutores,
personal, asistencia, inscripciones, finanzas, inventario, comunicaciones, portafolio, calendario,
cursos extra, exportaciones, auditoría e integración con Gemini.

## Arquitectura

El backend usa FastAPI y SQLAlchemy asíncrono. El código se organiza en:

- `app/kernel/domain`: entidades, reglas y errores de negocio.
- `app/kernel/application`: casos de uso.
- `app/kernel/ports`: contratos hacia infraestructura.
- `app/infrastructure`: base de datos, autenticación, colas, archivos, IA y WebSockets.
- `app/interfaces/api/v1`: API modular oficial.
- `app/interfaces/web/routers`: módulos web extraídos y mantenibles.
- `app/interfaces/web/routes.py`: rutas legacy aún pendientes de migración gradual.

La API modular tiene prioridad sobre cualquier ruta legacy equivalente. El arranque omite colisiones
para que una misma combinación de método y URL nunca tenga dos implementaciones activas.

## Preparación local

1. Crear y activar un entorno virtual con Python 3.12.
2. Instalar dependencias:

   ```powershell
   pip install -r requirements-dev.txt
   ```

3. Copiar `.env.example` a `.env` y reemplazar secretos y conexiones.
4. Aplicar migraciones:

   ```powershell
   alembic upgrade head
   ```

5. Iniciar la aplicación:

   ```powershell
   uvicorn app.main:app --reload
   ```

La documentación OpenAPI está disponible en `/api/docs` únicamente en desarrollo.

## Docker

```powershell
docker compose up --build
docker compose exec app alembic upgrade head
```

Los volúmenes de MySQL, Redis, media y PDF son persistentes. Para producción se deben reemplazar
todas las credenciales del compose, usar `ENVIRONMENT=prod`, configurar HTTPS, hosts confiables y
orígenes CORS explícitos.

## Seguridad

- `/api/v1` requiere un access token, salvo login, refresh y registros públicos por código.
- Los módulos validan permisos incluidos en el JWT y la sede se contrasta contra la base de datos.
- Las operaciones autenticadas por cookie validan el origen en métodos con estado.
- Los refresh tokens se rotan y en base de datos se conserva solo una huella SHA-256.
- El login limita intentos mediante Redis y usa un respaldo local si Redis no está disponible.
- `/media` y `/pdf` requieren autenticación; no son directorios estáticos públicos.
- Las subidas se validan por firma binaria, tamaño y nombre generado por el servidor.
- Cada operación API genera una entrada de auditoría sin almacenar el cuerpo de la solicitud.

El archivo `.env`, claves, certificados, logs y archivos cargados no deben versionarse. Si alguna
credencial estuvo previamente en Git, debe rotarse y eliminarse también del historial cuando sea
apropiado.

## Pruebas y calidad

```powershell
pytest
ruff check tests app/middleware app/infrastructure/services/secure_storage.py
python -m compileall -q app
```

Las pruebas iniciales cubren configuración, JWT, rotación de refresh tokens, almacenamiento seguro y
unicidad de rutas. El objetivo siguiente es ampliar cobertura por módulo y reducir progresivamente la
deuda del router legacy.

## Datos recientes para demostración

En desarrollo se pueden refrescar las fechas de registros existentes para presentar el dashboard sin
alterar montos ni crear personas ficticias:

```powershell
.\.venv\Scripts\python.exe scripts\seed_dashboard_demo.py --apply
```

El script se bloquea automáticamente si `ENVIRONMENT=prod`.

## Servicios externos

- MySQL mediante `mysql+aiomysql`.
- Redis para limitación de login y colas RQ.
- Gemini mediante el SDK oficial `google-genai`; el modelo se configura con `GEMINI_MODEL`.
- Archivos PDF y multimedia en almacenamiento local protegido, reemplazable mediante los puertos de
  infraestructura existentes.
