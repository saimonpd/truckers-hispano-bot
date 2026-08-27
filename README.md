# Truckers Hispano BOT
Un bot de Discord diseñado para automatizar tareas repetitivas y la gestión de la comunidad, facilitando el trabajo de los moderadores y mejorando la experiencia general de los usuarios.

## Funcionalidades

### Sistema de Bienvenida
Cuando un nuevo miembro se une al servidor, el bot automáticamente:
- Asigna un rol por defecto (`AUTO_ROLE_ID`)
- Envía un mensaje de bienvenida con embed
- Muestra un conjunto persistente de botones con enlaces (Web, Instagram, YouTube, Twitter, TikTok)

**Flujo:**
```
on_member_join (cog Welcome)
   → WelcomeService.handle_new_member()
        → _assign_role()            [asigna AUTO_ROLE_ID, maneja discord.Forbidden]
        → _send_welcome_message()   [construye embed + WelcomeView, envía a CHANNEL_WELCOME]
```

### Sistema de Eventos
Permite a los encargados crear eventos en el servidor, publicarlos como un embed interactivo en un canal fijo, y que los miembros se apunten o desapunten directamente desde los botones del mensaje, sin necesidad de comandos adicionales.

**Comando:** `/crear_evento` — Solo disponible para el rol `ENCARGADO_EVENTOS`.

**Parámetros obligatorios:** `titulo`, `descripcion`, `juego`, `servidor`, `organizador`, `fecha` (`DD/MM/YYYY`), `hora_reunion` (`HH:MM`), `hora_salida` (`HH:MM`), `ruta_origen`, `ruta_destino`.

**Parámetros opcionales:** `link_trucksbook`, `link_truckersmp`, `parada_intermedio`, `dlcs_requeridos`, `carga`, `trailer`, `ruta_imagen`.

**Flujo de creación:**
```
/crear_evento (comando)
   → validar_tiempos_evento()       [valida fecha/hora, genera timestamps Discord]
   → create_event() [servicio]
        → build_event_embed()       [construye el embed]
        → EventView(...)            [construye los botones de link]
        → channel.send(embed, view) [publica en Discord]
        → save_event()              [persiste en BD, incluyendo message_id]
```

**Flujo de apuntarse/desapuntarse:**
```
Usuario pulsa "✅ Apuntarse / Desapuntarse"
   → toggle_participacion() [servicio]
        → obtener_datos_evento()          [lee el evento de BD]
        → validar_tiempos_evento()        [recalcula timestamps Discord — no se guardan en BD]
        → obtener_lista_ids_evento()      [comprueba si el usuario ya está apuntado]
        → modificar_participantes_evento() [INSERT o DELETE en participantes_evento]
        → build_event_embed()             [reconstruye el embed con la lista actualizada]
   → interaction.message.edit(embed=nuevo_embed)
```

**Reglas de negocio (validación de fechas — `utils/validators/date_validator.py`):**
- La fecha debe cumplir el patrón `DD/MM/YYYY` y la hora `HH:MM` en formato 24h, validados por regex (`_persear_fechahora`) antes de intentar convertirlos a `datetime`.
- Además de la sintaxis, se valida que la fecha exista realmente en el calendario (p. ej. `31/02/2026` pasa el regex pero falla al construir el `datetime`, y se traduce a un `ValueError` legible).
- La fecha/hora de reunión (`dt_reunion`) no puede ser anterior al momento actual (`datetime.now()`).
- La hora de salida (`dt_salida`) debe ser estrictamente posterior a la hora de reunión.
- Si toda la validación pasa, `validar_tiempos_evento()` devuelve un `dict` con los `datetime` (`dt_reunion`, `dt_salida`), los timestamps Unix (`ts_reunion`, `ts_salida`) y las cadenas ya formateadas para Discord (`discord_reunion` en formato `<t:...:F> (<t:...:R>)`, `discord_salida` en formato `<t:...:t>`).

**Timestamps de Discord:** los campos `discord_reunion` y `discord_salida` no se persisten en la base de datos — solo se guardan `fecha`, `hora_reunion` y `hora_salida` como texto plano. Los timestamps se recalculan cada vez que se reconstruye el embed, garantizando que nunca queden desactualizados.

