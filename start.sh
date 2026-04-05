#!/bin/bash

# Colores para la consola 
GREEN='\033[0-32m'
NC='\033[0m'

echo -e "${GREEN}>>> Limpiando contenedores antiguos...${NC}"
docker-compose down

echo -e "${GREEN}>>> Levantando la infraestructura (Nginx + Flask + Redis)...${NC}"
# --build asegura que si cambio algo en el código de Flask, se actualice
docker-compose up --build -d

echo -e "${GREEN}>>> ¡Servidor arriba! Mostrando logs en tiempo real...${NC}"
docker logs -f flask_backend