from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.bot import ahorcado, juegos, texts
from src.bot.formatters import formatear_resultado
from src.bot.handlers import buscar_palabra_del_dia, obtener_pista


def _menu_keyboard(suscrito_palabra_dia: bool) -> InlineKeyboardMarkup:
    boton_palabra_dia = (
        InlineKeyboardButton("🔕 Desactivar palabra del día", callback_data="francis_menu:palabradia_off")
        if suscrito_palabra_dia
        else InlineKeyboardButton("🔔 Activar palabra del día", callback_data="francis_menu:palabradia_on")
    )
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Cómo consultarme", callback_data="francis_menu:ayuda")],
        [InlineKeyboardButton("🦉 Acerca de Francis", callback_data="francis_menu:acerca")],
        [boton_palabra_dia],
    ])


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(texts.BIENVENIDA)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(texts.AYUDA)


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data.get("db")
    suscrito = db.esta_suscrito_palabra_dia(update.effective_user.id) if db is not None else False
    await update.message.reply_text("🦉 ¿En qué puedo servirle?", reply_markup=_menu_keyboard(suscrito))


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    db = context.bot_data.get("db")
    accion = (query.data or "").split(":", 1)[-1]
    if accion == "ayuda":
        await query.message.reply_text(texts.AYUDA)
    elif accion == "acerca":
        await query.message.reply_text(texts.ACERCA_DE)
    elif accion in ("palabradia_on", "palabradia_off") and db is not None:
        user_id = update.effective_user.id
        if accion == "palabradia_on":
            db.suscribir_palabra_dia(user_id)
        else:
            db.desuscribir_palabra_dia(user_id)
        suscrito = db.esta_suscrito_palabra_dia(user_id)
        await query.edit_message_reply_markup(reply_markup=_menu_keyboard(suscrito))
        await query.message.reply_text(
            texts.PALABRA_DIA_SUSCRITO if suscrito else texts.PALABRA_DIA_DESUSCRITO
        )


def _favoritos_keyboard(favoritos: list[str]) -> InlineKeyboardMarkup:
    filas = [
        [InlineKeyboardButton(f"🗑 Quitar \"{palabra}\"", callback_data=f"francis_fav:quitar:{palabra}")]
        for palabra in favoritos
    ]
    return InlineKeyboardMarkup(filas)


async def favoritos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data.get("db")
    favoritos = db.listar_favoritos(update.effective_user.id) if db is not None else []
    if not favoritos:
        await update.message.reply_text(
            "🦉 Aún no tiene palabras guardadas en sus favoritos. Cuando le "
            "sirva una definición, use el botón \"⭐ Guardar en favoritos\"."
        )
        return
    lista = "\n".join(f"• {palabra}" for palabra in favoritos)
    await update.message.reply_text(
        f"🦉 Sus palabras favoritas:\n\n{lista}",
        reply_markup=_favoritos_keyboard(favoritos),
    )


async def historial_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data.get("db")
    historial = db.listar_historial(update.effective_user.id) if db is not None else []
    if not historial:
        await update.message.reply_text("🦉 Todavía no hemos conversado sobre ninguna palabra.")
        return
    lista = "\n".join(f"• {palabra}" for palabra in historial)
    await update.message.reply_text(f"🦉 Sus últimas palabras consultadas:\n\n{lista}")


async def favorito_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    db = context.bot_data.get("db")
    if db is None:
        return

    _, accion, palabra = (query.data or "").split(":", 2)
    user_id = update.effective_user.id

    if accion == "add":
        db.agregar_favorito(user_id, palabra)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"🦉 Guardado \"{palabra}\" en sus favoritos. ⭐")
    elif accion == "quitar":
        db.quitar_favorito(user_id, palabra)
        favoritos = db.listar_favoritos(user_id)
        if favoritos:
            await query.edit_message_text(
                "🦉 Sus palabras favoritas:\n\n" + "\n".join(f"• {p}" for p in favoritos),
                reply_markup=_favoritos_keyboard(favoritos),
            )
        else:
            await query.edit_message_text(
                "🦉 Ya no le quedan palabras guardadas en sus favoritos."
            )


