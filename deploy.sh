#!/bin/bash
# Script de déploiement pour l'application météo

# Variables
APP_NAME="api-meteo"
# Utiliser l'image spécifique si fournie, sinon utiliser l'image latest
IMAGE_NAME=${DOCKER_IMAGE:-"siflybel/api-meteo:latest"}
CONTAINER_NAME="api-meteo-container"
PORT=5000
MAX_RETRIES=3
RETRY_DELAY=5

# Fonction pour afficher des messages avec l'horodatage
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Fonction pour vérifier si une commande s'est exécutée avec succès
check_success() {
    if [ $? -ne 0 ]; then
        log "❌ $1"
        exit 1
    fi
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

# Récupérer la dernière image depuis Docker Hub avec plusieurs tentatives
log "📥 Récupération de l'image Docker..."
for i in $(seq 1 $MAX_RETRIES); do
    docker pull $IMAGE_NAME && break
    if [ $i -eq $MAX_RETRIES ]; then
        log "❌ Échec lors de la récupération de l'image Docker après $MAX_RETRIES tentatives."
        exit 1
    fi
    log "⚠️ Tentative $i échouée. Nouvelle tentative dans $RETRY_DELAY secondes..."
    sleep $RETRY_DELAY
done
log "✅ Image Docker récupérée avec succès."

# Arrêter et supprimer le conteneur existant s'il existe
if docker ps -a | grep -q $CONTAINER_NAME; then
    log "🛑 Arrêt du conteneur existant..."
    docker stop $CONTAINER_NAME
    check_success "Échec lors de l'arrêt du conteneur existant."
    docker rm $CONTAINER_NAME
    check_success "Échec lors de la suppression du conteneur existant."
    log "✅ Ancien conteneur supprimé."
else
    log "ℹ️ Aucun conteneur existant trouvé."
fi

# Vérifier si une clé API est fournie et valide (format minimal)
if [ -z "$OPENWEATHER_API_KEY" ]; then
    log "⚠️ Aucune clé API OpenWeatherMap fournie. L'application utilisera des données simulées."
elif [ ${#OPENWEATHER_API_KEY} -lt 10 ]; then
    log "⚠️ La clé API OpenWeatherMap semble invalide (trop courte). Vérifiez sa valeur."
else
    log "🔑 Clé API OpenWeatherMap configurée."
fi

# Créer un réseau Docker si nécessaire
if ! docker network ls | grep -q "api-meteo-network"; then
    log "🌐 Création du réseau Docker..."
    docker network create api-meteo-network
    check_success "Échec de la création du réseau Docker."
else
    log "🌐 Réseau Docker existant."
fi

# Démarrer le nouveau conteneur
log "🚀 Lancement du nouveau conteneur..."
docker run -d \
    --name $CONTAINER_NAME \
    --network api-meteo-network \
    -p $PORT:5000 \
    -e OPENWEATHER_API_KEY=$OPENWEATHER_API_KEY \
    --restart always \
    --health-cmd="curl -f http://localhost:5000/ || exit 1" \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    $IMAGE_NAME

# Vérifier si le conteneur a démarré avec succès
if [ $? -eq 0 ]; then
    log "✅ Conteneur démarré avec succès!"
    
    # Attendre que le conteneur soit en bonne santé
    log "⏳ Vérification de l'état du conteneur..."
    for i in {1..12}; do
        health_status=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER_NAME 2>/dev/null)
        
        if [ "$health_status" = "healthy" ]; then
            log "✅ Conteneur en bonne santé!"
            log "🌐 Application accessible à l'adresse: http://localhost:$PORT"
            break
        elif [ "$health_status" = "unhealthy" ]; then
            log "❌ Le conteneur est en mauvaise santé. Vérifiez les logs."
            docker logs $CONTAINER_NAME --tail 20
            exit 1
        fi
        
        if [ $i -eq 12 ]; then
            log "⚠️ Délai d'attente dépassé pour la vérification de santé."
        else
            log "⏳ En attente de la santé du conteneur... ($i/12)"
            sleep 5
        fi
    done
else
    log "❌ Échec du déploiement du conteneur."
    exit 1
fi

# Afficher les logs du conteneur
log "📋 Affichage des logs du conteneur:"
docker logs $CONTAINER_NAME --tail 10

log "📝 Déploiement finalisé."
exit 0 