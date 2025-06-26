# ui/dashboard_ui.py
from dearpygui.dearpygui import *
from ui.flights_ui import show_flights_ui
from ui.user_ui import show_user_ui
from ui.login_ui import login_state
from config import DEBUG_OUTPUT
from cat_logger import logger

# Dummy data source
def get_dashboard_stats():
    return {
        "flights": 12,
        "users": 46,
        "companies": 5,
        "news": [
            "Catalysts Skies v1.0 has launched!",
            "New aircraft added to the fleet.",
            "Cargo operations unlocked for Tier 2 companies."
        ]
    }

def show_dashboard_ui(username=None, token=None):
    with window(tag="main_window", no_title_bar=True, width=1280, height=720):

        with tab_bar(label="AppTabs", tag="main_tabs"):

            # --- Dashboard Tab ---
            with tab(label="Dashboard"):
                stats = get_dashboard_stats()

                add_spacer(height=20)  # or adjust the height you want
                add_text(f"Welcome, {username}!", bullet=False, color=[255, 255, 180])
                add_separator()
                add_spacer(height=10)

                with group(horizontal=True):
                    add_text(f"Active Flights: {stats['flights']}", color=[200, 255, 200])
                    add_spacer(width=40)
                    add_text(f"Total Users: {stats['users']}", color=[200, 200, 255])
                    add_spacer(width=40)
                    add_text(f"Total Companies: {stats['companies']}", color=[255, 200, 200])

                add_spacer(height=20)
                add_text("Latest News:", color=[255, 255, 220])
                add_separator()

                for news_item in stats['news']:
                    add_text(f"- {news_item}")

            show_flights_ui()
            add_tab(label="Company")
            show_user_ui(login_state["token"])
