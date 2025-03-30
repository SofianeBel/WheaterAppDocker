import pytest
from app import app, normalize_city_name

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_endpoint_html(client):
    """Teste si le point de terminaison racine renvoie l'interface HTML par défaut"""
    response = client.get('/')
    
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data
    assert b'temps' in response.data  # Vérifier un texte simple sans accents

def test_index_endpoint_json(client):
    """Teste si le point de terminaison racine renvoie la documentation API en JSON"""
    response = client.get('/', headers={'Accept': 'application/json'})
    json_data = response.get_json()
    
    assert response.status_code == 200
    assert json_data['status'] == 'success'
    assert 'name' in json_data['data']
    assert 'endpoints' in json_data['data']

def test_api_endpoint(client):
    """Teste si le point de terminaison API renvoie la documentation"""
    response = client.get('/api')
    json_data = response.get_json()
    
    assert response.status_code == 200
    assert json_data['status'] == 'success'
    assert 'name' in json_data['data']
    assert 'endpoints' in json_data['data']

def test_weather_endpoint_success(client):
    """Teste si le point de terminaison météo renvoie des données pour une ville valide"""
    response = client.get('/weather?city=Paris')
    json_data = response.get_json()
    
    assert response.status_code == 200
    assert json_data['status'] == 'success'
    assert json_data['data']['city'] == 'Paris'
    assert 'temperature' in json_data['data']
    assert 'weather' in json_data['data']
    assert 'timestamp' in json_data

def test_weather_endpoint_missing_param(client):
    """Teste si le point de terminaison météo renvoie 400 quand le paramètre ville est manquant"""
    response = client.get('/weather')
    json_data = response.get_json()
    
    assert response.status_code == 400
    assert json_data['status'] == 'error'
    assert json_data['error'] == 'Le paramètre city est requis'

def test_weather_endpoint_city_not_found(client):
    """Teste si le point de terminaison météo renvoie 404 pour une ville inconnue"""
    response = client.get('/weather?city=Unknown')
    json_data = response.get_json()
    
    assert response.status_code == 404
    assert json_data['status'] == 'error'
    assert 'non trouvées' in json_data['error']
    assert 'available_cities' in json_data
    assert 'suggestions' in json_data

def test_cities_endpoint(client):
    """Teste si le point de terminaison des villes renvoie une liste de villes"""
    response = client.get('/cities')
    json_data = response.get_json()
    
    assert response.status_code == 200
    assert json_data['status'] == 'success'
    assert 'cities' in json_data['data']
    assert isinstance(json_data['data']['cities'], list)
    assert len(json_data['data']['cities']) > 0

def test_normalize_city_name():
    """Teste la fonction de normalisation des noms de ville"""
    assert normalize_city_name("Paris") == "paris"
    assert normalize_city_name("New York") == "new york"
    assert normalize_city_name("Sâo Pãulo") == "sao paulo"
    assert normalize_city_name("Münich") == "munich"
    assert normalize_city_name("") == ""
    assert normalize_city_name("Paris-Est") == "paris est"
    assert normalize_city_name("   Tokyo   ") == "tokyo"

def test_weather_endpoint_city_variant(client):
    """Teste si le point de terminaison météo gère correctement les variantes de noms"""
    # Test avec une variante de Londres
    response = client.get('/weather?city=Londre')
    json_data = response.get_json()
    
    # Soit c'est traité comme Londres (200) ou on a une suggestion (404)
    if response.status_code == 200:
        assert json_data['status'] == 'success'
        assert json_data['data']['city'] in ['London', 'Londres']
    else:
        assert response.status_code == 404
        assert 'suggestions' in json_data
        assert 'londre' in json_data['suggestions'] 