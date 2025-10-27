sudo docker compose down

# Limpiar TODO: contenedores, imágenes, redes, caché
sudo docker system prune -a --volumes

# Limpiar solo contenedores e imágenes
sudo docker system prune -a

# Limpiar redes no utilizadas
sudo docker network prune

# Limpiar volúmenes no utilizados
sudo docker volume prune

# Limpiar build cache
sudo docker builder prune
