from dearpygui.dearpygui import *
import logging
import time
import threading
from config import DEBUG_OUTPUT
from cat_logger import logger
from flight_data import get_airport_info, haversine 
from PIL import Image
import re
import requests
import math
import os
import numpy as np

# Sim status tracking state
sim_status = {
    "connected": False,
    "tracking": False,
    "data": {},
    "flight_id": None,
    "flight_initialized": False,
    "flight_confirmed": False,
    "start_time": None,
    "pax": 150,
    "cargo": 2000,
    "aircraft": "",
    "flight_number": ""
}

def get_aircraft():
    return ["A320", "B738", "E175", "CRJ700"]

def normalize_icao(sender, app_data, user_data):
    value = re.sub(r'[^A-Za-z0-9]', '', app_data)[:4].upper()
    set_value(sender, value)

def format_runways(runways):
    lines = []
    for rwy in runways:
        le = rwy.get("le_ident", "N/A")
        he = rwy.get("he_ident", "N/A")
        le_head = rwy.get("le_heading_degT", "N/A")
        he_head = rwy.get("he_heading_degT", "N/A")
        surface = rwy.get("surface", "N/A")
        length = rwy.get("length_ft", "N/A")
        lines.append(
            f"  RWY {le}/{he}: {le_head}°/{he_head}° | {surface} | {length} ft"
        )
    return "\n".join(lines) if lines else "  No runway data available"

def format_airport_type(typ):
    if not typ:
        return "N/A"
    return typ.replace("_", " ").title()

def get_metar(icao):
    url = f"https://metar.vatsim.net/{icao}"
    try:
        response = requests.get(url, headers={'Accept': 'text/plain'}, timeout=5)
        metar = response.text.strip() if response.status_code == 200 else ""
        if not metar or "not found" in metar.lower():
            return "unavailable"
        return metar
    except Exception:
        return "unavailable"

def update_flight_details_panel(dep, arr, alt):
    # Prevent any two airports from being the same
    if dep == arr or dep == alt or arr == alt:
        for tag in ["dep_card", "arr_card", "alt_card", "flightdata_card"]:
            if does_item_exist(tag):
                delete_item(tag)
        show_error_popup("airport_duplicate", "Departure, Arrival, and Alternate airports must all be different.")
        return False

    dep_info = get_airport_info(dep)
    arr_info = get_airport_info(arr)
    alt_info = get_airport_info(alt)

    # If any airport is not found, show error and do not proceed
    if not dep_info or not arr_info or not alt_info:
        for tag in ["dep_card", "arr_card", "alt_card", "flightdata_card"]:
            if does_item_exist(tag):
                delete_item(tag)
        show_error_popup("airport_not_found", "One or more airport ICAO codes were not found. Please check your entries.")
        return False

    # Fetch METARs
    dep_metar = get_metar(dep)
    arr_metar = get_metar(arr)
    alt_metar = get_metar(alt)

    # Distances (convert km to NM)
    dist_dep_arr_km = haversine(dep_info["latitude"], dep_info["longitude"], arr_info["latitude"], arr_info["longitude"])
    dist_arr_alt_km = haversine(arr_info["latitude"], arr_info["longitude"], alt_info["latitude"], alt_info["longitude"])
    dist_dep_arr_nm = dist_dep_arr_km / 1.852
    dist_arr_alt_nm = dist_arr_alt_km / 1.852

    # Remove previous cards if present
    for tag in ["dep_card", "arr_card", "alt_card", "flightdata_card"]:
        if does_item_exist(tag):
            delete_item(tag)

    # Airport cards in a row
    with group(horizontal=True, parent="flight_details_group"):
        with child_window(tag="dep_card", width=380, height=250, border=True):
            add_text(f"Departure: {dep_info['name']} ({dep})", color=[0, 120, 215, 255])
            add_text(f"Type: {format_airport_type(dep_info.get('type', 'N/A'))}", color=[180, 180, 180, 255])
            add_text("Runways:", color=[180, 180, 180, 255])
            add_text(format_runways(dep_info.get("runways", [])), color=[220, 220, 220, 255])
            add_text("METAR:", color=[180, 180, 180, 255])
            add_text(dep_metar, color=[0, 255, 0, 255], wrap=300)

        with child_window(tag="arr_card", width=380, height=250, border=True):
            add_text(f"Arrival: {arr_info['name']} ({arr})", color=[0, 120, 215, 255])
            add_text(f"Type: {format_airport_type(arr_info.get('type', 'N/A'))}", color=[180, 180, 180, 255])
            add_text("Runways:", color=[180, 180, 180, 255])
            add_text(format_runways(arr_info.get("runways", [])), color=[220, 220, 220, 255])
            add_text("METAR:", color=[180, 180, 180, 255])
            add_text(arr_metar, color=[0, 255, 0, 255], wrap=300)

        with child_window(tag="alt_card", width=380, height=250, border=True):
            add_text(f"Alternate: {alt_info['name']} ({alt})", color=[0, 120, 215, 255])
            add_text(f"Type: {format_airport_type(alt_info.get('type', 'N/A'))}", color=[180, 180, 180, 255])
            add_text("Runways:", color=[180, 180, 180, 255])
            add_text(format_runways(alt_info.get("runways", [])), color=[220, 220, 220, 255])
            add_text("METAR:", color=[180, 180, 180, 255])
            add_text(alt_metar, color=[0, 255, 0, 255], wrap=300)

    # Flight data card below
    with child_window(tag="flightdata_card", width=1160, height=200, border=True, parent="flight_details_group"):
        add_text("Flight Data", color=[0, 120, 215, 255])
        add_separator()
        add_text(f"Flight Number: {sim_status.get('flight_number', '')}", color=[180, 180, 180, 255])
        add_text(f"Aircraft: {sim_status.get('aircraft', '')}", color=[180, 180, 180, 255])
        add_text(f"Distance: {dist_dep_arr_nm:.1f} NM (Dep-Arr)", color=[255, 215, 0, 255])
        add_text(f"Arr-Alt Distance: {dist_arr_alt_nm:.1f} NM", color=[255, 215, 0, 255])
        add_text(f"PAX: {sim_status.get('pax', 'N/A')}", color=[180, 180, 180, 255])
        add_text(f"Cargo: {sim_status.get('cargo', 'N/A')} kg", color=[180, 180, 180, 255])
    return True

