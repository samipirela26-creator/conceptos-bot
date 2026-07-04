"""Personalidad de 'Francis la Búho': una dama erudita y refinada, de
modales impecables, que reside en su biblioteca privada dentro de "la
Lenovo" -la misma casa donde ya viven Larry (mayordomo/rana) y Coco
(banquero/cocodrilo). Habla siempre de usted, con calidez elegante y algo
de humor comedido -nunca estridente-. Estos textos SOLO enmarcan la
respuesta (saludos, avisos) -- el contenido de la definición en sí nunca
sale de aquí, siempre viene de RAE/Wikcionario (ver src/bot/formatters.py)."""
import random

BIENVENIDA = (
    "🦉 Un placer recibirle. Soy Francis, y resido en mi pequeña biblioteca "
    "dentro de la Lenovo -la misma casa donde ya atienden Larry, con su "
    "agenda, y Coco, con las cuentas-. A mí me corresponden las palabras.\n\n"
    "Tráigame cualquier concepto que le intrigue -directo, o en forma de "
    "pregunta- y le serviré dos versiones, como corresponde: la de la Real "
    "Academia Española, y una explicación llana, para el resto de los "
    "mortales.\n\n"
    "Por ejemplo: \"casa\", \"¿qué es la fotosíntesis?\", \"significado de ósmosis\"."
)

AYUDA = (
    "🦉 Con sumo gusto le explico cómo consultarme:\n\n"
    "• Escríbame la palabra directo: \"casa\"\n"
    "• O, si lo prefiere, en forma de pregunta: \"¿qué significa ósmosis?\"\n\n"
    "Respondo siempre con dos fuentes de mi entera confianza -jamás invento "
    "nada, sería de pésimo gusto-:\n"
    "📖 la definición formal de la Real Academia Española\n"
    "🔎 una explicación sencilla de Wikcionario\n\n"
    "Y si alguna palabra no figura en mis anaqueles, se lo diré con toda "
    "franqueza, en vez de improvisar."
)

ACERCA_DE = (
    "🦉 Soy Francis, y esta pequeña biblioteca dentro de la Lenovo es mi "
    "hogar -la misma casa donde ya atienden Larry, con su agenda, y Coco, "
    "con las cuentas-.\n\n"
    "Amo las palabras casi tanto como amo a Dios, de quien procede todo "
    "buen entendimiento. Por eso jamás invento una definición: todo lo que "
    "le sirvo sale de la Real Academia Española y de Wikcionario, tal cual "
    "lo escribieron.\n\n"
    "\"En el principio era el Verbo\" -y a mí me toca, con humildad, "
    "acercarle un poco de ese saber."
)

INTROS_RESULTADO = [
    "🦉 Aquí tiene, servido con gusto:",
    "🦉 Permítame consultar mis volúmenes... ya lo tengo:",
    "🦉 Un instante, por favor... listo:",
    "🦉 Con mucho gusto, esto encontré para usted:",
]

NO_ENCONTRADO = [
    "🦉 Lamento decirle que ni la RAE ni Wikcionario tienen registrada "
    "\"{palabra}\". ¿Segura está de la ortografía?",
    "🦉 Repasé mis anaqueles de cabo a rabo y \"{palabra}\" no aparece en "
    "ninguna de mis dos fuentes. Prefiero confesarlo a inventarle algo.",
]

SOLO_RAE = "🔎 Nota: Wikcionario no conserva entrada para esta palabra en español."
SOLO_WIKCIONARIO = "📖 Nota: la Real Academia no tiene entrada para esta palabra."

ERROR_SERVICIO = (
    "🦉 Disculpe usted, mis fuentes están de ánimo esquivo hoy (un problema "
    "de conexión). ¿Tendría la gentileza de intentarlo de nuevo en un momento?"
)

CHARLA = [
    "🦉 Buenas. Cuando guste, tráigame una palabra o concepto y con gusto se lo defino.",
    "🦉 A su servicio. Dígame qué palabra desea que le esclarezca.",
    "🦉 Aquí, entre mis libros, esperando su próxima palabra.",
]

TRABAJANDO = [
    "🦉 Un momento, por favor... aquí estoy, para servirle.",
    "🦉 Permítame un instante, ya voy a mis anaqueles a buscarle eso.",
    "🦉 Con gusto. Deme apenas un momento para consultar mis fuentes.",
    "🦉 Un momento, por favor... no tardo en tener su respuesta.",
]

TOQUE_DE_FE = [
    "\n\n_Toda palabra buena viene de lo alto, de Aquel que es la Palabra misma. Gloria a Dios._ ✨",
    "\n\n_Y el saber, con humildad, siempre nos acerca un poco más a Dios._ 🙏",
    "\n\n_Como está escrito: \"En el principio era el Verbo\" -toda palabra tiene su origen en Él._ 📖",
    "\n\n_Que este conocimiento le sirva, y que en todo demos gracias al Señor._ ✨",
    "\n\n_Bendito sea Dios, dador de todo buen entendimiento._ 🙏",
]

