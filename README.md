# API Météo

Une API simple pour obtenir des informations météorologiques pour différentes villes avec des fonctionnalités améliorées.

## Fonctionnalités

- Plusieurs endpoints pour différentes fonctionnalités :
  - GET `/` - Documentation de l'API
  - GET `/weather?city=Paris` - Obtenir les données météorologiques pour une ville spécifique
  - GET `/cities` - Obtenir une liste des villes disponibles
- Données météorologiques améliorées incluant température, conditions, humidité et vitesse du vent
- Format de réponse JSON cohérent avec statut et horodatage
- Gestion des erreurs améliorée avec des retours utiles
- Journalisation pour le suivi des requêtes
- Tests unitaires avec pytest
- CI/CD avec GitHub Actions
- Conteneurisation Docker

## Installation

### Prérequis

- Python 3.10+ installé
- Docker (optionnel, pour la conteneurisation)

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

Exécuter le conteneur :
```bash
docker run -p 5000:5000 api-meteo
```

## Tests

Exécuter les tests avec :
```bash
pytest
```

## Utilisation de l'API

### Documentation de l'API

#### Requête
```
GET /
```

#### Réponse
```json
{
  "status": "success",
  "data": {
    "name": "Weather API",
    "version": "1.0.0",
    "description": "Une API simple pour obtenir des informations météorologiques pour différentes villes",
    "endpoints": [
      {"path": "/", "method": "GET", "description": "Documentation de l'API"},
      {"path": "/weather", "method": "GET", "description": "Obtenir les données météo d'une ville", "params": ["city"]},
      {"path": "/cities", "method": "GET", "description": "Obtenir la liste des villes disponibles"}
    ]
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
    "country": "France",
    "temperature": 15,
    "weather": "Clear",
    "humidity": 70,
    "wind_speed": 10,
    "last_updated": "2023-06-15T10:00:00Z"
  },
  "timestamp": "2023-06-15T12:00:00.000000"
}
```

### Obtenir les Villes Disponibles

#### Requête
```
GET /cities
```

#### Réponse
```json
{
  "status": "success",
  "data": {
    "cities": ["paris", "london", "new york", "tokyo"]
  },
  "timestamp": "2023-06-15T12:00:00.000000"
}
```

### Réponses d'Erreur

#### Paramètre de Ville Manquant
```json
{
  "error": "City parameter is required",
  "status": "error"
}
```

#### Ville Non Trouvée
```json
{
  "error": "Weather data for <city> not found",
  "status": "error",
  "available_cities": ["paris", "london", "new york", "tokyo"]
}
```

#### Point de Terminaison Non Trouvé
```json
{
  "error": "Endpoint not found",
  "status": "error"
}
```

## Pipeline CI/CD

Le projet inclut un workflow GitHub Actions pour :
1. Exécuter les tests à chaque push et pull request
2. Construire et exporter une image Docker
3. Pousser l'image Docker vers Docker Hub

## Améliorations Futures

- Se connecter à une vraie API météo comme OpenWeatherMap
- Ajouter un cache pour les réponses de l'API afin de réduire les appels API externes
- Implémenter une limitation de débit
- Ajouter une authentification pour l'accès à l'API
- Créer une interface simple pour afficher la météo
- Ajouter le support des données météorologiques historiques
- Support des prévisions météorologiques
- Implémenter une journalisation d'erreurs plus détaillée
- Ajouter une documentation Swagger/OpenAPI 