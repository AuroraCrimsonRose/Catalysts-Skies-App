import requests
from config import API_BASE_URL, DEBUG_OUTPUT
from cat_logger import logger
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in km

def clean_floats(obj):
    if isinstance(obj, dict):
        return {k: clean_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_floats(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj

def create_flight(flight_info, token):
    """Send a request to create a new flight."""
    url = f"{API_BASE_URL}/flights"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, json=flight_info, headers=headers)
        if DEBUG_OUTPUT:
            logger.info(f"POST {url} - {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to create flight: {e}")
        return None

def update_flight(flight_id, update_data, token):
    """Update flight data (e.g., position, status)."""
    url = f"{API_BASE_URL}/flights/{flight_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.put(url, json=update_data, headers=headers)
        if DEBUG_OUTPUT:
            logger.info(f"PUT {url} - {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to update flight: {e}")
        return None

def get_flight(flight_id, token):
    """Retrieve flight details."""
    url = f"{API_BASE_URL}/flights/{flight_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        if DEBUG_OUTPUT:
            logger.info(f"GET {url} - {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get flight: {e}")
        return None

def send_flight_point(flight_id, point_data, token):
    """Send a point-in-flight update (e.g., position, telemetry)."""
    url = f"{API_BASE_URL}/flights/{flight_id}/points"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(url, json=point_data, headers=headers)
        if DEBUG_OUTPUT:
            logger.info(f"POST {url} - {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send flight point: {e}")
        return None

def get_airport_info(icao):
    url = f"{API_BASE_URL}/airports/{icao}"
    try:
        response = requests.get(url)
        if DEBUG_OUTPUT:
            logger.info(f"GET {url} - {response.status_code}: {response.text}")
        response.raise_for_status()
        airport_data = response.json()
        return clean_floats(airport_data)
    except Exception as e:
        logger.error(f"Failed to get airport info for {icao}: {e}")
        return None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in km