Piper TTS Service

Servicio de Text-to-Speech (TTS) local usando Piper. Convierte texto a audio WAV u OGG con distintas voces preentrenadas.

---

Instalación con Docker:

git clone <repo-url>
cd piper-docker
docker build -t piper-tts-app .
docker run -d -p 8000:8000 piper-tts-app

Ahora el servicio estará corriendo en http://localhost:8000.

---

Endpoints:

1. /health
Método: GET
Descripción: Verifica si el servicio está activo y muestra las voces disponibles.

Ejemplo:

curl http://localhost:8000/health

Respuesta esperada:

{
  "status": "healthy",
  "available_voices": ["es_ES-carlfm-x_low", "es_MX-claude-high"]
}

---

2. /tts
Método: GET
Descripción: Genera audio a partir de texto.

Parámetros Query:
- text    : Texto que quieres convertir a voz
- voice   : Nombre de la voz disponible (es_ES-carlfm-x_low, es_MX-claude-high)
- format  : Opcional. Formato de salida (wav o ogg). Por defecto wav

Ejemplo en WAV:

curl "http://localhost:8000/tts?text=Hola+Mundo&voice=es_MX-claude-high" --output hola.wav

Ejemplo en OGG:

curl "http://localhost:8000/tts?text=Hola+Mundo&voice=es_MX-claude-high&format=ogg" --output hola.ogg

---

Voces Disponibles:

- es_ES-carlfm-x_low
- es_MX-claude-high

Estas voces se encuentran en la carpeta voices/ y se pueden agregar más siguiendo el mismo formato .onnx + .json.

---

Notas:

- Por defecto, el audio se genera en WAV si no se especifica el parámetro format.
- Puedes agregar nuevas voces creando un archivo .onnx y su correspondiente .json en la carpeta voices/ y actualizando voices.json.

---

Autor:

Creado por Yorian Lara.
