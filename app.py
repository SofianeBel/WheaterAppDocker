from flask import Flask, request, jsonify, render_template
import os
import json
import logging
from datetime import datetime, timezone

app = Flask(__name__)

# Configuration de la journalisation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Données météorologiques simulées avec plus de détails
WEATHER_DATA = {
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

# Fonction utilitaire pour obtenir l'heure UTC actuelle
def get_current_utc_time():
    return datetime.now(timezone.utc).isoformat()

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
                ]
            },
            "timestamp": get_current_utc_time()
        })
    # Par défaut, renvoyer l'interface utilisateur
    return render_template('index.html')

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
            ]
        },
        "timestamp": get_current_utc_time()
    })

@app.route('/weather', methods=['GET'])
def get_weather():
    try:
        city = request.args.get('city', '').lower()
        
        logger.info(f"Requête météo reçue pour la ville : {city}")
        
        if not city:
            logger.warning("Paramètre de ville manquant dans la requête")
            return jsonify({"error": "Le paramètre city est requis", "status": "error"}), 400
        
        if city not in WEATHER_DATA:
            logger.warning(f"Données météo pour la ville '{city}' non trouvées")
            return jsonify({
                "error": f"Données météo pour {city} non trouvées", 
                "status": "error",
                "available_cities": list(WEATHER_DATA.keys())
            }), 404
        
        logger.info(f"Renvoi des données météo pour {city}")
        return jsonify({
            "status": "success",
            "data": WEATHER_DATA[city],
            "timestamp": get_current_utc_time()
        })
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la requête : {str(e)}")
        return jsonify({"error": "Erreur interne du serveur", "status": "error"}), 500

@app.route('/cities', methods=['GET'])
def get_cities():
    """Renvoie une liste des villes disponibles"""
    return jsonify({
        "status": "success",
        "data": {
            "cities": list(WEATHER_DATA.keys())
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