**Concurrencia:** para evitar condiciones de carrera cuando varios usuarios pulsan "Apuntarse" casi a la vez sobre el mismo evento, se mantiene un `asyncio.Lock` por `message_id` (no uno global), de forma que eventos distintos se procesan en paralelo sin bloquearse entre sí.

**Manejo de errores:** se distingue entre errores de negocio (`ValueError`, con mensaje pensado para el usuario) y errores técnicos (`RuntimeError`, registrados internamente con `log.error()`, mostrando al usuario un mensaje genérico sin exponer detalles internos).

### Sistema de Moderación
Comandos de administración restringidos por permisos nativos de Discord (no por rol específico, sino por el permiso asociado: `kick_members`, `ban_members`, `mute_members`, `manage_nicknames`).

| Comando | Permiso requerido | Descripción |
|---|---|---|
| `/admin_kick` | `kick_members` | Expulsa a un usuario del servidor |
| `/admin_ban` | `ban_members` | Banea a un usuario del servidor |
| `/admin_aislar` | `mute_members` | Aísla (timeout) a un usuario durante N minutos |
| `/admin_editarnombre` | `manage_nicknames` | Cambia el nickname de un usuario y le notifica por MD |

**Flujo (ejemplo `/admin_kick`):**
```
/admin_kick (comando, cog Admin)
   → moderation_services.kick()   [ejecuta usuario.kick() con razón + moderador]
   → safe_send()                  [responde al staff, ephemeral por defecto]
```

Todos los comandos capturan de forma diferenciada:
- `discord.Forbidden` → el bot no tiene permisos suficientes (log.warning + aviso al staff)
- `discord.HTTPException` → fallo de red o de la API de Discord (log.error + aviso genérico)
- `Exception` genérica → red de seguridad final para no dejar interacciones colgadas

`/admin_editarnombre` además envía un MD al usuario afectado informando del cambio; si el usuario tiene los MDs cerrados, se captura `discord.Forbidden` sin romper el flujo principal.

### Sistema de Empresas
Permite a los encargados registrar empresas de la comunidad directamente desde Discord: se asigna un rol de representante y un rol propio de la empresa al dueño, se crea un canal privado visible solo para la empresa y el equipo encargado, y se persiste el registro en base de datos. También permite eliminar una empresa revirtiendo todo lo anterior.

**Comandos:** `/registrar_empresa` y `/eliminar_empresa` — Ambos restringidos al rol `ROLE_ENCARGADO_EMPRESAS`.

**Parámetros de `/registrar_empresa`:** `nombre_empresa` (texto), `dueño_empresa` (mención de usuario).

**Parámetros de `/eliminar_empresa`:** `rol_empresa` (mención del rol de la empresa a eliminar).

**Flujo de creación:**
/registrar_empresa (comando)
→ crear_empresa() [servicio]
→ comprobación de nombre duplicado (discord.utils.get sobre guild.roles)
→ crear_rol_empresa() [crea el rol con color aleatorio y hoist=True]
→ miembro.add_roles() [asigna rol de empresa + ROLE_REPRESENTANTE_EMPRESA al dueño]
→ crear_canal_empresa() [canal privado bajo CATEGORIA_EMPRESAS_ID, visible para el rol de empresa y ROLE_ENCARGADO_EMPRESAS]
→ guardar_empresa() [persiste en BD: nombre, dueño, rol_id, canal_id]

**Flujo de eliminación:**
/eliminar_empresa (comando)
→ eliminar_empresa() [servicio]
→ obtener_empresa_por_rol_id() [recupera la empresa a partir del rol mencionado]
→ comprobación: el comando no puede ejecutarse desde el propio canal de la empresa
→ miembro.remove_roles() [quita el rol de empresa y el de representante al dueño]
→ canal_empresa.delete() [borra el canal]
→ rol_empresa.delete() [borra el rol]
→ eliminar_empresa_bd() [borra el registro de BD]


