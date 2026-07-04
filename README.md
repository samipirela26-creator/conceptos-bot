# conceptos-bot (Francis la Búho)

Bot de Telegram que define palabras/conceptos usando **dos fuentes reales**,
sin inventar contenido:

- 📖 **RAE**, vía la API comunitaria [rae-api.com](https://rae-api.com) (scrapea dle.rae.es).
- 🔎 **Wikcionario en español**, vía la API pública de MediaWiki (licencia CC BY-SA).

La IA (Gemini) se usa **únicamente** para entender qué palabra pidió el
usuario cuando escribe una pregunta en lenguaje libre (ej. "¿qué significa
ósmosis?") — nunca para redactar o reformular la definición en sí. Si el
mensaje ya es una palabra directa ("casa"), ni siquiera hace falta IA (ver
`src/utils/concept_extractor.py`).

## Uso

Escríbele al bot una palabra o pregunta:

```
casa
¿qué es la fotosíntesis?
significado de ósmosis
```

Responde con las acepciones de la RAE y una explicación de Wikcionario. Si
la palabra no existe en ninguna de las dos fuentes, lo dice claramente en
vez de adivinar.

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env: TELEGRAM_BOT_TOKEN (de @BotFather) y GEMINI_API_KEY
python run.py
```

## Estructura

```
src/
  services/rae.py           # cliente rae-api.com
  services/wikcionario.py   # cliente Wikcionario (MediaWiki API)
  llm/gemini_client.py      # SOLO extrae el concepto del mensaje libre
  utils/concept_extractor.py # heurística sin IA (caso común: palabra directa)
  bot/handlers.py            # flujo: entender -> consultar -> formatear
  bot/formatters.py          # arma el mensaje final (texto real, sin tocar)
  bot/texts.py                # personalidad "Francis la Búho"
```

## Despliegue 24/7

Ver `systemd/conceptos-bot.service.template` (mismo patrón que `asistente-bot`
y `gastos-bot`: servicio `systemd --user`, liviano, `MemoryMax=300M`).
