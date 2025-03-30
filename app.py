from flask import Flask, request, jsonify, render_template
import os
import json
import logging
import requests
from datetime import datetime, timezone
import re
import unicodedata

# Test SUCCESS

# Charger les variables d'environnement depuis .env si disponible
try:
    from dotenv import load_dotenv
    load_dotenv()  # Charge les variables depuis .env
    print("Variables d'environnement chargées depuis .env")
except ImportError:
    print("dotenv non installé. Si vous avez un fichier .env, installez python-dotenv.")

app = Flask(__name__)

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
USE_MOCK_DATA = not OPENWEATHER_API_KEY  # Utiliser des données mockées si pas de clé API

# Afficher un message indiquant si l'API est utilisée
if USE_MOCK_DATA:
    print("Aucune clé API trouvée - Utilisation des données simulées")
else:
    print(f"Clé API trouvée - Utilisation de l'API OpenWeatherMap (Clé: {OPENWEATHER_API_KEY[:5]}...)")

# Données météorologiques simulées avec plus de détails
MOCK_WEATHER_DATA = {
    "paris": {
        "city": "Paris",
        "country": "France",
        "temperature": 15,
        "weather": "Ensoleillé",
        "humidity": 70,
        "wind_speed": 10,
        "last_updated": "2023-06-15T10:00:00Z"
    },
    "london": {
        "city": "Londres",
        "country": "Royaume-Uni",
        "temperature": 12,
        "weather": "Nuageux",
        "humidity": 85,
        "wind_speed": 15,
        "last_updated": "2023-06-15T09:30:00Z"
    },
    "new york": {
        "city": "New York",
        "country": "États-Unis",
        "temperature": 20,
        "weather": "Ensoleillé",
        "humidity": 60,
        "wind_speed": 8,
        "last_updated": "2023-06-15T04:00:00Z"
    },
    "tokyo": {
        "city": "Tokyo",
        "country": "Japon",
        "temperature": 25,
        "weather": "Pluvieux",
        "humidity": 90,
        "wind_speed": 12,
        "last_updated": "2023-06-15T18:00:00Z"
    }
}

# Traduire les conditions météo en français
WEATHER_TRANSLATIONS = {
    "Clear": "Dégagé",
    "Clouds": "Nuageux",
    "Rain": "Pluvieux",
    "Drizzle": "Bruine",
    "Thunderstorm": "Orageux",
    "Snow": "Neigeux",
    "Mist": "Brumeux",
    "Smoke": "Fumeux",
    "Haze": "Brumeux",
    "Dust": "Poussièreux",
    "Fog": "Brouillard",
    "Sand": "Sableux",
    "Ash": "Cendres",
    "Squall": "Bourrasques",
    "Tornado": "Tornade"
}

# Fonction utilitaire pour obtenir l'heure UTC actuelle
def get_current_utc_time():
    return datetime.now(timezone.utc).isoformat()

# Fonction pour normaliser les noms de ville (supprimer les accents, mettre en minuscules, etc.)
def normalize_city_name(city_name):
    if not city_name:
        return ""
    # Supprimer les accents
    normalized = unicodedata.normalize('NFKD', city_name).encode('ASCII', 'ignore').decode('utf-8')
    # Mettre en minuscules et supprimer les espaces superflus
    normalized = normalized.lower().strip()
    # Remplacer les tirets et underscores par des espaces
    normalized = re.sub(r'[-_]+', ' ', normalized)
    # Supprimer les caractères non alphanumériques (sauf espaces)
    normalized = re.sub(r'[^\w\s]', '', normalized)
    # Supprimer les espaces multiples
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized

# Dictionnaire de correspondances pour les variantes de noms de villes
CITY_NAME_VARIATIONS = {
    "londre": "london",
    "londra": "london",
    "londres": "london",
    "nueva york": "new york",
    "newyork": "new york",
    "ny": "new york",
    "paris": "paris",
    "parigi": "paris",
    "tokyo": "tokyo"
}