**Reglas de negocio:**
- No se puede registrar una empresa con un nombre que ya coincide con un rol existente en el servidor (comprobación previa a crear nada, evita duplicados).
- No se puede ejecutar `/eliminar_empresa` desde el propio canal de la empresa que se está eliminando: al borrarse el canal a mitad del comando, Discord invalida el contexto de la interacción y el mensaje de confirmación final fallaría con `discord.NotFound` (`Unknown Message`). El servicio lo valida explícitamente y lanza un `ValueError` legible antes de tocar nada.
- La empresa se identifica siempre por el rol mencionado (`rol_id`), no por nombre en texto libre, evitando ambigüedades por mayúsculas, espacios o nombres duplicados.

**Manejo de errores y reversión (rollback):** si falla cualquier paso de `crear_empresa()` después de haber creado el rol y/o el canal en Discord (por ejemplo, un error al guardar en BD), el servicio revierte lo ya creado —borra el canal y el rol— para no dejar recursos huérfanos en el servidor. En `eliminar_empresa()`, si el dueño ya no está en el servidor se registra un `warning` y se continúa con el resto de la limpieza en vez de abortar.

**Diseño de la capa de servicio:** al igual que en el sistema de eventos, `crear_empresa(guild, data)` y `eliminar_empresa(guild, rol_id, canal_interaccion)` reciben un `discord.Guild` (necesario para operar roles/canales) junto a tipos primitivos (`dict`, `str`), no objetos de comando o interacción — mismo patrón pensado para una futura reutilización desde una API.

## Arquitectura
El proyecto sigue una estructura por capas para mantener separada la lógica de Discord de la lógica de negocio:

```
main.py                      -> Entry point: intents, setup_hook, carga de cogs y vistas persistentes
cogs/
    commands/                -> Comandos de barra (slash commands), delegan en services/
        admin.py                 (moderación)
        events.py                (creación de eventos)
        company.py               (registro y eliminacion de empresas)
    systems/                 -> Escucha eventos de Discord (on_member_join, etc.), delega en services/
        welcome.py
services/                    -> Lógica de negocio, independiente de discord.py en su interfaz pública
    events_services.py
    welcome_services.py
    moderation_services.py
    company_services.py
database/
    connection.py            -> Pool de conexiones (mariadb.ConnectionPool)
    repositories/            -> Único punto de acceso a la base de datos
        event_repository.py
        compnay_repository.py
ui/
    embeds/                  -> Constructores de embeds (lógica de presentación de mensajes)
    views/                   -> Componentes de interfaz de Discord (botones, vistas persistentes)
utils/
    validators/              -> Validación de datos y reglas de negocio (fechas, formatos, etc.)
    dm_utils.py              -> Envío de mensajes directos
    safe_send.py             -> Envío de respuestas a interacciones a prueba de fallos (expiración, HTTPException)
    startup_checks.py        -> Comprobaciones de arranque.
config/                      -> Configuración centralizada (config.py, channels.py, roles.py)
```

¿Por qué esta arquitectura?
- El único trabajo de los cogs/commands es escuchar un evento o comando de Discord y delegarlo a un servicio.
- Los `services` contienen la lógica de negocio real y reciben/devuelven en su mayoría tipos primitivos (`dict`, `str`, `int`) en lugar de objetos de `discord.py`, para no acoplar la lógica de negocio a la capa de Discord.
- Los `repositories` son el único punto de acceso a la base de datos: ninguna otra capa ejecuta queries directamente.
- Los `embeds` son funciones puras: reciben un `dict` de datos y devuelven un `discord.Embed`, sin acceder a la base de datos ni a Discord.
- Las `views` solo gestionan la interacción (botones, locks de concurrencia) y delegan la lógica en los services.

Los cogs se cargan automáticamente en `main.py` escaneando recursivamente el directorio `cogs/`, y las vistas persistentes se registran en `setup_hook` para evitar fallos de interacción después de un reinicio del bot.

### Diseño orientado a futuro (Web + API)
La separación en capas no es solo orden interno: está pensada para que, más adelante, se pueda montar una API (por ejemplo con FastAPI) y/o una web que compartan la misma lógica de negocio que el bot, en lugar de duplicarla.