async def palabra_del_dia_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    encontrada = buscar_palabra_del_dia()
    if encontrada is None:
        await update.message.reply_text(texts.ERROR_SERVICIO)
        return
    concepto, resultado_rae, resultado_wikcionario = encontrada
    mensaje = formatear_resultado(concepto, resultado_rae, resultado_wikcionario)
    await update.message.reply_text(
        f"{texts.PALABRA_DEL_DIA_INTRO}\n\n{mensaje}", parse_mode="Markdown"
    )


async def suscribir_palabra_dia_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data.get("db")
    if db is None:
        return
    db.suscribir_palabra_dia(update.effective_user.id)
    await update.message.reply_text(texts.PALABRA_DIA_SUSCRITO)


async def cancelar_palabra_dia_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = context.bot_data.get("db")
    if db is None:
        return
    db.desuscribir_palabra_dia(update.effective_user.id)
    await update.message.reply_text(texts.PALABRA_DIA_DESUSCRITO)


async def ahorcado_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mensaje, teclado = ahorcado.iniciar_juego(context.user_data)
    await update.message.reply_text(mensaje, reply_markup=teclado)


async def ahorcado_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    partes = (query.data or "").split(":", 2)
    accion = partes[1] if len(partes) > 1 else ""

    if accion == "letra":
        letra = partes[2]
        mensaje, teclado, terminado = ahorcado.procesar_letra(context.user_data, letra)
        await query.edit_message_text(mensaje, reply_markup=teclado)
    elif accion == "pista":
        palabra = ahorcado.palabra_actual(context.user_data)
        if palabra is None:
            await query.message.reply_text(texts.AHORCADO_SIN_JUEGO)
            return
        pista = obtener_pista(palabra)
        await query.message.reply_text(pista or texts.AHORCADO_SIN_PISTA)
    elif accion == "rendirse":
        mensaje = ahorcado.rendirse(context.user_data)
        await query.edit_message_text(mensaje)


async def juegos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(texts.JUEGOS_INTRO, reply_markup=juegos.teclado_categorias())


async def juegos_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    partes = (query.data or "").split(":", 2)
    accion = partes[1] if len(partes) > 1 else ""

    if accion == "categorias":
        await query.edit_message_text(texts.JUEGOS_INTRO, reply_markup=juegos.teclado_categorias())
    elif accion == "cat":
        categoria_id = partes[2]
        nombre = juegos.nombre_categoria(categoria_id)
        teclado = juegos.teclado_juegos_de_categoria(categoria_id)
        descripciones = juegos.texto_juegos_de_categoria(categoria_id)
        if nombre is None or teclado is None or descripciones is None:
            await query.edit_message_text(texts.JUEGOS_CATEGORIA_VACIA, reply_markup=juegos.teclado_categorias())
            return
        await query.edit_message_text(
            f"🦉 {nombre}\n\n{descripciones}\n\nElija un juego:", reply_markup=teclado
        )
    elif accion == "juego":
        juego_id = partes[2]
        resultado = juegos.iniciar_juego(context.user_data, juego_id)
        if resultado is None:
            await query.edit_message_text(texts.JUEGOS_CATEGORIA_VACIA, reply_markup=juegos.teclado_categorias())
            return
        mensaje, teclado = resultado
        await query.edit_message_text(mensaje, reply_markup=teclado)
    elif accion == "siguiente":
        mensaje, teclado, _ = juegos.siguiente_prompt(context.user_data)
        await query.edit_message_text(mensaje, reply_markup=teclado)
    elif accion == "salir":
        mensaje = juegos.salir_juego(context.user_data)
        await query.edit_message_text(mensaje)
