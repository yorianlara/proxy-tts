from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import requests
import os
import logging
import sys
from converter import convert_to_ogg, temp_files_to_cleanup

# Configurar logging
logging.basicConfig(
    level=logging.WARNING,  # Menos verboso
    format='%(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# CREAR LA APLICACIÓN PRIMERO
app = FastAPI(title="TTS Proxy Service", version="1.0.0")
MIMIC3_URL = "http://mimic3_tts:59125/api/tts"

def cleanup_file(file_path: str):
    """Función para limpiar archivo temporal en segundo plano"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            if file_path in temp_files_to_cleanup:
                temp_files_to_cleanup.remove(file_path)
            logger.info(f"🧹 Archivo temporal eliminado: {file_path}")
    except Exception as e:
        logger.error(f"⚠️ Error eliminando {file_path}: {e}")

@app.get("/")
async def root():
    return {"message": "TTS Proxy Service - Usa /tts para convertir texto a audio OGG"}

@app.get("/tts")
async def text_to_speech(
    text: str,
    speed: float = 1.0,
    download: bool = True,
    background_tasks: BackgroundTasks = None
):
    try:
        logger.info(f"📞 Recibida petición: '{text}'")
        
        # VOZ FIJA - es_ES/m-ailabs_low
        params = {
            "text": text,
            "lengthScale": speed,
            "voice": "es_ES/m-ailabs_low"  # Voz siempre fija
        }
        
        logger.info(f"🔗 Llamando a Mimic3 con voz fija: es_ES/m-ailabs_low")
        
        response = requests.get(MIMIC3_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(500, f"Mimic3 error: {response.text}")
        
        # Verificar que es audio WAV
        if len(response.content) < 4 or not response.content.startswith(b'RIFF'):
            raise HTTPException(500, "Respuesta no es audio WAV válido")
        
        logger.info("✅ Audio WAV válido recibido")
        
        # Convertir a OGG
        ogg_file_path = convert_to_ogg(response.content)
        
        logger.info(f"✅ OGG creado: {ogg_file_path}")
        
        if download:
            if background_tasks:
                background_tasks.add_task(cleanup_file, ogg_file_path)
            
            return FileResponse(
                ogg_file_path,
                media_type='audio/ogg',
                filename="audio.ogg"
            )
        else:
            return {
                "message": "Audio convertido exitosamente",
                "file_path": ogg_file_path
            }
            
    except Exception as e:
        logger.error(f"🔥 Error: {str(e)}")
        raise HTTPException(500, f"Error interno: {str(e)}")

@app.get("/health")
async def health_check():
    try:
        response = requests.get("http://mimic3_tts:59125/api/healthcheck", timeout=5)
        mimic3_status = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        mimic3_status = f"unreachable: {str(e)}"
    
    return {"status": "healthy", "mimic3": mimic3_status}

@app.get("/cleanup")
async def manual_cleanup():
    """Endpoint manual para limpiar archivos temporales"""
    cleaned = []
    for file_path in temp_files_to_cleanup[:]:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                cleaned.append(file_path)
                temp_files_to_cleanup.remove(file_path)
        except Exception as e:
            logger.error(f"Error limpiando {file_path}: {e}")
    
    return {"cleaned_files": cleaned, "remaining": len(temp_files_to_cleanup)}
