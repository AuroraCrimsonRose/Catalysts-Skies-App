from SimConnect import *
import time
from config import DEBUG_OUTPUT
from cat_logger import logger

def connect_to_sim():
    try:
        sm = SimConnect()
        aq = AircraftRequests(sm, _time=2000)
        if DEBUG_OUTPUT:
            logger.info("Connected to Microsoft Flight Simulator successfully.")
        return sm, aq
    except Exception as e:
        logger.error(f"Failed to connect to Microsoft Flight Simulator: {e}")
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
            "vertical_speed": aq.get("VERTICAL_SPEED"),
            "pitch": aq.get("PLANE_PITCH_DEGREES"),
            "bank": aq.get("PLANE_BANK_DEGREES"),
            "on_ground": aq.get("SIM_ON_GROUND"),
            "engine_rpm": aq.get("GENERAL_ENG_RPM:1"),
            "fuel_total": aq.get("FUEL_TOTAL_QUANTITY"),
            "flaps_position": aq.get("FLAPS_HANDLE_PERCENT"),
            "gear_position": aq.get("GEAR_HANDLE_POSITION"),
            "parking_brake": aq.get("PARKING_BRAKE_POSITION"),
            "sim_time": aq.get("ZULU_TIME"),
            "sim_rate": aq.get("SIM_RATE"),
            "ambient_temp": aq.get("AMBIENT_TEMPERATURE"),
            "wind_speed": aq.get("AMBIENT_WIND_VELOCITY"),
            "wind_direction": aq.get("AMBIENT_WIND_DIRECTION"),
        }
        return aircraft_data
    except Exception as e:
        logger.error(f"Error fetching aircraft data: {e}")
        return None

def calculate_landing_fpm(aq):
    """
    Calculates the vertical speed in feet per minute (FPM) at the moment of landing.
    Returns the FPM value if the aircraft has just landed, otherwise returns None.
    """
    try:
        # Get current on_ground and vertical_speed
        on_ground = aq.get("SIM_ON_GROUND")
        vertical_speed = aq.get("VERTICAL_SPEED")  # in feet per minute

        # Store previous state in function attribute
        if not hasattr(calculate_landing_fpm, "prev_on_ground"):
            calculate_landing_fpm.prev_on_ground = on_ground
            calculate_landing_fpm.prev_vertical_speed = vertical_speed
            return None

        # Detect transition from airborne to on ground (landing event)
        if not calculate_landing_fpm.prev_on_ground and on_ground:
            landing_fpm = calculate_landing_fpm.prev_vertical_speed
        else:
            landing_fpm = None

        # Update previous state
        calculate_landing_fpm.prev_on_ground = on_ground
        calculate_landing_fpm.prev_vertical_speed = vertical_speed

        return landing_fpm
    except Exception as e:
        logger.error(f"Error calculating landing FPM: {e}")
        return None
