# API Météo

Une API simple pour obtenir des informations météorologiques pour différentes villes avec des fonctionnalités améliorées, une interface utilisateur et une intégration avec OpenWeatherMap.

## Fonctionnalités

- Interface utilisateur moderne pour visualiser la météo
- Intégration avec l'API OpenWeatherMap pour des données météo réelles
- Mode de secours avec données simulées si aucune clé API n'est fournie
- Plusieurs endpoints pour différentes fonctionnalités :
  - GET `/` - Interface utilisateur par défaut ou documentation API (selon l'en-tête Accept)
  - GET `/api` - Documentation de l'API
  - GET `/weather?city=Paris` - Obtenir les données météorologiques pour une ville spécifique
  - GET `/cities` - Obtenir une liste des villes disponibles
- Données météorologiques améliorées incluant température, conditions, humidité et vitesse du vent
- Format de réponse JSON cohérent avec statut et horodatage
- Gestion des erreurs améliorée avec des retours utiles
- Journalisation pour le suivi des requêtes
- Tests unitaires avec pytest
- CI/CD avec GitHub Actions
- Conteneurisation Docker

## Captures d'écran

### Interface Utilisateur
L'application inclut une interface utilisateur moderne et responsive pour visualiser les données météorologiques :
- Recherche de météo par ville
- Affichage des températures, conditions, humidité et vitesse du vent
- Liste des villes disponibles
- Design responsive adapté aux mobiles et ordinateurs
- Indicateur de source des données (API réelle ou données simulées)

## Installation

### Prérequis

- Python 3.10+ installé
- Docker (optionnel, pour la conteneurisation)
- Clé API OpenWeatherMap (optionnel, mais recommandé)

### Obtenir une clé API OpenWeatherMap

1. Créez un compte sur [OpenWeatherMap](https://home.openweathermap.org/users/sign_up)
2. Une fois connecté, allez dans la section "API Keys" de votre tableau de bord
3. Notez votre clé API pour l'utiliser avec l'application

### Configuration

1. Cloner ce dépôt
   ```bash
   git clone <url-de-votre-dépôt>
   cd weather-api
   ```

2. Installer les dépendances
   ```bash
   pip install -r requirements.txt
   ```

3. Configurer la clé API OpenWeatherMap (optionnel mais recommandé)
   
   **Sur Linux/Mac :**
   ```bash
   export OPENWEATHER_API_KEY=votre_clé_api
   ```
   
   **Sur Windows (PowerShell) :**
   ```powershell
   $env:OPENWEATHER_API_KEY="votre_clé_api"
   ```
   
   **Sur Windows (CMD) :**
   ```cmd
   set OPENWEATHER_API_KEY=votre_clé_api
   ```

## Exécution de l'Application

### En local

```bash
python app.py
```

L'application sera disponible à l'adresse http://localhost:5000

### Avec Docker

Construire l'image Docker :
```bash
docker build -t api-meteo .
```

Exécuter le conteneur (sans clé API - mode données simulées) :
```bash
docker run -p 5000:5000 api-meteo
```

Exécuter le conteneur avec une clé API :
```bash
docker run -p 5000:5000 -e OPENWEATHER_API_KEY=votre_clé_api api-meteo
```

## Tests

Exécuter les tests avec :
```bash
pytest
```

## Utilisation de l'API

### Accès à l'interface utilisateur

Ouvrez simplement votre navigateur à l'adresse suivante :
```
http://localhost:5000/
```

### Documentation de l'API

#### Requête
```
GET /api
```

#### Réponse
```json
{
  "status": "success",
  "data": {
    "name": "API Météo",
    "version": "1.0.0",
    "description": "Une API simple pour obtenir des informations météorologiques pour différentes villes",
    "endpoints": [
      {"path": "/", "method": "GET", "description": "Documentation de l'API ou interface utilisateur"},
      {"path": "/api", "method": "GET", "description": "Documentation de l'API"},
      {"path": "/weather", "method": "GET", "description": "Obtenir les données météo d'une ville", "params": ["city"]},
      {"path": "/cities", "method": "GET", "description": "Obtenir la liste des villes disponibles"}
    ],
    "using_real_api": true
  },
  "timestamp": "2023-06-15T12:00:00.000000"
}
```

### Obtenir les Informations Météorologiques

#### Requête
```
GET /weather?city=Paris
```

#### Réponse
```json
{
  "status": "success",
  "data": {
    "city": "Paris",
    "country": "FR",
    "temperature": 15,
    "weather": "Dégagé",
    "humidity": 70,
    "wind_speed": 10.8,
    "last_updated": "2023-06-15T10:00:00Z"
  },
  "timestamp": "2023-06-15T12:00:00.000000",
  "from_mock_data": false
}
```

### Obtenir les Villes Disponibles

#### Requête
```
GET /cities
```

#### Réponse (avec API réelle)
```json
{
  "status": "success",
  "data": {
    "cities": ["paris", "london", "new york", "tokyo"],
    "message": "Vous pouvez rechercher n'importe quelle ville dans le monde grâce à l'API OpenWeatherMap"
  },
  "timestamp": "2023-06-15T12:00:00.000000"
}
```

### Réponses d'Erreur

#### Paramètre de Ville Manquant
```json
{
  "error": "Le paramètre city est requis",
  "status": "error"
}
```

#### Ville Non Trouvée
```json
{
  "error": "Données météo pour <city> non trouvées",
  "status": "error",
  "available_cities": []
}
```

#### Point de Terminaison Non Trouvé
```json
{
  "error": "Point de terminaison non trouvé",
  "status": "error"
}
```

## Pipeline CI/CD

Le projet inclut un workflow GitHub Actions pour :
1. Exécuter les tests à chaque push et pull request
2. Construire et exporter une image Docker
3. Pousser l'image vers Docker Hub

Pour configurer le déploiement vers Docker Hub, ajoutez vos identifiants Docker Hub (`DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN`) aux secrets du dépôt GitHub.

## Fonctionnement en Mode Dégradé

Si aucune clé API OpenWeatherMap n'est fournie (ou si l'API est indisponible), l'application utilise automatiquement des données simulées pour les villes prédéfinies (Paris, Londres, New York, Tokyo). Cela garantit que l'application reste fonctionnelle même sans connexion à l'API externe.

## Améliorations Futures

- Ajouter un cache pour les réponses de l'API afin de réduire les appels API externes
- Implémenter une limitation de débit pour respecter les limites de l'API gratuite
- Ajouter une authentification pour l'accès à l'API
- Ajouter le support des données météorologiques historiques
- Support des prévisions météorologiques sur plusieurs jours
- Implémenter une journalisation d'erreurs plus détaillée
- Ajouter une documentation Swagger/OpenAPI
- Ajouter un mode sombre à l'interface utilisateur
- Ajouter la géolocalisation pour détecter automatiquement la ville de l'utilisateur 