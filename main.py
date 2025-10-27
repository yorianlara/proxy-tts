from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
import json
import wave
import tempfile
import subprocess
from piper import PiperVoice

APP_DIR = Path(__file__).parent
VOICES_DIR = APP_DIR / "voices"
VOICES_FILE = VOICES_DIR / "voices.json"

# Cargar voces disponibles
with open(VOICES_FILE, "r", encoding="utf-8") as f:
    available_voices = json.load(f)

app = FastAPI(title="Piper TTS API")

def synthesize_text(text: str, voice_name: str) -> Path:
    voice_entry = next((v for v in available_voices if v["name"] == voice_name), None)
    if not voice_entry:
        raise HTTPException(status_code=404, detail=f"Voz '{voice_name}' no encontrada")

    voice_path = VOICES_DIR / voice_entry["onnx"]
    if not voice_path.exists():
        raise HTTPException(status_code=404, detail=f"Archivo de voz '{voice_path}' no encontrado")

    voice = PiperVoice.load(str(voice_path))

    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with wave.open(temp_wav, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    return Path(temp_wav.name)

def convert_wav_to_ogg(wav_path: Path) -> Path:
    temp_ogg = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(wav_path),
        "-c:a", "libvorbis", str(temp_ogg.name)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Path(temp_ogg.name)

@app.get("/tts")
def tts(
    text: str = Query(...),
    voice: str = Query(...),
    format: str = Query("wav", regex="^(wav|ogg)$")
):
    try:
        wav_path = synthesize_text(text, voice)
        if format == "ogg":
            audio_path = convert_wav_to_ogg(wav_path)
            return FileResponse(path=audio_path, media_type="audio/ogg", filename="output.ogg")
        else:
            return FileResponse(path=wav_path, media_type="audio/wav", filename="output.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy", "available_voices": [v["name"] for v in available_voices]}
