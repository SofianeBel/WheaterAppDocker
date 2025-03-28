import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

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

def test_cities_endpoint(client):
    """Teste si le point de terminaison des villes renvoie une liste de villes"""
    response = client.get('/cities')
    json_data = response.get_json()
    
    assert response.status_code == 200
    assert json_data['status'] == 'success'
    assert 'cities' in json_data['data']
    assert isinstance(json_data['data']['cities'], list)
    assert len(json_data['data']['cities']) > 0

def test_index_endpoint(client):
    """Teste si le point de terminaison index renvoie la documentation de l'API"""
    response = client.get('/')
    json_data = response.get_json()
    
    assert response.status_code == 200
    assert json_data['status'] == 'success'
    assert 'name' in json_data['data']
    assert 'version' in json_data['data']
    assert 'endpoints' in json_data['data'] 