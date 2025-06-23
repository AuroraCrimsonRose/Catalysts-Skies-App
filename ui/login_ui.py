# ui/login_ui.py
from dearpygui.dearpygui import *
from PIL import Image
import numpy as np
import os

LOGO_PATH = os.path.abspath(os.path.join("assets", "logo.png"))

# Load logo texture
def load_texture_from_file(path: str, tag: str):
    if not os.path.exists(path):
        print(f"[Texture] File not found: {path}")
        return

    if does_item_exist(tag):
        return

    try:
        image = Image.open(path).convert("RGBA")
        width, height = image.size

        pixel_data = np.asarray(image, dtype=np.uint8)
        if pixel_data.shape[2] != 4:
            print(f"[Texture] Invalid image shape: {pixel_data.shape}")
            return

        normalized = pixel_data.astype(np.float32) / 255.0
        flat_data = normalized.flatten().tolist()

        with texture_registry():
            add_static_texture(width, height, flat_data, tag=tag)
        print(f"[Texture] Loaded '{tag}' ({width}x{height})")
    except Exception as e:
        print(f"[Texture] Failed to load '{tag}': {e}")

# Generate points for a cubic Bezier curve
def bezier_points(p1, p2, p3, p4, num=30):
    t = np.linspace(0, 1, num)
    points = []
    for tt in t:
        x = (1-tt)**3*p1[0] + 3*(1-tt)**2*tt*p2[0] + 3*(1-tt)*tt**2*p3[0] + tt**3*p4[0]
        y = (1-tt)**3*p1[1] + 3*(1-tt)**2*tt*p2[1] + 3*(1-tt)*tt**2*p3[1] + tt**3*p4[1]
        points.append([x, y])
    return points

# Dummy login check
def _attempt_login(sender, app_data, user_data):
    username = get_value("login_username")
    token = get_value("login_token")

    if username and token:
        delete_item("login_window")
        user_data(username, token)
    else:
        set_value("login_status", "Username and token required.")   
                
def show_login_ui(on_login_success):
    load_texture_from_file(LOGO_PATH, "logo_texture")
    FOOTER_PATH = os.path.abspath(os.path.join("assets", "footer.png"))
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

        # Draw the footer image at the bottom (background)
        with drawlist(width=window_width, height=window_height, tag="wave_layer"):
            if does_item_exist("footer_texture"):
                # Get the original image size
                texture_width = get_item_configuration("footer_texture")["width"]
                texture_height = get_item_configuration("footer_texture")["height"]
                # Calculate display height to maintain aspect ratio
                display_height = int(window_width * (texture_height / texture_width))
                draw_image("footer_texture",
                           pmin=[0, window_height - display_height],
                           pmax=[window_width, window_height])

        # Centered card (foreground)
        with child_window(width=card_width, height=card_height, pos=[card_x, card_y], border=False,
                          no_scrollbar=True, no_scroll_with_mouse=True):
            add_spacer(height=30)
            # Centered logo
            if does_item_exist("logo_texture"):
                with group(horizontal=True):
                    add_spacer(width=(card_width-100)//2)
                    add_image("logo_texture", width=100, height=100)
            add_spacer(height=30)

            # Centered input fields and button
            with group(horizontal=False):
                # Username
                add_spacer(height=10)
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("👤")
                    add_input_text(label="", hint="Username", tag="login_username", width=180)
                add_spacer(height=10)
                # Password
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("🔑")
                    add_input_text(label="", hint="Token", tag="login_token", password=True, width=180)
                add_spacer(height=20)
                # Login button (shorter width, centered with input fields)
                with group(horizontal=True):
                    add_spacer(width=(card_width-180)//2)
                    add_button(label="LOGIN", width=180, callback=_attempt_login, user_data=on_login_success)
                add_spacer(height=10)
                # Forgot password
                with group(horizontal=True):
                    add_spacer(width=(card_width-140)//2)
                    add_text("FORGOT PASSWORD?", color=[100, 150, 255])
                add_spacer(height=30)
                # Policy text
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    with group(horizontal=False):
                        add_text("By logging in you agree to our", wrap=220)
                        add_text("privacy policy & terms of service", wrap=220)
                add_spacer(height=10)
                # Status
                with group(horizontal=True):
                    add_spacer(width=(card_width-220)//2)
                    add_text("", tag="login_status", color=[255, 100, 100])
