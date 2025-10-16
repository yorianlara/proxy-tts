# Conversión básica
curl "http://192.168.1.100:8000/tts?text=Tu%20texto%20aquí" --output audio.ogg

# Con velocidad personalizada
curl "http://192.168.1.100:8000/tts?text=Hola&speed=0.8" --output audio.ogg

# Verificar salud del servicio
curl "http://192.168.1.100:8000/health"

# Limpieza manual (si es necesario)
curl "http://192.168.1.100:8000/cleanup"