Puntos concretos que ya lo permiten hoy:
- **`services/` como contrato estable.** Por ejemplo, `create_event(bot, data)` recibe un `dict` plano (no un `discord.Interaction` ni un `app_commands.Choice`), igual que `toggle_participacion(message_id, discord_id, nombre)`. Un futuro endpoint web solo necesita construir ese mismo `dict` a partir de un formulario y llamar al servicio — sin reescribir la lógica de creación de eventos ni la validación de fechas.
- **`utils/validators/` es reutilizable tal cual.** `validar_tiempos_evento()` no depende de Discord ni recibe nada de `discord.py`; puede llamarse igual desde un endpoint HTTP para validar un formulario antes de guardar, devolviendo el mismo `dict` con `datetime`, timestamps Unix y las cadenas de formato Discord. Nota para la futura API: la comparación `dt_reunion < datetime.now()` usa la hora local del servidor donde corra el proceso (no hay timezone-awareness ni offset por usuario); si la API se despliega en un servidor con otra zona horaria que el bot, conviene revisarlo para evitar validaciones inconsistentes entre ambos.
- **`database/repositories/` es el único punto de acceso a BD.** Una API reutilizaría directamente `event_repository.py` sin duplicar queries ni definir un segundo modelo de datos.
- **Los embeds están aislados.** Al ser funciones puras (`dict` → `discord.Embed`), la lógica de presentación de Discord nunca se mezcla con lo que necesitaría devolver una API en JSON.

Punto de fricción a tener en cuenta: `create_event()` sigue recibiendo el objeto `bot` para publicar el evento en el canal de Discord (dentro de `_publish_on_discord()`, ya aislada como función privada). Si en el futuro se quiere crear un evento desde la web sin pasar por el bot (o el bot y la API corren como procesos separados), este es el único punto que habría que desacoplar — separando "guardar en BD" de "publicar en Discord" como dos pasos independientes que la API pueda orquestar según el caso.

El sistema de empresas sigue el mismo contrato: `crear_empresa(guild, data)` recibe `data` como `dict` plano (`nombre_empresa`, `dueño_empresa`), igual que `eliminar_empresa(guild, rol_id, canal_interaccion=None)` recibe primitivos en vez de un `discord.Interaction`. El único acoplamiento a Discord que permanece —igual que en eventos— es la necesidad de un `discord.Guild` real para poder crear/borrar roles y canales, ya que esa parte de la lógica no tiene sentido fuera de Discord.

## Comprobaciones de arranque (Startup Checks)
Justo después de que el bot se conecta (`on_ready`), y tras haber cargado todos los cogs y sincronizado los slash commands en `setup_hook`, se ejecuta `run_startup_checks()` (`utils/startup_checks.py`). Es un "smoke test" contra el entorno real, pensado para detectar en el arranque —y no en producción, a mitad de una interacción de un usuario— que algo de la configuración no encaja con lo que hay realmente en Discord o en la base de datos.

