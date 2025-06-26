from dearpygui.dearpygui import *
from PIL import Image
import numpy as np
import os
import requests
import hashlib
from cat_logger import logger
from config import DEBUG_OUTPUT, API_BASE_URL

LOGO_PATH = os.path.abspath(os.path.join("assets", "logo.png"))
FOOTER_PATH = os.path.abspath(os.path.join("assets", "footer.png"))

login_state = {
    "token": None,
    "username": None,
    "gravatar_hash": None,
    "error": None
}

def show_error_popup(tag: str, message: str):
    if does_item_exist(tag):
        delete_item(tag)
    with window(modal=True, popup=True, tag=tag, no_title_bar=False, width=300, height=130):
        add_text(message, wrap=280)
        add_spacer(height=10)
        add_button(label="OK", width=270, callback=lambda: delete_item(tag))
        if DEBUG_OUTPUT:
            logger.error(f"Popup '{tag}' shown with message: {message}")


def load_texture_from_file(path: str, tag: str):
    if not os.path.exists(path):
        logger.error(f"[Texture] File '{path}' does not exist")
        return
    if does_item_exist(tag):
        return
    try:
        image = Image.open(path).convert("RGBA")
        width, height = image.size
        pixel_data = np.asarray(image, dtype=np.uint8)
        if pixel_data.shape[2] != 4:
            if DEBUG_OUTPUT:
                logger.warning(f"[Texture] Image '{path}' does not have an alpha channel, converting to RGBA")
            return
        normalized = pixel_data.astype(np.float32) / 255.0
        flat_data = normalized.flatten().tolist()
        with texture_registry():
            add_static_texture(width, height, flat_data, tag=tag)
        if DEBUG_OUTPUT:
            logger.info(f"[Texture] Loaded '{tag}' from '{path}' ({width}x{height})")
    except Exception as e:
        logger.error(f"[Texture] Failed to load '{tag}' from '{path}': {e}")

def _attempt_login(sender, app_data, user_data):
    username = get_value("login_username")
    password = get_value("login_token")
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            token_data = response.json()
            login_state["token"] = token_data["access_token"]
            login_state["username"] = username
            login_state["gravatar_hash"] = hashlib.md5(username.strip().lower().encode()).hexdigest()
            delete_item("login_window")
            user_data(username, token_data["access_token"])
        elif response.status_code == 401:
            show_error_popup("login_popup", "❌ Invalid username or password.")
        else:
            show_error_popup("login_popup", f"❌ Login failed: {response.status_code}\n{response.text}")
    except Exception as e:
        show_error_popup("login_popup", f"❌ Could not connect to server:\n{str(e)}")

def _attempt_register(sender, app_data, user_data):
    username = get_value("reg_username")
    email = get_value("reg_email")
    password = get_value("reg_password")
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json={
            "username": username,
            "email": email,
            "gravatar_email": email,
            "password": password
        })
        if response.status_code == 200:
            show_error_popup("register_popup", "✅ Registered successfully. You may now log in.")
        elif response.status_code == 400:
            msg = response.json().get("detail", "Invalid input")
            show_error_popup("register_popup", f"❌ {msg}")
        else:
            show_error_popup("register_popup", f"❌ Failed: {response.status_code}\n{response.text}")
    except Exception as e:
        show_error_popup("register_popup", f"❌ Could not connect to server:\n{str(e)}")