# --- METAR auto-refresh thread ---
def metar_auto_refresh():
    while True:
        time.sleep(900)  # 15 minutes
        if sim_status["flight_initialized"]:
            dep = get_value("dep_icao")
            arr = get_value("arr_icao")
            alt = get_value("altn_icao")
            update_flight_details_panel(dep, arr, alt)

threading.Thread(target=metar_auto_refresh, daemon=True).start()

# UI callbacks

def initialize_flight():
    dep = get_value("dep_icao")
    arr = get_value("arr_icao")
    alt = get_value("altn_icao")
    acft = get_value("aircraft")
    flight_num = f"TEST{str(int(time.time()))[-4:]}"
    set_value("flight_number", flight_num)
    sim_status["flight_number"] = flight_num
    sim_status["aircraft"] = acft
    configure_item("accept_flight_btn", show=True)
    configure_item("deny_flight_btn", show=True)
    # Hide input fields
    for tag in ["dep_icao", "arr_icao", "altn_icao", "aircraft", "flight_number", "initialize_flight_btn"]:
        if does_item_exist(tag):
            configure_item(tag, show=False)
    sim_status["flight_initialized"] = True
    update_flight_details_panel(dep, arr, alt)
    if DEBUG_OUTPUT:
        logger.info("Flight initialized, awaiting confirmation.")

def accept_flight():
    dep = get_value("dep_icao")
    arr = get_value("arr_icao")
    alt = get_value("altn_icao")
    if not update_flight_details_panel(dep, arr, alt):
        return
    configure_item("accept_flight_btn", show=False)
    configure_item("deny_flight_btn", show=False)
    configure_item("track_flight_btn", show=True)
    configure_item("end_flight_btn", show=True)
    sim_status["flight_confirmed"] = True
    if DEBUG_OUTPUT:
        logger.info("Flight accepted and airport info displayed.")

