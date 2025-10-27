# Detener y eliminar contenedores, redes y volúmenes anteriores
echo "--- Limpiando entorno anterior ---"
docker compose down -v

# Levantar todos los servicios
echo "--- Iniciando servicios con Docker Compose ---"
docker compose up -d

# Mostrar estado de los contenedores
echo "--- Estado de los contenedores ---"
docker compose ps
