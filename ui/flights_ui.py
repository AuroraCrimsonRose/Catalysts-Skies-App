from dearpygui.dearpygui import *
import logging
import time
import threading

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Sim status tracking state
sim_status = {
    "connected": False,
    "tracking": False,
    "data": {},
    "flight_id": None,
    "flight_initialized": False,
    "flight_confirmed": False,
    "start_time": None
}

# Placeholder combo box data

def get_airports():
    return ["KDEN", "KLAX", "KSEA", "KATL", "KORD", "TEST"]

def get_aircraft():
    return ["A320", "B738", "CRJ7", "TEST"]

def get_altn_options():
    return ["KBOI", "KSLC", "KPDX", "TEST"]

# UI callbacks

def initialize_flight():
    # Placeholder: normally this would call the backend with flight details
    dep = get_value("dep_icao")
    arr = get_value("arr_icao")
    alt = get_value("altn_icao")
    acft = get_value("aircraft")
    flight_num = f"TEST{str(int(time.time()))[-4:]}"

    set_value("flight_number", flight_num)
    set_value("flight_details_text", f"Flight: {flight_num}\nFrom: {dep} To: {arr}\nAlternate: {alt}\nAircraft: {acft}\nPassengers/Cargo: Auto-calculated")
    configure_item("accept_flight_btn", show=True)
    configure_item("deny_flight_btn", show=True)
    sim_status["flight_initialized"] = True

    log.info("Flight initialized, awaiting confirmation.")

def accept_flight():
    configure_item("accept_flight_btn", show=False)
    configure_item("deny_flight_btn", show=False)
    configure_item("track_flight_btn", show=True)
    configure_item("flight_details_text", show=True)
    sim_status["flight_confirmed"] = True

    log.info("Flight accepted.")

def deny_flight():
    configure_item("accept_flight_btn", show=False)
    configure_item("deny_flight_btn", show=False)
    configure_item("flight_details_text", show=False)
    set_value("flight_number", "")
    sim_status["flight_initialized"] = False
    log.info("Flight denied, returning to planning.")

def connect_to_sim():
    sim_status["connected"] = True
    log.info("SimConnect connected (placeholder).")

def start_tracking():
    if not sim_status["connected"]:
        set_value("tracking_status", "❌ Not connected to MSFS")
        return
    sim_status["tracking"] = True
    sim_status["start_time"] = time.time()
    set_value("tracking_status", "✅ Tracking Started")
    threading.Thread(target=track_updates, daemon=True).start()
    log.info("Tracking started.")

def track_updates():
    while sim_status["tracking"]:
        elapsed = int(time.time() - sim_status["start_time"])
        set_value("elapsed_time", f"Elapsed: {elapsed}s")
        set_value("telemetry_text", "Speed: 420kts\nAltitude: 32000ft\nFuel Used: 1200gal\nDistance: 312nm")
        # Placeholder for calling /update
        log.info("[TRACKING] Updated flight stats to server")
        time.sleep(5)

def show_flights_ui():
    with tab(label="Flights"):
        add_text("Plan Your Flight", color=[255, 255, 200])
        add_separator()
        add_spacer(height=10)

        add_combo(label="Departure ICAO", items=get_airports(), tag="dep_icao", width=200)
        add_combo(label="Arrival ICAO", items=get_airports(), tag="arr_icao", width=200)
        add_combo(label="Alternate ICAO", items=get_altn_options(), tag="altn_icao", width=200)
        add_combo(label="Aircraft", items=get_aircraft(), tag="aircraft", width=250)
        add_input_text(label="Flight Number", tag="flight_number", readonly=True, width=250)
        add_button(label="Initialize Flight", callback=initialize_flight)

        add_button(label="✅ Accept Flight", tag="accept_flight_btn", callback=accept_flight, show=False)
        add_button(label="❌ Deny Flight", tag="deny_flight_btn", callback=deny_flight, show=False)
        add_text("", tag="flight_details_text", show=False)

        add_button(label="📡 Start Tracking", tag="track_flight_btn", callback=start_tracking, show=False)
        add_text("", tag="tracking_status")
        add_text("", tag="elapsed_time")
        add_text("", tag="telemetry_text")