def deny_flight():
    configure_item("accept_flight_btn", show=False)
    configure_item("deny_flight_btn", show=False)
    set_value("flight_number", "")
    sim_status["flight_initialized"] = False
    # Show input fields again
    for tag in ["dep_icao", "arr_icao", "altn_icao", "aircraft", "flight_number", "initialize_flight_btn"]:
        if does_item_exist(tag):
            configure_item(tag, show=True)
    # Remove cards
    for tag in ["dep_card", "arr_card", "alt_card", "flightdata_card"]:
        if does_item_exist(tag):
            delete_item(tag)
    if DEBUG_OUTPUT:
        logger.info("Flight denied, returning to planning.")

def connect_to_sim():
    sim_status["connected"] = True
    if DEBUG_OUTPUT:
        logger.info("SimConnect connected (placeholder).")

def start_tracking():
    if not sim_status["connected"]:
        set_value("tracking_status", "❌ Not connected to MSFS")
        return
    sim_status["tracking"] = True
    sim_status["start_time"] = time.time()
    set_value("tracking_status", "✅ Tracking Started")
    threading.Thread(target=track_updates, daemon=True).start()
    if DEBUG_OUTPUT:
        logger.info("Tracking started.")

def end_flight():
    # Reset sim_status
    sim_status.update({
        "tracking": False,
        "flight_id": None,
        "flight_initialized": False,
        "flight_confirmed": False,
        "start_time": None,
        "flight_number": "",
        "aircraft": "",
        "pax": 150,
        "cargo": 2000
    })
    # Show input fields again
    for tag in ["dep_icao", "arr_icao", "altn_icao", "aircraft", "flight_number", "initialize_flight_btn"]:
        if does_item_exist(tag):
            configure_item(tag, show=True)
    # Hide/clear buttons and status
    for tag in ["accept_flight_btn", "deny_flight_btn", "track_flight_btn", "end_flight_btn"]:
        if does_item_exist(tag):
            configure_item(tag, show=False)
    set_value("tracking_status", "")
    set_value("elapsed_time", "")
    set_value("telemetry_text", "")
    # Remove cards
    for tag in ["dep_card", "arr_card", "alt_card", "flightdata_card"]:
        if does_item_exist(tag):
            delete_item(tag)
    if DEBUG_OUTPUT:
        logger.info("Flight ended and UI reset.")

def track_updates():
    while sim_status["tracking"]:
        elapsed = int(time.time() - sim_status["start_time"])
        set_value("elapsed_time", f"Elapsed: {elapsed}s")
        set_value("telemetry_text", "Speed: 420kts\nAltitude: 32000ft\nFuel Used: 1200gal\nDistance: 312nm")
        if DEBUG_OUTPUT:
            logger.info("[TRACKING] Updated flight stats to server")
        time.sleep(5)

def show_error_popup(tag, message):
    if does_item_exist(tag):
        delete_item(tag)
    with window(modal=True, popup=True, tag=tag, no_title_bar=False, width=350, height=120):
        add_text(message, wrap=320)
        add_spacer(height=10)
        add_button(label="OK", width=320, callback=lambda: delete_item(tag))

def show_flights_ui():
    with tab(label="Flights"):
        add_text("Plan Your Flight", color=[0, 180, 255, 255])
        add_separator()
        add_spacer(height=10)

        add_input_text(label="Departure ICAO", tag="dep_icao", width=200, callback=normalize_icao)
        add_input_text(label="Arrival ICAO", tag="arr_icao", width=200, callback=normalize_icao)
        add_input_text(label="Alternate ICAO", tag="altn_icao", width=200, callback=normalize_icao)
        add_combo(label="Aircraft", items=get_aircraft(), tag="aircraft", width=250)
        add_input_text(label="Flight Number", tag="flight_number", readonly=True, width=250)
        add_button(label="Initialize Flight", tag="initialize_flight_btn", callback=initialize_flight)

        add_button(label="Accept Flight", tag="accept_flight_btn", callback=accept_flight, show=False)
        add_button(label="Deny Flight", tag="deny_flight_btn", callback=deny_flight, show=False)

        # Cards container
        add_group(tag="flight_details_group")

        add_button(label="Start Tracking", tag="track_flight_btn", callback=start_tracking, show=False)
        add_button(label="End Flight", tag="end_flight_btn", callback=end_flight, show=False)
        add_text("", tag="tracking_status")
        add_text("", tag="elapsed_time")
        add_text("", tag="telemetry_text")