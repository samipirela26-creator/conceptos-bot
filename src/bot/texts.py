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
