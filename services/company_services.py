import discord
import random
import logging
from config.roles import ROLE_ENCARGADO_EMPRESAS, ROLE_REPRESENTANTE_EMPRESA
from config.channels import CATEGORIA_EMPRESAS_ID
from database.repositories.company_repository import guardar_empresa, obtener_empresa_por_rol_id, eliminar_empresa_bd

async def _crear_rol_empresa(guild: discord.Guild, nombre_empresa: str) -> discord.Role:
    rol = await guild.create_role(
        name=nombre_empresa,
        hoist=True,
        color=discord.Color.from_rgb(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        ),
        reason="Creación automática de empresa"
    )
    try:
        await rol.edit(position=guild.me.top_role.position - 0) # Cambiar depende de la posicion en la lista que quieras
    except discord.HTTPException as e:
        logging.warning(f"No se pudo reposicionar el rol de empresa '{nombre_empresa}': {e}")

    return rol


async def _crear_canal_empresa(
    guild: discord.Guild, nombre_empresa: str, rol_empresa: discord.Role) -> discord.TextChannel:
    categoria = guild.get_channel(CATEGORIA_EMPRESAS_ID)
    rol_encargado = guild.get_role(ROLE_ENCARGADO_EMPRESAS)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        rol_empresa: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        rol_encargado: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    return await guild.create_text_channel(
        name=nombre_empresa.lower().replace(" ", "-"),
        category=categoria,
        overwrites=overwrites
    )


async def crear_empresa(guild: discord.Guild, data: dict) -> dict:
    """
    Orquesta la creación de una empresa: roles, canal y persistencia en BD.

    Espera en `data`:
        dueño_empresa (str): ID de Discord del dueño.
        nombre_empresa (str): Nombre de la empresa.

    Lanza:
        ValueError: si ya existe un rol con ese nombre.
        RuntimeError: si falla algún paso (revierte lo creado en Discord).
    """
    if discord.utils.get(guild.roles, name=data["nombre_empresa"]):
        raise ValueError(f"Ya existe una empresa con el nombre '{data['nombre_empresa']}'.")


    rol_empresa = None
    canal_empresa = None

    try:
        rol_representante = guild.get_role(ROLE_REPRESENTANTE_EMPRESA)
        rol_empresa = await _crear_rol_empresa(guild, data["nombre_empresa"])

        miembro = await guild.fetch_member(int(data["dueño_empresa"]))
        await miembro.add_roles(rol_representante, rol_empresa)

        canal_empresa = await _crear_canal_empresa(guild, data["nombre_empresa"], rol_empresa)

        data["rol_id"] = str(rol_empresa.id)
        data["canal_id"] = str(canal_empresa.id)

        empresa = guardar_empresa(data)
        if not empresa:
            raise RuntimeError("Error al guardar la empresa en la base de datos.")

        return empresa

    except Exception as e:
        logging.error(f"Error creando empresa '{data.get('nombre_empresa')}': {e}")
        if canal_empresa:
            await canal_empresa.delete()
        if rol_empresa:
            await rol_empresa.delete()
        raise

async def eliminar_empresa(guild: discord.Guild, rol_id: str, canal_interaccion: discord.abc.Messageable | None=None) -> bool:
    """
    Orquesta el borrado de una empresa a partir del rol mencionado: quita roles al dueño,
    borra canal, borra rol y elimina el registro de la base de datos.

    Lanza:
        ValueError: si no existe ninguna empresa asociada a ese rol.
        RuntimeError: si falla el borrado en base de datos tras limpiar Discord.
    """
    empresa = obtener_empresa_por_rol_id(rol_id)
    if not empresa:
        raise ValueError("Ese rol no corresponde a ninguna empresa registrada.")

    if canal_interaccion and str(canal_interaccion.id) == empresa["canal_id"]:
        raise ValueError(
            "No puedes eliminar la empresa desde su propio canal, ejecuta el comando desde otro canal."
        )

    rol_empresa = guild.get_role(int(empresa["rol_id"]))
    canal_empresa = guild.get_channel(int(empresa["canal_id"]))
    rol_representante = guild.get_role(ROLE_REPRESENTANTE_EMPRESA)

    try:
        miembro = await guild.fetch_member(int(empresa["dueño_empresa"]))
        roles_a_quitar = [r for r in (rol_empresa, rol_representante) if r and r in miembro.roles]
        if roles_a_quitar:
            await miembro.remove_roles(*roles_a_quitar)
    except discord.NotFound:
        logging.warning(f"El dueño de la empresa '{empresa['nombre_empresa']}' ya no está en el servidor o no lo he encontrado.")

    if canal_empresa:
        try:
            await canal_empresa.delete(reason="Eliminación de empresa")
        except discord.HTTPException as e:
            logging.error(f"No se pudo borrar el canal de la empresa '{empresa['nombre_empresa']}': {e}")
            raise RuntimeError("No se pudo eliminar el canal de la empresa en Discord, consulta con el administrador.")
    else:
        logging.warning(f"El canal de la empresa '{empresa['nombre_empresa']}' ya no existía.")

    if rol_empresa:
        try:
            await rol_empresa.delete(reason="Eliminación de empresa")
        except discord.HTTPException as e:
            logging.error(f"No se pudo borrar el rol de la empresa '{empresa['nombre_empresa']}': {e}")
            raise RuntimeError("No se pudo eliminar el rol de la empresa en Discord, consulta con un administrador.")
    else:
        logging.warning(f"El rol de la empresa '{empresa['nombre_empresa']}' ya no existía en Discord.")

    exito = eliminar_empresa_bd(empresa["empresa_id"])
    if not exito:
        raise RuntimeError(
            "Se eliminó la empresa de Discord pero hubo un error al borrar el registro en la base de datos."
        )

    return True