**Comprobaciones realizadas:**
- **Base de datos**: obtiene una conexión del pool y ejecuta `SELECT 1` para confirmar que la BD responde.
- **Canales** (`CHANNEL_WELCOME`, `CHANNEL_EVENTS`): confirma que cada ID configurado corresponde a un canal real y accesible por el bot (usa `get_channel` y recurre a `fetch_channel` si no está en caché).
- **Roles** (`AUTO_ROLE_ID`, `ENCARGADO_EVENTOS`, `ROLE_NOTIFICACION_EVENTOS`): se comprueban por cada servidor en el que el bot ya está presente al arrancar, ya que un rol pertenece a un servidor concreto.
- **Roles de empresas** (`ROLE_ENCARGADO_EMPRESAS`, `ROLE_REPRESENTANTE_EMPRESA`): comprobados igual que el resto de roles, por cada servidor en el que el bot está presente.
- **Categoría de empresas** (`CATEGORIA_EMPRESAS_ID`): confirma que la categoría configurada existe y es accesible, reutilizando la misma comprobación que los canales (`get_channel`/`fetch_channel`), ya que una categoría es también un tipo de canal en discord.py.
- **Permisos del bot** (`manage_roles`, `manage_channels`): confirma que el rol del bot tiene estos permisos a nivel de servidor, necesarios para crear/editar/borrar roles y canales de empresas. No cubre la jerarquía de roles (que el rol del bot esté por encima del rol que crea), ya que eso depende de la posición relativa en el momento de cada operación y no de un permiso fijo; ese caso puntual se maneja con un `try/except discord.HTTPException` en `crear_rol_empresa()`.
- **Vistas persistentes**: confirma por nombre de clase que `EventView` quedó registrada en `bot.persistent_views`, para detectar antes de tiempo el escenario en el que sus botones ("🔔 Avisos Eventos", "✅ Apuntarse / Desapuntarse") dejarían de responder tras un reinicio. `WelcomeView` queda fuera de esta comprobación a propósito: al estar formada solo por botones `discord.ButtonStyle.link`, no lleva `custom_id` y Discord no la necesita "recordar" tras un reinicio (un botón de tipo link abre una URL sin pasar por el bot), así que nunca aparecerá en `bot.persistent_views` aunque esté correctamente registrada con `add_view()`.
- **Slash commands**: confirma que el árbol de comandos no está vacío antes de darse por sincronizado.

**Comportamiento ante fallos:** cada comprobación se registra individualmente en el log (`✅`/`❌`) con el motivo del fallo si lo hay. Si alguna comprobación crítica falla, el bot **no se detiene** —sigue funcionando, ya que en muchos casos preferimos que el bot siga dando servicio en lo que sí funciona antes que caerse por completo— pero el mensaje final de arranque cambia de "todas las comprobaciones pasaron correctamente" a un aviso explícito de que hay que revisar la configuración antes de dar el servicio por operativo.

**Por qué se ejecuta en `on_ready` y no en `setup_hook`:** `bot.guilds` (y por tanto los roles de cada servidor) todavía no está poblado durante `setup_hook`, ya que el bot aún no ha terminado de conectarse al gateway de Discord. Las comprobaciones de canales y roles necesitan ese caché ya disponible para dar un resultado fiable.

> Esto complementa pero no sustituye a un test suite (`pytest`) para la lógica de negoción pura en `services/` y `utils/validators/`. Los startup checks verifican que el *entorno* (BD, canales, roles) es correcto en el momento del arranque; un test suite verificaría que el *código* (p. ej. `validar_tiempos_evento()`) se comporta bien ante distintos casos, sin necesidad de un servidor de Discord real ni de una base de datos.

## Logging
El proyecto usa el módulo `logging` de Python de forma consistente en todas las capas — nunca `print()`. La configuración global se hace una sola vez, en `main.py`:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
```

**Convención de loggers:** cada módulo obtiene su propio logger con nombre descriptivo (`logging.getLogger("events")`, `logging.getLogger("database")`, `logging.getLogger("dm_utils")`, etc.) en vez de usar el logger raíz. Esto permite identificar de un vistazo en qué capa ocurrió cada línea del log, y en el futuro permitiría subir/bajar el nivel de un módulo concreto sin tocar el resto (por ejemplo, silenciar `discord.gateway` mientras se deja `events` en `DEBUG`).

**Convención de niveles:**
- `log.info(...)` — operaciones normales que conviene poder auditar: un evento creado, un usuario apuntándose/desapuntándose, un kick/ban ejecutado, la configuración cargada correctamente.
- `log.warning(...)` — situaciones anómalas pero esperables, que no impiden seguir funcionando: un usuario con los MDs cerrados, falta de permisos puntual, un intento de apuntarse a un evento que ya no existe.
- `log.error(...)` — fallos reales que requieren atención: excepciones de BD, fallos de la API de Discord, estados inconsistentes (p. ej. un evento publicado en Discord que no llegó a guardarse en BD).

**Regla de oro seguida en todo el proyecto: ningún `except` se deja vacío ni devuelve un valor por defecto sin registrar antes qué ha pasado.** Antes de esta revisión, `utils/dm_utils.py` capturaba cualquier excepción y devolvía `False` en silencio; ahora cada rama del `except` deja constancia en el log del motivo exacto del fallo, distinguiendo el caso esperado (MDs cerrados, `warning`) del caso inesperado (`error`).

**Capas con logging reforzado en esta revisión:**
- `database/connection.py`: registra la inicialización del pool y, si falla, el motivo antes de relanzar la excepción (evita que el bot arranque con una BD inaccesible sin que quede rastro de por qué).
- `config/config.py`: registra qué variable de entorno falta antes de lanzar el `ValueError` de fail-fast, tanto para `TOKEN` como para las variables de BD.
- `services/events_services.py`: antes no registraba nada; ahora deja rastro de cada evento creado, cada participante que se une/sale, y en particular del caso de estado inconsistente en el que un evento se publica en Discord pero falla al guardarse en BD (requiere intervención manual).
- `services/moderation_services.py`: registra cada acción de moderación ejecutada con éxito (kick, ban, timeout, cambio de nick), complementando los logs de fallo que ya existían en `cogs/commands/admin.py`.
- `utils/dm_utils.py`: distingue en el log entre "MD no entregado porque el usuario los tiene cerrados" (warning, esperado) y cualquier otro fallo (error, inesperado) — antes ambos casos eran indistinguibles y silenciosos.

## Configuración

### Variables de entorno (`.env`)
Basado en `.env.example`:

```
# DISCORD
TOKEN =

