#!/bin/bash

echo "=========================================="
echo "   INICIANDO SISTEMA DE TURNOS (IAEW)     "
echo "=========================================="

# 1. Detener y limpiar todo (incluido volúmenes para arrancar de cero)
echo "♻️  Deteniendo contenedores y borrando volúmenes..."
docker compose down -v

# 2. Levantar todo (reconstruyendo la imagen de la API/Worker)
echo "🚀 Levantando servicios (esto puede demorar unos minutos)..."
docker compose up -d --build

# 3. Mostrar estado final
echo "✅ Estado de los contenedores:"
docker compose ps

echo "=========================================="
echo "   LISTO PARA USAR: http://localhost:8000/docs "
echo "=========================================="