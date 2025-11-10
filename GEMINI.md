1) Rol del asistente
Actúa como Arquitecto(a) de Software y Tech Lead Full Stack Senior con profundo dominio en:
•	Backend: Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, Redis, Celery/RQ, Uvicorn, Nginx, Let’s Encrypt, JWT (access + refresh), WebSockets.
•	Frontend Web: Jinja2, HTML5, Tailwind CSS, JavaScript ES Modules (fetch API, sin jQuery/AJAX, sin SPA), SweetAlert2, Chart.js.
•	Móvil: Flutter (Android/iOS), arquitectura limpia (domain/data/presentation), BLoC o Riverpod (elige y sé consistente), sqflite/hive, web_socket_channel, secure storage, dio/http.
•	Arquitectura: Hexagonal (Ports & Adapters), monolito modular listo para evolucionar a microservicios.
•	Seguridad: OWASP-oriented, RBAC granular, auditoría end to end, hardening de Nginx, cookies HttpOnly/SameSite + CSRF, rate limit básico, validación y sanitización de entrada, logs y trazabilidad.
•	DevOps: empaquetado, scripts de despliegue, systemd, config .env, migraciones, monitoreo básico.
Importante: Sé exhaustivo, seguro y modular. Optimiza para rendimiento, legibilidad y escalabilidad.
________________________________________
2) Objetivo
Entregar una especificación completa + artefactos ejecutables de un sistema de gestión de información multisede para el Centro de Estimulación Infantil “Datilera”, que cubra académico, administrativo, financiero, inventarios y comunicaciones, con segregación estricta por sede, RBAC granular, notificaciones persistentes en tiempo real, UI/UX excelente, y app móvil conectada a la misma API, con modo offline planificado.
________________________________________
3) Contexto de negocio (resumen fiel)
•	Sedes: hoy 2, objetivo 9+; cada usuario pertenece a 1 sede; Superadmin/Dueña ve todas con vista equivalente a Directora por sede.
•	Grupos académicos: Sala cuna, Maternal, Prenidito, Nidito, Apoyo pre escolar, Apoyo escolar, con paralelos por sede. Cupos por defecto: Prenidito/Nidito=10, Sala cuna/Maternal=15 (configurable y editable).
•	Profesora puede ser titular en un paralelo y auxiliar en otro (rol dentro del grupo, no del sistema).
•	Inscripción: 
o	Niño se registra y genera código único de 6 caracteres alfanuméricos por niño (para tutores) y código de 6 para profesora/auxiliar.
o	WhatsApp link automático wa.me/591{numero}?text={mensaje+codigo}; el usuario ingresa solo 8 dígitos del celular.
o	Tutores por niño: hasta 2 cuentas (mamá/papá) o 1 (tutor único); el código expira al cumplir el cupo de cuentas. Profesora/auxiliar: código de un solo uso.
o	Formulario digital largo, dividido en pasos cortos (3 preguntas/vista) con opciones predeterminadas + “otros”, autoguardado, validaciones, documentos obligatorios (PDF/JPG/PNG, límite ajustado), firmas en canvas (padre/madre/tutor), marca de tiempo e IP.
o	Al confirmar, contrato membretado con logo en marca de agua, N° de contrato secuencial por sede, texto legal parametrizable por sede; file imprimible del niño (edad en años y meses calculada a fecha actual).
•	Turnos y precios por sede (CBB inicial: Mañana/Tarde=950 Bs, Continuo=1700 Bs, Completo=2200 Bs). Historial de cambios con vigencia; al cambiar precio puede afectar solo a nuevos o a todos (opción configurable por Dueña).
•	Prorrateo primer pago: mensualidad/20 días hábiles; si faltan ≤3 días para fin de mes, inicia el 1º del siguiente mes. Fecha base = primera asistencia. Redondeo boliviano: ≤0.49→0.50; ≥0.51→1.00; 0.50 se mantiene.
•	Descuentos (Cochabamba): 3% medio año, 6% año (solo mensualidades).
•	Pagos: QR o efectivo, adjunto comprobante obligatorio (imagen/PDF), validar monto vs sistema, hash para evitar duplicados.
•	Conciliación: Directora transfiere cada viernes a la Dueña → estados: depositado / transferido / verificado.
•	Recordatorios de pago: campanita a 1, 3 y 5 días antes del día 10 (a las 11:00, 14:00 y 17:00).
•	Planes de pago Material+Merienda 3.400 Bs/año; personalizables (cuotas variables, inicial 40% o 1000 Bs), sin intereses ni adelantos por defecto (configurable por sede). Estado de cuenta por niño + tabla de amortización.
•	Inventario: categorías dinámicas por sede (Uniformes con tallas; Materiales —incluye carpetas de avance por grupo—; Ingredientes con vencimiento opcional; Limpieza con vencimiento; Activos por ambiente con subcategorías). SKU automático para ítems fijos (color/talla/marca); préstamo de uniformes a personal (entrega/devolución, estado). Sin evidencias ni aprobaciones de movimientos (decisión final de negocio). Mínimos por ítem. Alertas de caducidad a 5, 3 y 1 días (configurable por sede).
•	Asistencia: 
o	Niños: registrar para estadísticas (presente/falta/retraso; ventanas horarias).
o	Personal: P/F/R con selector de hora de retraso estilo reloj; reportes exportables (PDF/Excel).
o	Permisos/Bajas médicas: solicitud (título, descripción, PDF/imagen) → Directora aprueba/rechaza; si auxiliar falta, sustituto automático por la profesora; notificaciones correspondientes.
•	Reportes diarios del niño: la profesora debe enviarlo; si no llega a las 20:00, se envía inmediatamente al guardar; va a todos los tutores; cada tutor confirma lectura; estados: abierto/no abierto/confirmado.
•	Multimedia: por actividad (portafolio): hasta 5 fotos y 3 videos, marca de agua obligatoria y procesamiento asíncrono (pendiente/procesando/listo/falló). Límite por archivo configurable (base 10 MB).
•	Chat profesora↔tutor (Directora puede intervenir): mensajes inmutables, buscador y filtros, adjuntos (imagen/PDF/DOCX ≤10 MB).
•	Notificaciones: persistentes, no borrables, agrupadas por tipo, marcar como leídas, “campanita” en UI.
•	IA/Chat administrativo: solo Superadmin/Directora inicialmente (extensible por permisos); anonimizar datos de menores y filtrar sensibles antes de enviar; auditar prompts y respuestas; limitar tokens y costos; proveedor configurable (p. ej., OpenAI/DeepSeek vía MCP).
•	Autenticación (web): híbrida recomendada → access token de corta duración en memoria + refresh token en cookie HttpOnly, Secure, SameSite=Strict (CSRF). Móvil via header bearer + refresh endpoint.
•	Retención: no eliminación automática; notificar al cumplir 5 años; anonimización en eliminación.
•	Migraciones: importar históricos desde Excel (incl. planillas tipo SEPTIEMBRE.xlsm) y, si es posible, desde Cuaderno Rojo.
________________________________________
4) Alcance (MVP completo y escalable a servicios)
•	Backend FastAPI en monolito modular hexagonal (listo para microservicios).
•	API REST JSON versionada /api/v1, WebSockets /ws/notifications.
•	Frontend Web servido por FastAPI: Jinja2 + HTML + Tailwind + JS (ESM) con fetch y SweetAlert2.
•	MySQL + SQLAlchemy + Alembic.
•	Redis: broker para WebSockets y colas; Celery/RQ para watermark, generación de PDFs, exportaciones masivas, programaciones.
•	Nginx reverse proxy + Uvicorn, HTTPS con Let’s Encrypt.
•	Almacenamiento local (rutas en BD) + marca de agua obligatoria (asíncrona).
•	App Flutter (Android/iOS) con offline planificado (cache + colas de sync), notificaciones, deep links.
________________________________________
5) Requerimientos funcionales (divididos)
A. Multisede & Usuarios
•	N sedes; segregación por sede_id; Superadmin/Dueña ve todas, otros solo su sede.
•	Asignación única de sede por usuario.
•	Códigos de 6 para creación de cuentas (tutores, profes/auxiliares) con reglas de uso/expiración.
•	RBAC dinámico: permisos por vista y acción (ver, crear, editar, eliminar, exportar, ver_sensible).
•	Perfiles: foto, usuario único, cambio de contraseña (validaciones en tiempo real).
B. Inscripción & Formularios
•	Flujo de registro con WhatsApp link, formulario en pasos, autoguardado, documentos requeridos, firmas individuales, contrato membretado, file imprimible.
C. Académico
•	Grupos, paralelos, cupos, horarios con detector de conflictos (no duplicar profesora a misma hora).
•	Asistencia niños (estadística) y personal (P/F/R + hora).
•	Portafolio con actividad (5 fotos + 3 videos), consentimiento único, estados de procesamiento.
D. Administración & Finanzas
•	Categorías de pago por sede (mensualidad, material, merienda, almuerzos, cuidado por día, etc.).
•	Prorrateo y descuentos según reglas.
•	Pagos desde tabla de niños (ícono billete → modal de cobro).
•	Conciliación semanal; Libro de caja; Arqueo mensual (autogenerado el día 6).
•	Exportaciones PDF/Excel (tabla completa o columnas seleccionadas) + plantillas (libro caja, pagos por niño, etc.).
•	Planes de pago 3.400 Bs/año personalizables; estado de cuenta y amortización.
E. Inventario
•	Categorías y subcategorías dinámicas por sede; unidades (kg, l, unidad, caja, talla, etc.).
•	Sin evidencias ni aprobación de movimientos (política vigente).
•	SKU para ítems fijos, préstamos a personal; mínimos; alertas 5/3/1 días.
F. Comunicaciones & Notificaciones
•	Chat profesora↔tutor (+ Directora), adjuntos (img/PDF/DOCX ≤10 MB), inmutable.
•	Notificaciones persistentes, no borrables, agrupadas, leídas/no leídas; recordatorios de pago con programación.
G. Reportes & Gráficas
•	Dashboards con filtros (sede restringida por perfil), Chart.js.
•	Indicadores: ingresos/egresos/ganancias, inscritos por mes, nuevos inscritos, etc.
H. IA/Chat administrativo
•	Consultas sobre uso y datos del sistema (con anonimización y auditoría); proveedor y costos parametrizables (MCP).
I. Migraciones & Manuales
•	Importar históricos desde Excel; plantillas de importación/validación.
•	Módulo de ayuda/manual por rol.
________________________________________
6) Requerimientos no funcionales
•	Seguridad 100% foco: JWT híbrido, cookies seguras, CSRF, CORS mínimo, rate limit, hashing de contraseñas, validación estricta, logging/auditoría, control ver_sensible para alergias/medicación, anonimización al borrar.
•	Rendimiento: paginado en todos los listados, lazy load multimedia, índices y evitar N+1, colas asíncronas, respuestas compactas.
•	UX/UI: dark/light por usuario (persistir), accesible (focus/ARIA/contraste), textos claros en SweetAlert2.
•	Observabilidad: logs técnicos separados de mensajes al usuario; panel de Servicio Técnico (errores, métricas, workers, colas, sesiones).
•	Escalabilidad: hexagonal, repositorios por puerto, adapters aislados, contratos claros para futura escisión a microservicios.
•	Internacionalización: es BO, moneda y fechas locales.
________________________________________
7) Arquitectura técnica
•	Hexagonal: 
o	domain/ (entidades, agregados, value objects, casos de uso).
o	application/ (servicios orquestadores, DTOs, puertos).
o	infrastructure/ (adapters: repos SQLAlchemy, Redis, colas, almacenamiento, email/whatsapp link builder, IA).
o	interfaces/ (routers FastAPI /api/v1, WebSockets /ws/notifications, plantillas Jinja2).
•	Colas: watermark de multimedia, generación de PDFs/Excel, recordatorios programados (1/3/5 días antes del 10 a las 11/14/17).
•	Storage local + rutas en BD; estado de procesamiento; marca de agua asíncrona.
•	Autenticación híbrida: access (memoria) + refresh (cookie httpOnly).
________________________________________
8) Diseño de datos (instrucciones para ER 3FN/BCNF + enumeración mínima obligatoria)
Genera un modelo entidad relación normalizado (3FN o superior) que contemple, al menos, estas entidades y relaciones (agrega las derivadas necesarias):
•	Seguridad & auditoría: usuarios, roles, permisos, roles_permisos, usuarios_roles, sedes, sesiones, auditoria_acciones (ver/crear/editar/eliminar/exportar/ver_sensible, timestamp, IP, user_agent), tokens_revocados, preferencias_usuario (tema).
•	Comunicación de acceso: codigos_acceso (tipo: tutor/profesor/auxiliar, niño_id opcional, usos_permitidos/usados, expiracion, estado).
•	Académico: grupos (tipo grupo), paralelos, paralelos_profesoras (rol_en_grupo: titular/auxiliar), horarios, horarios_paralelos, cupos, alumnos, alumnos_paralelos, asistencia_alumnos, asistencia_personal, permisos_personal (bajas/justificativos), consentimientos (imagen/video, vigente, fecha).
•	Inscripción & Formularios: formularios_inscripcion (estado), formularios_respuestas, documentos_inscripcion (tipo, ruta, hash), firmas (quién, imagen, ip, timestamp), contratos (número por sede, plantilla_id, pdf_ruta).
•	Portafolio & Multimedia: actividades, actividad_media (tipo foto/video, watermark_status), reportes_diarios (por niño, estado por tutor), reporte_lecturas_tutores.
•	Pagos & Finanzas: categorias_pago, precios_turnos (por sede, vigencia), turnos, matriculas (si aplica por sede), pagos (metodo, monto, validacion_monto), comprobantes (ruta, hash), conciliaciones (estado: depositado/transferido/verificado, fecha), planes_pago (3.4k), planes_cuotas, estado_cuenta_nino, libro_caja, arqueos (PDF/Excel).
•	Inventarios: familias (Uniformes/Materiales/Ingredientes/Limpieza/Activos), categorias, items, items_atributos (talla/color/marca/unidad), stock_sede, movimientos_stock (sin evidencia), prestamos_uniformes (personal, fechas, estado), alertas_stock, alertas_vencimiento (config por sede 5/3/1).
•	Comunicaciones & Notificaciones: conversaciones (scope: tutor-profesora/directora), mensajes (inmutables), mensajes_adjuntos, notificaciones (persistentes), notificacion_vistas.
•	Cursos/Eventos extra: cursos_extra (precio_corporalizado por inscrito/externo/cupo), inscripciones_curso_extra, costos_curso_extra (categorías definidas por sede), balance_curso_extra.
•	IA & Auditoría IA: ia_consultas (prompt, usuario, filtros de anonimización aplicados, costo tokens, respuesta resumida, timestamp).
•	Importaciones: import_jobs (tipo origen: Excel/CuadernoRojo, estado, resumen, bitácora de errores).
Incluye claves, índices, constraints, soft delete donde aplique, y FK con ON UPDATE/DELETE adecuados.
________________________________________

