from pydub import AudioSegment
import tempfile
import os
import io
import atexit
import subprocess

# Lista global para trackear archivos temporales
temp_files_to_cleanup = []

# Función de limpieza al cerrar la aplicación
def cleanup_temp_files():
    for file_path in temp_files_to_cleanup:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                print(f"🧹 Eliminado: {file_path}")
        except Exception as e:
            print(f"⚠️ Error eliminando {file_path}: {e}")

# Registrar limpieza al salir
atexit.register(cleanup_temp_files)

def convert_to_ogg(audio_data: bytes) -> str:
    """
    Convierte audio WAV (bytes) a archivo OGG con codec Opus
    """
    temp_wav_path = None
    temp_ogg_path = None
    
    try:
        # Crear archivo temporal para WAV
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
            temp_wav_path = temp_wav.name
            temp_wav.write(audio_data)
        
        # Crear archivo temporal para OGG
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_ogg:
            temp_ogg_path = temp_ogg.name
        
        # Exportar como OGG con Opus (MEJOR CALIDAD PARA VOZ)
        subprocess.run([
            'ffmpeg', '-i', temp_wav_path,
            '-c:a', 'libopus',        # Codec Opus
            '-b:a', '32k',            # Bitrate 32 kbps
            '-ar', '48000',           # Sample rate 48 kHz
            '-vbr', 'on',             # Variable bitrate
            '-application', 'voip',   # Optimizado para voz
            '-y',                     # Sobrescribir si existe
            temp_ogg_path
        ], check=True, capture_output=True)
        
        print(f"✅ Conversión Opus exitosa: {temp_ogg_path}")
        
        # Agregar a la lista de limpieza
        temp_files_to_cleanup.append(temp_ogg_path)
        
        return temp_ogg_path
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en ffmpeg: {e.stderr.decode()}")
        raise Exception(f"Error en conversión de audio: {e.stderr.decode()}")
        
    except Exception as e:
        print(f"❌ Error en conversión: {str(e)}")
        raise
        
    finally:
        # Siempre limpiar el WAV temporal
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.unlink(temp_wav_path)
            except:
                pass