# Palabras curadas para la "palabra del día" -- solo son candidatas a
# buscarse; su definición real, como siempre, sale de RAE/Wikcionario.
PALABRAS_DEL_DIA = [
    "serendipia", "efímero", "melancolía", "ósmosis", "quimera", "epifanía",
    "nostalgia", "resiliencia", "empatía", "sutil", "ecuánime", "diáfano",
    "efervescente", "elocuente", "perspicaz", "ubicuo", "vernáculo",
    "idiosincrasia", "paradoja", "utopía", "sinergia", "letargo", "aurora",
    "efluvio", "candor", "sosiego", "algarabía", "vestigio", "epítome",
    "arcano", "lánguido", "gregario", "hosco", "pletórico",
]

PALABRA_DEL_DIA_INTRO = (
    "🦉 Buenos días. Hoy le traigo, de entre mis anaqueles, una palabra que "
    "bien merece su atención:"
)

PALABRA_DIA_SUSCRITO = (
    "🦉 Con sumo gusto. Cada mañana le llevaré, sin falta, una palabra de mis "
    "anaqueles."
)

PALABRA_DIA_DESUSCRITO = (
    "🦉 Como usted disponga. Ya no le enviaré la palabra del día -- pero sigo "
    "aquí, si alguna vez la quiere pedir con /palabradeldia."
)

# Palabras curadas para el juego del ahorcado -- lista propia, más extensa
# que PALABRAS_DEL_DIA, para que el juego no se sienta repetitivo. Se
# guardan con su ortografía correcta (tildes, ñ) porque también se usan
# para pedir la pista real a RAE/Wikcionario.
PALABRAS_AHORCADO = [
    "biblioteca", "murciélago", "cocodrilo", "jardín", "montaña", "estrella",
    "camino", "puente", "espejo", "relámpago", "tormenta", "desierto",
    "cascada", "horizonte", "sendero", "linterna", "brújula", "pergamino",
    "candelabro", "escalera", "campanario", "laberinto", "faro", "vitral",
    "manuscrito", "telaraña", "girasol", "colibrí", "mariposa", "delfín",
    "tiburón", "elefante", "jirafa", "leopardo", "águila", "serpiente",
    "tortuga", "ballena", "pingüino", "castillo", "torre", "fortaleza",
    "cascabel", "trueno", "arcoíris", "cometa", "eclipse", "constelación",
    "océano", "volcán", "biblia", "santuario", "oración", "milagro",
    "peregrino", "monasterio", "salterio", "profeta",
]

AHORCADO_INTRO = (
    "🦉 Ahorquemos una palabra, ¿le parece? Elija sus letras con calma -- "
    "y si se atasca, ahí tiene el botón de pista."
)

AHORCADO_GANADO = [
    "🦉 ¡Justo a tiempo! La adivinó sin agotar mi paciencia. Un placer jugar con usted.",
    "🦉 Excelente. Sabía que sus letras y su cabeza harían buen equipo.",
    "🦉 Bravo. Otra palabra rescatada de mis anaqueles gracias a usted.",
]

AHORCADO_PERDIDO = [
    "🦉 Ay, esta vez el ahorcado ganó la partida. No se aflija, la palabra era \"{palabra}\".",
    "🦉 Se nos escapó esta ronda -- la palabra era \"{palabra}\". ¿Probamos otra?",
]

AHORCADO_SIN_PISTA = "🦉 Lo lamento, no tengo una pista para esta palabra en mis fuentes."

AHORCADO_SIN_JUEGO = (
    "🦉 No hay ninguna partida en curso. Escriba /ahorcado para empezar una."
)

AHORCADO_RENDIRSE = "🦉 Como guste. La palabra era \"{palabra}\". Cuando quiera, jugamos de nuevo."

JUEGOS_INTRO = (
    "🦉 Cien juegos para conversar tengo en mis anaqueles, ordenados por "
    "categoría. Elija una para empezar:"
)

JUEGOS_SIN_JUEGO = (
    "🦉 No hay ningún juego en curso. Escriba /juegos para elegir uno."
)

JUEGOS_CATEGORIA_VACIA = "🦉 Vaya, esa categoría parece estar vacía por ahora."

JUEGOS_FIN = [
    "🦉 Y con esa, agotamos las consignas de este juego. ¿Probamos otro? Escriba /juegos.",
    "🦉 Ahí se terminaron las rondas de este juego. Ha sido un placer -- /juegos para elegir otro.",
    "🦉 Eso es todo lo que tenía guardado para este juego. Cuando quiera, elegimos otro con /juegos.",
]

JUEGOS_SALIDA = [
    "🦉 Como guste. Dejamos \"{titulo}\" por aquí -- cuando quiera, volvemos con /juegos.",
    "🦉 Entendido, cerramos \"{titulo}\" por ahora. Escriba /juegos si quiere otra ronda.",
]


def juegos_fin() -> str:
    return random.choice(JUEGOS_FIN)


def juegos_salida(titulo: str) -> str:
    return random.choice(JUEGOS_SALIDA).format(titulo=titulo)


def intro_resultado() -> str:
    return random.choice(INTROS_RESULTADO)


def no_encontrado(palabra: str) -> str:
    return random.choice(NO_ENCONTRADO).format(palabra=palabra)


def charla() -> str:
    return random.choice(CHARLA)


def trabajando() -> str:
    return random.choice(TRABAJANDO)


def toque_de_fe() -> str:
    return random.choice(TOQUE_DE_FE)


def ahorcado_ganado() -> str:
    return random.choice(AHORCADO_GANADO)


def ahorcado_perdido(palabra: str) -> str:
    return random.choice(AHORCADO_PERDIDO).format(palabra=palabra)