# DATABASE
DB_HOST =
DB_USER =
DB_PASSWORD =
DB_NAME =
DB_PORT =
```

`config/config.py` carga estas variables con `python-dotenv` y lanza un `ValueError` de forma inmediata si falta `TOKEN`, para detectar errores de configuración al arrancar y no en mitad de la ejecución.

### IDs del servidor
Deben actualizarse con los valores reales de tu servidor de Discord:

- `config/channels.py`: `CHANNEL_WELCOME`, `CHANNEL_EVENTS`, `CATEGORIA_EMPRESAS_ID`
- `config/roles.py`: `AUTO_ROLE_ID`, `ENCARGADO_EVENTOS`, `ROLE_NOTIFICACION_EVENTOS`, `ROLE_ENCARGADO_EMPRESAS`, `ROLE_REPRESENTANTE_EMPRESA`

### Base de datos
El bot usa MariaDB con un pool de conexiones (`mariadb.ConnectionPool`, tamaño 5) inicializado en `setup_hook` antes de cargar los cogs. Tablas utilizadas:
- `eventos` — un registro por evento, indexado por `message_id`
- `participantes_evento` — relación `message_id` ↔ `discord_id` de los usuarios apuntados
- `empresas` — un registro por empresa, con `nombre_empresa`, `dueño_empresa`, `rol_id` y `canal_id`

## Tecnologías
- Python 3.14
- discord.py
- mariadb (conector oficial, con connection pooling)
- logging
- python-dotenv

## Instalación y Configuración

Requisitos previos:
- Python 3.14
- Una aplicación de bot de Discord con el **Server Members Intent** activado en el Discord Developer Portal
- Una instancia de MariaDB accesible con las tablas `eventos`, `participantes_evento` y `empresas`

Instalación:
```
git clone https://github.com/<tu-usuario>/Discord-bot-Truckers-Hispano.git
cd Discord-bot-Truckers-Hispano
pip install -r requirements.txt
```

Configuración:
1. Crea tu archivo `.env` a partir de `.env.example` y rellena los valores de Discord y de la base de datos.
2. Actualiza `config/channels.py` y `config/roles.py` con los IDs correctos de tu servidor.

Ejecutar el bot:
```
python main.py
```

Al arrancar, el bot realiza los siguientes pasos:
1. Inicializa el pool de conexiones a la base de datos (`init_pool`)
2. Registra las vistas persistentes (`WelcomeView`, `EventView`)
3. Carga todos los cogs encontrados bajo `cogs/`
4. Sincroniza los comandos de barra (slash commands) con Discord
5. Se conecta y registra en el log: `Bot connected: <bot_name>`