def show_register_window():
    if does_item_exist("register_window"):
        configure_item("register_window", show=True)
        return

    window_width = 280
    window_height = 550
    card_width = 260
    card_height = 420
    card_x = (window_width - card_width) // 2
    card_y = (window_height - card_height) // 2

    with window(tag="register_window", no_title_bar=True, no_move=True, no_resize=True, no_close=True,
                width=window_width, height=window_height,
                no_scrollbar=True, no_scroll_with_mouse=True):

        with drawlist(width=window_width, height=window_height, tag="register_wave_layer"):
            if does_item_exist("footer_texture"):
                texture_width = get_item_configuration("footer_texture")["width"]
                texture_height = get_item_configuration("footer_texture")["height"]
                display_height = int(window_width * (texture_height / texture_width))
                draw_image("footer_texture",
                           pmin=[0, window_height - display_height],
                           pmax=[window_width, window_height])

        with child_window(width=card_width, height=card_height, pos=[card_x, card_y], border=False,
                          no_scrollbar=True, no_scroll_with_mouse=True):
            add_spacer(height=30)
            if does_item_exist("logo_texture"):
                with group(horizontal=True):
                    add_spacer(width=(card_width-100)//2)
                    add_image("logo_texture", width=100, height=100)
            add_spacer(height=30)

            with group(horizontal=False):
                add_spacer(height=10)
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("👤")
                    add_input_text(label="", hint="Username", tag="reg_username", width=180)
                add_spacer(height=10)
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("📧")
                    add_input_text(label="", hint="Email", tag="reg_email", width=180)
                add_spacer(height=10)
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("🔑")
                    add_input_text(label="", hint="Password", tag="reg_password", password=True, width=180)
                add_spacer(height=20)
                with group(horizontal=True):
                    add_spacer(width=(card_width-180)//2)
                    add_button(label="REGISTER", width=180, callback=_attempt_register, user_data=None)
                add_spacer(height=10)
                with group(horizontal=True):
                    add_spacer(width=(card_width-120)//2)
                    add_button(label="Back to Login", callback=lambda: configure_item("register_window", show=False))
                add_spacer(height=30)
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("", tag="register_status", color=[255, 100, 100])


def show_login_ui(on_login_success):
    load_texture_from_file(LOGO_PATH, "logo_texture")
    load_texture_from_file(FOOTER_PATH, "footer_texture")

    window_width = 280
    window_height = 550
    card_width = 260
    card_height = 420
    card_x = (window_width - card_width) // 2
    card_y = (window_height - card_height) // 2

    with window(tag="login_window", no_title_bar=True, no_move=True, no_resize=True, no_close=True,
                width=window_width, height=window_height,
                no_scrollbar=True, no_scroll_with_mouse=True):

        with drawlist(width=window_width, height=window_height, tag="wave_layer"):
            if does_item_exist("footer_texture"):
                texture_width = get_item_configuration("footer_texture")["width"]
                texture_height = get_item_configuration("footer_texture")["height"]
                display_height = int(window_width * (texture_height / texture_width))
                draw_image("footer_texture",
                           pmin=[0, window_height - display_height],
                           pmax=[window_width, window_height])

        with child_window(width=card_width, height=card_height, pos=[card_x, card_y], border=False,
                          no_scrollbar=True, no_scroll_with_mouse=True):
            add_spacer(height=30)
            if does_item_exist("logo_texture"):
                with group(horizontal=True):
                    add_spacer(width=(card_width-100)//2)
                    add_image("logo_texture", width=100, height=100)
            add_spacer(height=30)

            with group(horizontal=False):
                add_spacer(height=10)
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("👤")
                    add_input_text(label="", hint="Username", tag="login_username", width=180)
                add_spacer(height=10)
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("🔑")
                    add_input_text(label="", hint="Password", tag="login_token", password=True, width=180)
                add_spacer(height=20)
                with group(horizontal=True):
                    add_spacer(width=(card_width-180)//2)
                    add_button(label="LOGIN", width=180, callback=_attempt_login, user_data=on_login_success)
                add_spacer(height=10)
                with group(horizontal=True):
                    add_spacer(width=(card_width-160)//2)
                    add_button(label="Register", callback=show_register_window)
                add_spacer(height=20)
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    with group(horizontal=False):
                        add_text("By logging in you agree to our", wrap=220)
                        add_text("privacy policy & terms of service", wrap=220)
                add_spacer(height=10)
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("", tag="login_status", color=[255, 100, 100])
