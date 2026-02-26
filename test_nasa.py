import requests
import pytest
import os

API_KEY = os.environ.get("NASA_API_KEY")
BASE_URL = "https://api.nasa.gov/planetary/apod"

@pytest.fixture
def apod_response():
    response = requests.get(BASE_URL, params={"api_key": API_KEY})
    return response

# --- Positive Tests ---

def test_status_code(apod_response):
    assert apod_response.status_code == 200

def test_response_is_json(apod_response):
    assert isinstance(apod_response.json(), dict)

def test_required_fields_present(apod_response):
    data = apod_response.json()
    assert "title" in data
    assert "date" in data
    assert "url" in data
    assert "explanation" in data

def test_media_type_is_valid(apod_response):
    data = apod_response.json()
    assert data["media_type"] in ["image", "video"]

def test_data_types(apod_response):
    data = apod_response.json()
    assert isinstance(data["title"], str)
    assert isinstance(data["date"], str)
    assert isinstance(data["explanation"], str)

def test_date_format(apod_response):
    data = apod_response.json()
    date = data["date"]
    assert len(date) == 10
    assert date[4] == "-"
    assert date[7] == "-"

def test_response_time(apod_response):
    assert apod_response.elapsed.total_seconds() < 3.0

# --- Parameterized Tests ---

@pytest.mark.parametrize("date", [
    "2024-01-01",
    "2023-06-15",
    "2022-12-25",
])
def test_apod_by_date(date):
    response = requests.get(BASE_URL, params={"api_key": API_KEY, "date": date})
    data = response.json()
    assert response.status_code == 200
    assert data["date"] == date
    assert "title" in data

# --- Negative Tests ---

def test_invalid_date_returns_error():
    response = requests.get(BASE_URL, params={"api_key": API_KEY, "date": "1800-01-01"})
    assert response.status_code == 400

def test_invalid_api_key():
    response = requests.get(BASE_URL, params={"api_key": "BADKEY123"})
    assert response.status_code == 403

def test_missing_api_key():
    response = requests.get(BASE_URL)
    assert response.status_code == 403

@pytest.mark.parametrize("bad_date", [
    "not-a-date",
    "2024-13-01",
    "2024-00-00",
])
def test_invalid_date_formats(bad_date):
    response = requests.get(BASE_URL, params={"api_key": API_KEY, "date": bad_date})
    assert response.status_code == 400
    
def test_apod_count():
    response = requests.get(BASE_URL, params={"api_key": API_KEY, "count": 5})
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 5