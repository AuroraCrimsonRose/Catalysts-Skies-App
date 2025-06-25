from SimConnect import *
import time

def connect_to_sim():
    try:
        sm = SimConnect()
        aq = AircraftRequests(sm, _time=2000)
        print("Connected to Microsoft Flight Simulator.")
        return sm, aq
    except Exception as e:
        print(f"Failed to connect to SimConnect: {e}")
        return None, None

def get_current_aircraft_data(aq):
    try:
        aircraft_data = {
            "title": aq.get("TITLE"),
            "latitude": aq.get("PLANE_LATITUDE"),
            "longitude": aq.get("PLANE_LONGITUDE"),
            "altitude": aq.get("PLANE_ALTITUDE"),
            "airspeed": aq.get("AIRSPEED_INDICATED"),
            "heading": aq.get("PLANE_HEADING_DEGREES_TRUE"),
            "icao": aq.get("ATC_MODEL"),
        }
        return aircraft_data
    except Exception as e:
        print(f"Error retrieving aircraft data: {e}")
        return None
