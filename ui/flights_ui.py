# ui/flights_ui.py
from dearpygui.dearpygui import *

# Placeholder functions for airport/aircraft logic
def get_airports():
    return ["KDEN", "KLAX", "KSEA", "KATL", "KORD", "TEST"]

def get_available_aircraft(departure):
    return ["A320 - N123AA", "B738 - N456BB", "CRJ7 - N789CC", "TEST - N0000X"]

def get_altn_options(arrival):
    return ["KBOI", "KSLC", "KPDX", "TEST"]

def start_flight(sender, app_data, user_data):
    dep = get_value("dep_icao")
    arr = get_value("arr_icao")
    alt = get_value("altn_icao")
    acft = get_value("aircraft")
    print(f"Flight started: {dep} -> {arr}, ALT: {alt}, Aircraft: {acft}")

def show_flights_ui():
    with tab(label="Flights"):
        add_text("Plan Your Flight", color=[255, 255, 200])
        add_separator()
        add_spacer(height=10)

        add_combo(label="Departure ICAO", items=get_airports(), tag="dep_icao", width=200)
        add_combo(label="Arrival ICAO", items=get_airports(), tag="arr_icao", width=200)

        add_spacer(height=5)
        add_combo(label="Alternate ICAO", items=get_altn_options(""), tag="altn_icao", width=200)
        add_combo(label="Aircraft at Departure", items=get_available_aircraft(""), tag="aircraft", width=250)

        add_spacer(height=10)
        add_button(label="Start Flight", callback=start_flight)