# Fonction pour obtenir les données météo depuis OpenWeatherMap
def get_weather_from_api(city):
    try:
        normalized_city = normalize_city_name(city)
        
        # Vérifier si c'est une variante de nom connue
        if normalized_city in CITY_NAME_VARIATIONS:
            normalized_city = CITY_NAME_VARIATIONS[normalized_city]
            
        logger.info(f"Requête à l'API OpenWeatherMap pour la ville : {normalized_city}")
        
        # Implementation d'un mécanisme de circuit breaker simple
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={normalized_city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fr"
                response = requests.get(url, timeout=5)  # Ajouter un timeout
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Traduire la condition météo principale
                    weather_main = data['weather'][0]['main']
                    weather_description = WEATHER_TRANSLATIONS.get(weather_main, data['weather'][0]['description'].capitalize())
                    
                    weather_data = {
                        "city": data['name'],
                        "country": data['sys']['country'],
                        "temperature": round(data['main']['temp']),
                        "weather": weather_description,
                        "humidity": data['main']['humidity'],
                        "wind_speed": round(data['wind']['speed'] * 3.6, 1),  # Conversion de m/s à km/h
                        "last_updated": get_current_utc_time(),
                        "city_id": data['id']  # Stocker l'ID de la ville pour les futures requêtes
                    }
                    
                    logger.info(f"Données météo obtenues avec succès pour {city}")
                    return weather_data
                elif response.status_code == 401:
                    logger.error(f"Erreur d'authentification API: {response.status_code} - {response.text}")
                    # Ne pas réessayer pour les erreurs d'authentification
                    return None
                elif response.status_code == 404:
                    logger.warning(f"Ville non trouvée: {response.status_code} - {response.text}")
                    # Ne pas réessayer pour les villes non trouvées
                    return None
                else:
                    logger.warning(f"Erreur API OpenWeatherMap: {response.status_code} - {response.text}")
                    retry_count += 1
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout lors de la requête à l'API pour {normalized_city}. Essai {retry_count+1}/{max_retries}")
                retry_count += 1
            except requests.exceptions.ConnectionError:
                logger.warning(f"Erreur de connexion lors de la requête à l'API pour {normalized_city}. Essai {retry_count+1}/{max_retries}")
                retry_count += 1
        
        logger.error(f"Échec après {max_retries} tentatives pour {normalized_city}")
        return None
                
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la requête à l'API OpenWeatherMap: {str(e)}")
        return None

@app.route('/', methods=['GET'])
def index():
    """Point de terminaison racine - Interface utilisateur ou documentation API"""
    # Vérifier si la requête est pour l'API JSON
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
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
                "using_real_api": not USE_MOCK_DATA
            },
            "timestamp": get_current_utc_time()
        })
    # Par défaut, renvoyer l'interface utilisateur
    return render_template('index.html', use_real_api=not USE_MOCK_DATA)

@app.route('/api', methods=['GET'])
def api_docs():
    """Documentation de l'API"""
    return jsonify({
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
            "using_real_api": not USE_MOCK_DATA
        },
        "timestamp": get_current_utc_time()
    })

@app.route('/weather', methods=['GET'])
def get_weather():
    try:
        city = request.args.get('city', '')
        
        logger.info(f"Requête météo reçue pour la ville : {city} (normalisé: {normalize_city_name(city)})")
        
        if not city:
            logger.warning("Paramètre de ville manquant dans la requête")
            return jsonify({"error": "Le paramètre city est requis", "status": "error"}), 400
        
        # Si nous avons une clé API, essayons d'abord d'obtenir des données réelles
        weather_data = None
        if not USE_MOCK_DATA:
            weather_data = get_weather_from_api(city)
        
        # Si nous n'avons pas de données réelles, utilisons les données mockées si disponibles
        if weather_data is None:
            normalized_city = normalize_city_name(city)
            
            # Vérifier si c'est une variante de nom connue
            if normalized_city in CITY_NAME_VARIATIONS:
                normalized_city = CITY_NAME_VARIATIONS[normalized_city]
            
            if normalized_city in MOCK_WEATHER_DATA:
                weather_data = MOCK_WEATHER_DATA[normalized_city]
                logger.info(f"Utilisation des données mockées pour {normalized_city}")
            else:
                logger.warning(f"Données météo pour la ville '{city}' non trouvées")
                return jsonify({
                    "error": f"Données météo pour {city} non trouvées", 
                    "status": "error",
                    "suggestions": list(CITY_NAME_VARIATIONS.keys()),
                    "available_cities": list(MOCK_WEATHER_DATA.keys()) if USE_MOCK_DATA else []
                }), 404
        
        logger.info(f"Renvoi des données météo pour {normalize_city_name(city)}")
        return jsonify({
            "status": "success",
            "data": weather_data,
            "timestamp": get_current_utc_time(),
            "from_mock_data": USE_MOCK_DATA or weather_data == MOCK_WEATHER_DATA.get(normalize_city_name(city))
        })
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la requête : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur", "status": "error", "details": str(e)}), 500

@app.route('/cities', methods=['GET'])
def get_cities():
    """Renvoie une liste des villes disponibles"""
    # Si nous utilisons des données mockées, retournons uniquement les villes mockées
    if USE_MOCK_DATA:
        return jsonify({
            "status": "success",
            "data": {
                "cities": list(MOCK_WEATHER_DATA.keys())
            },
            "timestamp": get_current_utc_time()
        })
    else:
        # Sinon, retournons les villes mockées comme suggestions, mais indiquez que n'importe quelle ville peut être recherchée
        return jsonify({
            "status": "success",
            "data": {
                "cities": list(MOCK_WEATHER_DATA.keys()),
                "message": "Vous pouvez rechercher n'importe quelle ville dans le monde grâce à l'API OpenWeatherMap"
            },
            "timestamp": get_current_utc_time()
        })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Point de terminaison non trouvé", "status": "error"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Erreur interne du serveur", "status": "error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 