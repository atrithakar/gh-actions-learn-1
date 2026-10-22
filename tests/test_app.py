import pytest
import json
from app import app, add, subtract, multiply, divide

# --- 1. Unit Tests for Core Functions ---
def test_add():
    assert add(5, 3) == 8
    assert add(-2, 2) == 0

def test_subtract():
    assert subtract(10, 4) == 6
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 5) == -10

def test_divide():
    assert divide(10, 2) == 5
    with pytest.raises(ValueError, match="Division by zero"):
        divide(5, 0)

# --- 2. Flask API Integration Tests ---
@pytest.fixture
def client():
    """Configures the Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def post_json(client, url, json_dict):
    """Helper to send POST requests with JSON."""
    return client.post(url, data=json.dumps(json_dict), content_type='application/json')

def test_index_route(client):
    """Ensure the frontend serves correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Flask Calculator' in response.data

def test_calculate_addition(client):
    response = post_json(client, '/calculate', {'num1': 10, 'num2': 5, 'operation': 'add'})
    assert response.status_code == 200
    assert response.get_json() == {'result': '15'}

def test_calculate_subtraction(client):
    response = post_json(client, '/calculate', {'num1': 10, 'num2': 5, 'operation': 'subtract'})
    assert response.status_code == 200
    assert response.get_json() == {'result': '5'}

def test_calculate_multiplication(client):
    response = post_json(client, '/calculate', {'num1': 10, 'num2': 5, 'operation': 'multiply'})
    assert response.status_code == 200
    assert response.get_json() == {'result': '50'}

def test_calculate_division(client):
    response = post_json(client, '/calculate', {'num1': 10, 'num2': 2, 'operation': 'divide'})
    assert response.status_code == 200
    assert response.get_json() == {'result': '5'}

def test_calculate_division_by_zero(client):
    response = post_json(client, '/calculate', {'num1': 10, 'num2': 0, 'operation': 'divide'})
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Division by zero'}

def test_calculate_invalid_operation(client):
    response = post_json(client, '/calculate', {'num1': 10, 'num2': 5, 'operation': 'modulus'})
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Unknown or missing operation'}

def test_calculate_wrong_media_type(client):
    # Sending raw data without 'application/json' triggers Flask's native 415
    response = client.post('/calculate', data="bad payload")
    assert response.status_code == 415

def test_calculate_empty_json(client):
    # Sending a valid JSON request but with an empty payload hits our custom 400 logic
    response = post_json(client, '/calculate', {})
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid request payload'}

def test_calculate_invalid_numbers(client):
    response = post_json(client, '/calculate', {'num1': 'apple', 'num2': 5, 'operation': 'add'})
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Inputs must be valid numbers'}