from dearpygui.dearpygui import *
import requests
import numpy as np
from PIL import Image
from io import BytesIO
from datetime import datetime
from ui import login_ui
from config import DEBUG_OUTPUT, API_BASE_URL
from cat_logger import logger

def load_texture_from_bytes(img_bytes, tag):
    try:
        image = Image.open(BytesIO(img_bytes)).convert("RGBA")
        width, height = image.size
        pixel_data = np.asarray(image, dtype=np.uint8)
        normalized = pixel_data.astype(np.float32) / 255.0
        flat_data = normalized.flatten().tolist()
        with texture_registry():
            add_static_texture(width, height, flat_data, tag=tag)
        if DEBUG_OUTPUT:
            logger.info(f"Loaded gravatar texture '{tag}' ({width}x{height})")
        return True
    except Exception as e:
        logger.error(f"Failed to decode gravatar image: {e}")
        return False

def logout_user():
    login_ui.login_state["token"] = None
    login_ui.login_state["username"] = None
    login_ui.login_state["gravatar_hash"] = None
    login_ui.login_state["error"] = None

    if DEBUG_OUTPUT:
        logger.info("User logged out.")

    delete_item("main_window", children_only=False)
    login_ui.show_login_ui(lambda u, t: logger.info("User re-logged in"))

def show_user_ui(token: str, on_logout=None):
    if not token:
        logger.warning("No token provided to show_user_ui()")
        with tab(label="User"):
            add_text("No token provided", color=[255, 100, 100])
        return

    headers = {"Authorization": f"Bearer {token}"}
    logger.info("Fetching user info from /users/me")

    try:
        response = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
        if DEBUG_OUTPUT:
            logger.info(f"Response status: {response.status_code}")
        logger.debug(f"Response content: {response.text}")

        if response.status_code == 200:
            user = response.json()
            gravatar_url = f"https://www.gravatar.com/avatar/{user['gravatar_hash']}?d=identicon"
        else:
            with tab(label="User"):
                add_text("Failed to load user data", color=[255, 100, 100])
                add_text(f"Server returned {response.status_code}: {response.text}", wrap=500)
            return
    except Exception as e:
        logger.error(f"Exception occurred while requesting user data: {str(e)}")
        with tab(label="User"):
            add_text("Could not connect to server", color=[255, 100, 100])
            add_text(str(e), wrap=500)
        return

    # Get company info
    company_info = "None"
    if user.get("company_id"):
        try:
            company_res = requests.get(f"{API_BASE_URL}/companies/{user['company_id']}", headers=headers)
            if company_res.status_code == 200:
                company = company_res.json()
                company_info = f"{company['name']} - {company['icao']}"
            else:
                company_info = "Unknown Company"
        except Exception as e:
            logger.warning(f"Failed to load company info: {e}")
            company_info = "Error loading company"

    # Format created_at
    try:
        created_at = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
        created_at_str = created_at.strftime("%B %d, %Y at %I:%M %p")
    except Exception as e:
        logger.warning(f"Error formatting created_at: {e}")
        created_at_str = user["created_at"]

    # Render UI
    with tab(label="User"):
        with child_window(tag="user_profile_content", width=-1, height=-1):
            add_spacer(height=20)
            add_text("User Profile", color=[200, 255, 255])
            add_separator()
            add_spacer(height=10)

            gravatar_tag = "gravatar_texture_user"
            try:
                gravatar_res = requests.get(gravatar_url)
                if gravatar_res.status_code == 200 and load_texture_from_bytes(gravatar_res.content, gravatar_tag):
                    add_image(gravatar_tag, width=100, height=100)
                else:
                    add_text("Gravatar could not be loaded")
            except Exception as e:
                logger.warning(f"Error loading gravatar: {e}")
                add_text("Gravatar error")

            add_spacer(height=10)
            add_text(f"Username: {user['username']}")
            add_text(f"Email: {user.get('email', 'Unavailable')}")
            add_text(f"Company: {company_info}")
            add_text(f"Account Created: {created_at_str}")
            add_spacer(height=10)
            add_button(label="Logout", callback=lambda: logout_user())

            add_spacer(height=20)
            if on_logout:
                add_button(label="Log Out", width=200, callback=on_logout)
