#!/bin/bash
# Script de déploiement pour l'application météo

# Variables
APP_NAME="api-meteo"
IMAGE_NAME="siflybel/api-meteo:latest"
CONTAINER_NAME="api-meteo-container"
PORT=5000

# Fonction pour afficher des messages avec l'horodatage
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    log "❌ Docker n'est pas installé. Installation impossible."
    exit 1
fi

# Afficher les informations du déploiement
log "🚀 Démarrage du déploiement de $APP_NAME"
log "📦 Image Docker: $IMAGE_NAME"
log "🔌 Port exposé: $PORT"

# Récupérer la dernière image depuis Docker Hub
log "📥 Récupération de la dernière image Docker..."
docker pull $IMAGE_NAME
if [ $? -ne 0 ]; then
    log "❌ Échec lors de la récupération de l'image Docker."
    exit 1
fi

# Arrêter et supprimer le conteneur existant s'il existe
if docker ps -a | grep -q $CONTAINER_NAME; then
    log "🛑 Arrêt du conteneur existant..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Vérifier si une clé API est fournie
if [ -z "$OPENWEATHER_API_KEY" ]; then
    log "⚠️  Aucune clé API OpenWeatherMap fournie. L'application utilisera des données simulées."
else
    log "🔑 Clé API OpenWeatherMap configurée."
fi

# Démarrer le nouveau conteneur
log "🚀 Lancement du nouveau conteneur..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:5000 \
    -e OPENWEATHER_API_KEY=$OPENWEATHER_API_KEY \
    --restart always \
    $IMAGE_NAME

# Vérifier si le conteneur a démarré avec succès
if [ $? -eq 0 ]; then
    log "✅ Déploiement terminé avec succès!"
    log "🌐 Application accessible à l'adresse: http://localhost:$PORT"
else
    log "❌ Échec du déploiement du conteneur."
    exit 1
fi

# Afficher les logs du conteneur (optionnel)
log "📋 Affichage des logs du conteneur:"
docker logs $CONTAINER_NAME --tail 10

log "📝 Déploiement finalisé."
exit 0 