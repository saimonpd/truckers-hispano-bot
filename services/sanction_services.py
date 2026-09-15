import discord
import logging

from database.repositories.sanction_repository import (
    add_sanction,
    delete_sanction,
    get_sanction,
    user_sanctions,
)
from ui.embeds.sanction_builder import (
    sanction_confirmation_delete_embed,
    sanction_list_embed,
)

log = logging.getLogger("sanctions")


async def sanction_register(bot: discord.Client, data: dict) -> str:
    mod_id = data.get("mod")
    usuario_id = data.get("usuario")
    razon = data.get("razon")

    sancion_id = add_sanction(mod_id, usuario_id, razon)

    if sancion_id:
        return f"Sancion registrada correctamente (ID: {sancion_id})"
    else:
        log.error(f"SANCTION | No se ha podido registrar la sancion de {usuario_id}")
        return "No se ha podido registrar la sancion"


async def sanction_delete(bot: discord.Client, data: dict):
    """
    No borra directamente: recoge la sancion, construye el embed de confirmacion
    y la view con los botones. El borrado real ocurre en sanction_delete_confirm,
    invocado desde la view al pulsar "Confirmar".
    """
    # Import diferido para evitar dependencia circular con la view
    from ui.views.sanction_view import sanction_confirmation_delete_view

    id_sancion = data.get("id_sancion")

    sancion = get_sanction(id_sancion)
    if not sancion:
        log.warning(f"SANCTION | Se intento eliminar la sancion {id_sancion} pero no existe")
        return "Esa sancion no existe"

    embed = sanction_confirmation_delete_embed(sancion)
    view = sanction_confirmation_delete_view(data={"id_sancion": id_sancion, "mod": data.get("mod")})

    return {"embed": embed, "view": view}


async def sanction_delete_confirm(id_sancion: int) -> str:
    """
    Ejecuta el borrado real tras la confirmacion del usuario desde la view.
    """
    eliminado = delete_sanction(id_sancion)

    if eliminado:
        return "Sancion eliminada correctamente"
    else:
        return "No se ha podido eliminar la sancion (puede que ya no exista)"


async def sanction_list(bot: discord.Client, data: dict):
    usuario_id = data.get("usuario")

    sanciones = user_sanctions(usuario_id)

    if not sanciones:
        return "Este usuario no tiene sanciones registradas"

    embed = sanction_list_embed({"usuario_id": usuario_id, "sanciones": sanciones})
    return {"embed": embed}