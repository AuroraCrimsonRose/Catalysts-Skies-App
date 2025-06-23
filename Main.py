from dearpygui.dearpygui import *
from ui.login_ui import show_login_ui
from ui.dashboard_ui import show_dashboard_ui

# App config
APP_TITLE = "CATALYSTS Skies"

# Correct call order
create_context()

# Build GUI after context
create_viewport(title=APP_TITLE, width=1280, height=720)
setup_dearpygui()

# Load login first
show_login_ui(on_login_success=show_dashboard_ui)

# Run app
show_viewport()
start_dearpygui()
destroy_context()