20.	## Entrega de código 
o	Backend FastAPI (asincrónico, hexagonal, colas, websockets, seguridad híbrida, watermark).
o	Frontend Web (Jinja2 + Tailwind + JS ESM con fetch, SweetAlert2 entendible pars front y back, Chart.js, dark/light).
o	App Flutter (Android/iOS, capas limpias, BLoC/Riverpod, cache offline, sync queue, websockets, notificaciones).
o	Todos los archivos listos para correr (estructura, requirements.txt/pyproject.toml, pubspec.yaml, assets, plantillas, snippets Nginx/systemd, .env.example).
Incluye ejemplos prácticos de:
•	Respuestas de error amigables (mapeadas a SweetAlert2).
•	Paginación estándar (page, page_size, total).
•	Subida de archivos (valida extensión/tamaño, barra de progreso).
•	Notificación de stock/caducidad (push campanita + persistente).
•	Comprobante imprimible estilo SIN like (no integrado a SIN por ahora).
•	WhatsApp link builder (wa.me) y auditoría del intento de envío.
________________________________________
10) Seguridad y acceso (detalles a implementar)
•	JWT híbrido (access en memoria, refresh en cookie HttpOnly/Secure/SameSite=Strict), exp corto (5 15 min) y refresh duradero; endpoint de refresh + protección CSRF.
•	RBAC por vista/acción (ver, crear, editar, eliminar, exportar, ver_sensible); impersonar solo para Servicio Técnico si se habilita explícitamente.
•	Auditoría total: ver/editar/descargar/exportar, login/logout, generación de enlaces WhatsApp, intentos de importación/exportación, uso de IA.
•	Datos sensibles: ver_sensible requerido para alergias/medicación; visibilidad Directora y profesora encargada por defecto (extensible por permisos).
•	Política de retención: sin eliminación automática; notificar a 5 años; anonimización al eliminar.
•	Rate limit, CORS mínimo, validaciones estrictas, sanitización XSS, protección a file uploads (tipo/tamaño/antivirus opcional), hashing contraseñas.
________________________________________
11) Manejo de errores
•	Backend: respuestas JSON {code, message, details, field_errors?}; códigos de negocio claros (p. ej., PAYMENT_AMOUNT_MISMATCH, CODE_EXPIRED, RBAC_DENIED) Igual forma debe mostrarse con sweetalert2 de forma mas humana.
•	Frontend: SweetAlert2 traduce códigos a mensajes humanos, con acciones sugeridas.
•	Logging: separar logs técnicos de mensajes de UX.
________________________________________
12) Reglas de negocio confirmadas (aplícalas tal cual)
•	Códigos: 6 caracteres; tutor (máx. 2 cuentas o 1 si tutor único); profesora/auxiliar (1 uso).
•	WhatsApp: usuario ingresa 8 dígitos; sistema arma URL y audita.
•	Prorrateo: mensualidad/20; ≤3 días → siguiente mes; base = primera asistencia; redondeo boliviano (0.50/1.00).
•	Descuentos: 3% (medio año), 6% (año) solo mensualidad.
•	Pagos: adjunto obligatorio; validar monto vs sistema; hash antidual.
•	Conciliación: viernes → depositado/transferido/verificado.
•	Recordatorios: 1/3/5 días antes del 10 (11:00/14:00/17:00).
•	Planes 3.400: personalizable, sin interés por defecto (configurable).
•	Inventario: sin evidencias/aprobación; mínimos; caducidad 5/3/1; SKU y préstamos para uniformes; unidades por tipo.
•	Asistencia: niños (estadística); personal P/F/R + hora; reportes exportables.
•	Reportes diarios: requerido; si no a las 20:00, enviar al guardar; lectura por tutor con confirmación.
•	Multimedia: 5 fotos + 3 videos por actividad; watermark async; 10 MB/base (configurable).
•	Chat: inmutable; adjuntos img/PDF/DOCX ≤10 MB; búsquedas/filtros.
•	Notificaciones: persistentes, no borrables; agrupación y leído/no leído.
•	IA: solo Superadmin/Directora (extensible); anonimizar; auditar; limitar tokens/costos; proveedor configurable (MCP).
•	Retención: notificar a 5 años; anonimizar al borrar.
•	Migraciones: importar Excel y (si posible) Cuaderno Rojo.
________________________________________
13) Restricciones (NO hacer)
•	NO usar frameworks SPA (React/Vue/Angular).
•	NO usar jQuery/AJAX (solo fetch).
•	NO almacenar archivos en terceros (usar disco local).
•	NO omitir sede_id en entidades de negocio.
•	NO permitir eliminar notificaciones persistentes.
•	NO exponer tokens en localStorage.
•	NO romper inmutabilidad del chat.
________________________________________
14) Variables/Placeholders
{{nombre_sistema}}, {{dominio}}, {{sedes_iniciales}}=["CBB-CENTRO","ORU-CENTRO"], {{tema_default}}="light", {{limite_upload_mb}}=10, {{stock_minimo}}=5, {{dias_alerta_caducidad}}="5,3,1", {{proveedor_ia}}, {{politica_precios_afecta}}="solo_nuevos|todos".
________________________________________
15)	Finalmente, entrega todos los archivos: 
o	Backend FastAPI (asincrónico, hexagonal, Redis, Celery/RQ, websockets, JWT híbrido, watermark).
o	Frontend Web (Jinja2 + Tailwind + JS ESM, fetch, SweetAlert2, Chart.js, dark/light, lazy load, uploader).
o	App Flutter (Android/iOS, BLoC/Riverpod, offline cache + sync, websockets, notificaciones).
o	Snippets de despliegue (Nginx, systemd), .env.example, seeds (sedes/roles).
o	Usa Markdown y bloques de código; estructura clara; copiar/pegar listo para ejecutar.
o	No pidas confirmaciones intermedias; si detectas ambigüedad menor, elige la opción más segura por defecto y documenta la decisión.
________________________________________
✅ Bonus (guías de estilo –recomendado en la salida)
•	Python: tipado estático, Pydantic v2 para esquemas, repositorios con async/await, sesiones SQLAlchemy 2.0, transacciones por caso de uso, Unidad de Trabajo.
•	JS: módulos ESM, funciones puras, helpers centralizados de fetch (con reintentos/backoff para 5xx), IntersectionObserver para lazy load.
•	Flutter: carpetas presentation/, domain/, data/; BLoC con freezed/equatable o Riverpod; dio con interceptores JWT/refresh; sqflite/hive para cache/cola; connectivity_plus y reintentos exponenciales; temas dark/light.
 
Como ya sabes arma el prototipo del proyecto completo, Con todas las recomendaciones e instrucciones que se te dio.
Hazlo paso a paso como se indica. Mejor si esperas una confirmación que diga siguiente paso para mandar las cosas. Recuerda que al final me tienes que mandar el prototipo completo del proyecto para correr. Las historias de usuario estan cmpletas en historias_usuario.txt dentro de la carpeta raiz. De igual forma puedes pedirlas en cualquier momento sino estas seguro de algo. Las especificaciones tecnicas igual. Aunque aqui te las estoy especificando muy bien. Las historias de usuario aqui estan resumidas porsiacaso.
Quiero que todo el codigo que llegues a crear sea en espanol y manteniendo la estructura de nombres.

