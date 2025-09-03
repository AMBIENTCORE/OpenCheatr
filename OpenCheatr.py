import asyncio
import json
import threading
import webbrowser
from pathlib import Path
from statistics import mean
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, font
import os
import sys
import tempfile
import shutil
import platform
import requests

import folium
from folium.features import DivIcon
from playwright.async_api import async_playwright

try:
    from tkintermapview import TkinterMapView
    MAPVIEW_AVAILABLE = True
except ImportError:
    MAPVIEW_AVAILABLE = False

OPENGUESSR_URL = "https://openguessr.com/"
MAP_FILE = Path("opencheatr_round_map.html")

# -------------------- Configuration Class --------------------
class Config:
    """Main configuration class for styling and UI constants."""
    
    # Window Configuration
    WINDOW_TITLE = "OpenCheatr"
    WINDOW_SIZE = "1200x900"
    MIN_WINDOW_SIZE = (1200, 900)
    
    # Colors - Dark Theme
    COLORS = {
        "SUCCESS": "#4CAF50",  # Material Design Green
        "ERROR": "#F44336",    # Material Design Red
        "BACKGROUND": "#1e1e1e",  # Dark background
        "SECONDARY_BACKGROUND": "#252526",  # Slightly lighter dark background
        "TEXT": "#ffffff",  # White text
        "SECONDARY_TEXT": "#cccccc",  # Light gray text
        "VALID_ENTRY": "#1b3a1b",    # Dark green
        "INVALID_ENTRY": "#3a1b1b",  # Dark red
        "UPDATED_ROW": "#1b3a1b",    # Dark green
        "FAILED_ROW": "#3a1b1b",     # Dark red
        "PROGRESSBAR": {
            "GREEN": "#4CAF50",   # Material Design Green
            "ORANGE": "#FF9800",  # Material Design Orange
            "RED": "#F44336",     # Material Design Red
            "TROUGH": "#2d2d2d"   # Dark gray
        }
    }
    
    # Font Configuration
    FONTS = {
        "DEFAULT_SIZE": 10,
        "TABLE_SIZE": 8,
        "TABLE_HEADING_SIZE": 8,
        "LOG_SIZE": 9
    }
    
    # Style Configuration
    STYLES = {
        "THEME": "clam",
        "CUSTOM_FONT": {
            "FAMILY": "I pixel u",
            "FILE": "assets/I-pixel-u.ttf"
        },
        "WIDGET_PADDING": 5
    }
    
    # UI Dimensions
    DIMENSIONS = {
        "PROGRESS_BAR_LENGTH": 100,
        "TABLE_HEIGHT": 20,
        "DEBUG_LOG_HEIGHT": 8,
        "DEBUG_LOG_WIDTH": 80
    }

# -------------------- Styling Functions --------------------
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def style_button(button, is_danger=False):
    """Apply standard button styling with optional variants."""
    button.configure(
        font=custom_font,
        bg=Config.COLORS["SECONDARY_BACKGROUND"],
        fg="#990000" if is_danger else Config.COLORS["TEXT"],
        padx=Config.STYLES["WIDGET_PADDING"],
        pady=Config.STYLES["WIDGET_PADDING"]
    )

def style_entry(entry, font_size=None):
    """Apply standard entry field styling."""
    font_to_use = ('Consolas', font_size if font_size else Config.FONTS["TABLE_SIZE"])
    entry.configure(
        font=font_to_use,
        bg=Config.COLORS["SECONDARY_BACKGROUND"],
        fg=Config.COLORS["TEXT"],
        insertbackground=Config.COLORS["TEXT"]
    )

def style_label(label, use_smaller_font=False):
    """Apply standard label styling."""
    if custom_font:
        current_size = custom_font.cget("size")
        font_size = current_size - 1 if use_smaller_font else current_size
        font_family = custom_font.cget("family")
    else:
        font_family = Config.STYLES["CUSTOM_FONT"]["FAMILY"]
        font_size = Config.FONTS["DEFAULT_SIZE"] - (1 if use_smaller_font else 0)
        
    label.configure(
        font=(font_family, font_size),
        bg=Config.COLORS["BACKGROUND"],
        fg=Config.COLORS["TEXT"],
        bd=0
    )

def configure_styles(style, custom_font):
    """Configure all ttk styles for the application."""
    # Set theme
    style.theme_use(Config.STYLES["THEME"])
    
    # Configure dark theme styles
    style.configure('Dark.TPanedwindow', background=Config.COLORS["BACKGROUND"], sashwidth=0)
    style.configure('TFrame', background=Config.COLORS["BACKGROUND"])
    style.configure('TButton', padding=Config.STYLES["WIDGET_PADDING"], font=custom_font, 
                   background=Config.COLORS["SECONDARY_BACKGROUND"], foreground=Config.COLORS["TEXT"], 
                   relief="solid", borderwidth=1)
    style.map('TButton',
        relief=[('pressed', 'sunken'), ('!pressed', 'solid')],
        borderwidth=[('pressed', 1), ('!pressed', 1)])
    style.configure('TEntry', padding=Config.STYLES["WIDGET_PADDING"], 
                   fieldbackground=Config.COLORS["SECONDARY_BACKGROUND"], foreground=Config.COLORS["TEXT"])
    style.configure('TLabel', background=Config.COLORS["BACKGROUND"], foreground=Config.COLORS["TEXT"], font=custom_font)
    style.configure('TText', padding=Config.STYLES["WIDGET_PADDING"], 
                   background=Config.COLORS["SECONDARY_BACKGROUND"], foreground=Config.COLORS["TEXT"])
    
    # LabelFrame styles - this is what was missing!
    style.configure('TLabelframe', background=Config.COLORS["BACKGROUND"], foreground=Config.COLORS["TEXT"])
    style.configure('TLabelframe.Label', background=Config.COLORS["BACKGROUND"], foreground=Config.COLORS["TEXT"], font=custom_font)
    
    # Table styles with dark theme
    style.configure('Treeview', 
                   rowheight=15,
                   font=('Consolas', Config.FONTS["TABLE_SIZE"]),
                   background=Config.COLORS["SECONDARY_BACKGROUND"],
                   foreground=Config.COLORS["TEXT"],
                   fieldbackground=Config.COLORS["SECONDARY_BACKGROUND"])
    style.configure('Treeview.Heading', 
                   font=('Consolas', Config.FONTS["TABLE_HEADING_SIZE"], 'bold'),
                   background=Config.COLORS["BACKGROUND"],
                   foreground=Config.COLORS["TEXT"])

def create_styled_button(parent, text, command, is_danger=False):
    """Create and return a styled button."""
    button = tk.Button(parent, text=text, command=command)
    style_button(button, is_danger=is_danger)
    return button

def create_styled_entry(parent, textvariable=None, width=None, justify=None):
    """Create and return a styled entry field."""
    entry = tk.Entry(parent, textvariable=textvariable, width=width, justify=justify)
    style_entry(entry)
    return entry

def create_styled_text(parent, width=None, height=None, state="normal", wrap="word"):
    """Create and return a styled text widget."""
    text = tk.Text(parent, width=width, height=height, state=state, wrap=wrap)
    text.configure(
        font=('Consolas', Config.FONTS["TABLE_SIZE"]),
        bg=Config.COLORS["SECONDARY_BACKGROUND"],
        fg=Config.COLORS["TEXT"],
        insertbackground=Config.COLORS["TEXT"]
    )
    return text

# Global variable for custom font
custom_font = None

# -------------------- Location Information Functions --------------------
def get_location_info(lat, lon):
    """Get location information from coordinates using reverse geocoding."""
    try:
        # Using Nominatim (OpenStreetMap) reverse geocoding service
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
        headers = {
            'User-Agent': 'OpenCheatr/1.0 (Educational Purpose)'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            # Extract location components
            country = address.get('country', 'Unknown Country')
            state = address.get('state', '')
            city = address.get('city') or address.get('town') or address.get('village', '')
            county = address.get('county', '')
            
            # Build location string
            location_parts = []
            if city:
                location_parts.append(city)
            if county and county != city:
                location_parts.append(county)
            if state and state not in location_parts:
                location_parts.append(state)
            if country:
                location_parts.append(country)
            
            location_str = ', '.join(location_parts) if location_parts else 'Unknown Location'
            
            return {
                'country': country,
                'location': location_str,
                'full_address': data.get('display_name', 'Unknown Location')
            }
    except Exception as e:
        print(f"Error getting location info: {e}")
    
    return {
        'country': 'Unknown',
        'location': 'Unknown Location',
        'full_address': 'Unknown Location'
    }

# -------------------- Map helpers --------------------
def build_round_map(locations):
    """
    locations: list of [lat, lon] pairs, length 5
    """
    if not locations:
        return

    # Center the map roughly on the average of points
    center_lat = mean([lat for lat, _ in locations])
    center_lon = mean([lon for _, lon in locations])

    m = folium.Map(location=[center_lat, center_lon], zoom_start=3, control_scale=True)

    # Add numbered pins 1..5
    for idx, (lat, lon) in enumerate(locations, start=1):
        # A small marker + a big number label for clarity
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            fill=True,
            fill_opacity=0.9,
            opacity=1,
        ).add_to(m)

        folium.Marker(
            location=[lat, lon],
            tooltip=f"Round {idx}: {lat:.6f}, {lon:.6f}",
            popup=f"Round {idx}: {lat:.6f}, {lon:.6f}",
            icon=DivIcon(
                icon_size=(24, 24),
                icon_anchor=(12, 12),
                html=f'<div style="font-weight:700;font-size:14px;'
                     f'border-radius:12px;padding:2px 6px;'
                     f'background:rgba(255,255,255,0.85);'
                     f'border:1px solid #333;'
                     f'transform: translate(-50%,-26px);">{idx}</div>'
            ),
        ).add_to(m)

    # Add a gentle auto-refresh so you can leave the file open
    m.get_root().html.add_child(folium.Element(
        '<meta http-equiv="refresh" content="5">'
    ))
    m.save(str(MAP_FILE))


# -------------------- Playwright watcher --------------------
async def watch_openguessr(log, on_locations):
    """
    log: callable(str) -> None
    on_locations: callable(list[[lat,lon]]) -> None
    """
    async with async_playwright() as p:
        log("Launching Chromium…")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        log("Attaching network listener…")

        # Debounce: only handle first 'locations-batch' per round-load
        seen_batches = set()

        async def on_response(resp):
            url = resp.url
            if "locations-batch" not in url:
                return
            # avoid double-handling the same response
            req_id = f"{url}|{resp.request.timing.get('startTime', 0)}"
            if req_id in seen_batches:
                return
            seen_batches.add(req_id)

            try:
                ctype = (resp.headers or {}).get("content-type", "").lower()
                if "application/json" not in ctype:
                    return
                data = await resp.json()
            except Exception:
                return

            if not isinstance(data, dict):
                return
            locs = data.get("locations")
            if not (isinstance(locs, list) and len(locs) >= 5 and all(isinstance(x, list) and len(x) == 2 for x in locs)):
                return

            # Normalize to floats
            try:
                coords = [(float(a), float(b)) for a, b in locs[:5]]
            except Exception:
                return

            log("🎯 Detected locations-batch with 5 rounds.")
            on_locations(coords)

        # Register the event handler
        page.on("response", on_response)

        log(f"Opening {OPENGUESSR_URL}")
        await page.goto(OPENGUESSR_URL, wait_until="domcontentloaded")

        log("Ready. Start a game; when the round loads, I'll grab the 5 coordinates.")
        # Keep running until the user closes the browser window
        try:
            while True:
                await asyncio.sleep(0.2)
        except asyncio.CancelledError:
            pass
        finally:
            await browser.close()


# -------------------- Map Display Class --------------------
class MapDisplay:
    def __init__(self, parent, width=600, height=400):
        self.parent = parent
        self.width = width
        self.height = height
        self.markers = []
        
        # Create frame for the map
        self.map_frame = tk.Frame(parent, bg=Config.COLORS["SECONDARY_BACKGROUND"])
        self.map_frame.pack(fill=tk.BOTH, expand=True)
        
        if MAPVIEW_AVAILABLE:
            self.create_tkinter_map()
        else:
            self.create_fallback_display()
    
    def create_tkinter_map(self):
        """Create map using TkinterMapView"""
        try:
            # Create the map widget
            self.map_widget = TkinterMapView(self.map_frame, width=self.width, height=self.height, corner_radius=0)
            self.map_widget.pack(fill=tk.BOTH, expand=True)
            
            # Set initial position to world view (zoomed out to fit all)
            self.map_widget.set_position(0.0, 0.0)  # Center of world
            self.map_widget.set_zoom(1)  # Very zoomed out to show whole world
            
            # Add initial message
            self.show_waiting_message()
            
        except Exception as e:
            print(f"TkinterMapView error: {e}")
            self.create_fallback_display()
    
    def create_fallback_display(self):
        """Create fallback display when TkinterMapView is not available"""
        # Clear frame
        for widget in self.map_frame.winfo_children():
            widget.destroy()
        
        # Create waiting display
        self.waiting_label = tk.Label(self.map_frame, 
                                    text="🗺️ Map Display\n\nTkinterMapView not available.\nInstall with: pip install tkintermapview\n\nMap will open in browser when locations are detected.",
                                    font=custom_font, fg=Config.COLORS["TEXT"], bg=Config.COLORS["SECONDARY_BACKGROUND"],
                                    justify=tk.CENTER)
        self.waiting_label.pack(expand=True)
    
    def show_waiting_message(self):
        """Show waiting message on the map"""
        if MAPVIEW_AVAILABLE and hasattr(self, 'map_widget'):
            # Clear existing markers
            self.clear_markers()
            
            # Add a temporary marker with instructions
            self.map_widget.set_marker(0, 0, text="Waiting for locations...\nStart a game to see pins!")
    
    def update_map(self, coords):
        """Update the map with new coordinates"""
        if not MAPVIEW_AVAILABLE:
            self.create_fallback_display()
            return
        
        if not hasattr(self, 'map_widget'):
            return
        
        # Clear existing markers
        self.clear_markers()
        
        if not coords or len(coords) < 5:
            return
        
        # Add markers for each location
        for i, (lat, lon) in enumerate(coords[:5], 1):
            marker = self.map_widget.set_marker(lat, lon, text=f"Round {i}")
            self.markers.append(marker)
        
        # Center the map on the average of all points
        if coords:
            avg_lat = sum(lat for lat, _ in coords) / len(coords)
            avg_lon = sum(lon for _, lon in coords) / len(coords)
            self.map_widget.set_position(avg_lat, avg_lon)
            self.map_widget.set_zoom(3)  # Zoom to show all points (adjusted for full-width layout)
    
    def clear_markers(self):
        """Clear all markers from the map"""
        if MAPVIEW_AVAILABLE and hasattr(self, 'map_widget'):
            # Clear all markers
            self.map_widget.delete_all_marker()
            self.markers = []
    
    def open_in_browser(self):
        """Open the map in browser as fallback"""
        if MAP_FILE.exists():
            webbrowser.open(MAP_FILE.resolve().as_uri())
        else:
            messagebox.showinfo("Map", "No map has been generated yet.")


# -------------------- Tk UI + thread/async glue --------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title(Config.WINDOW_TITLE)
        root.geometry(Config.WINDOW_SIZE)
        root.minsize(*Config.MIN_WINDOW_SIZE)
        
        # Set ttk style to clam
        style = ttk.Style()
        
        # Load custom font
        global custom_font
        custom_font_path = resource_path(Config.STYLES["CUSTOM_FONT"]["FILE"])
        if not os.path.exists(custom_font_path):
            print(f"Warning: Font file '{custom_font_path}' not found! Using default font.")
            custom_font = font.Font(family="Arial", size=Config.FONTS["DEFAULT_SIZE"])
        else:
            # EMBED the font directly into tkinter
            try:
                # Check if font is already available
                available_fonts = font.families()
                if Config.STYLES["CUSTOM_FONT"]["FAMILY"] not in available_fonts:
                    # Try to load the font using the correct tkinter method
                    if platform.system() == 'Windows':
                        # On Windows, try to copy font to temp directory and load it
                        temp_font_path = os.path.join(tempfile.gettempdir(), os.path.basename(custom_font_path))
                        shutil.copy2(custom_font_path, temp_font_path)
                        
                        # Try to load from temp location
                        root.tk.call('tk', 'fontCreate', Config.STYLES["CUSTOM_FONT"]["FAMILY"], 
                                    '-file', temp_font_path)
                    else:
                        # On other platforms, try direct loading
                        root.tk.call('tk', 'fontCreate', Config.STYLES["CUSTOM_FONT"]["FAMILY"], 
                                    '-file', custom_font_path)
                
                custom_font = font.Font(family=Config.STYLES["CUSTOM_FONT"]["FAMILY"], size=Config.FONTS["DEFAULT_SIZE"])
                print(f"[SUCCESS] Custom font '{Config.STYLES['CUSTOM_FONT']['FAMILY']}' embedded successfully")
            except Exception as e:
                print(f"Warning: Failed to embed custom font '{Config.STYLES['CUSTOM_FONT']['FAMILY']}': {e}. Using default font.")
                custom_font = font.Font(family="Arial", size=Config.FONTS["DEFAULT_SIZE"])
        
        # Configure all styles
        configure_styles(style, custom_font)
        
        # Configure the root window background
        root.configure(bg=Config.COLORS["BACKGROUND"])
        
        # Create main container with vertical paned window
        self.main_paned = ttk.PanedWindow(root, orient=tk.VERTICAL, style='Dark.TPanedwindow')
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top panel for controls and logs (fixed height)
        self.top_frame = ttk.Frame(self.main_paned, height=180)  # Fixed height
        self.top_frame.pack_propagate(False)  # Prevent shrinking
        self.main_paned.add(self.top_frame, weight=0)  # Fixed size
        
        # Bottom panel for map (takes remaining space)
        self.bottom_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.bottom_frame, weight=1)
        
        self.setup_controls()
        self.setup_debug_panel()
        self.setup_map_panel()
        
        self.loop = None
        self.thread = None
        self.running = False

    def setup_controls(self):
        """Setup control buttons in horizontal layout"""
        # Create horizontal container for controls and logs
        self.top_container = ttk.Frame(self.top_frame)
        self.top_container.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Controls
        controls_frame = ttk.Frame(self.top_container, padding=10)
        controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.btn = create_styled_button(controls_frame, "LAUNCH", 
                                      self.start_listener)
        self.btn.configure(fg=Config.COLORS["SUCCESS"])  # Green text
        self.btn.pack(pady=5, fill=tk.X)
        
        self.detailed_map_btn = create_styled_button(controls_frame, 
                                                   "OPEN WEB MAP", 
                                                   self.open_detailed_map)
        self.detailed_map_btn.config(state=tk.DISABLED)
        self.detailed_map_btn.pack(pady=5, fill=tk.X)
        
        self.clear_map_btn = create_styled_button(controls_frame, 
                                                "CLEAR", 
                                                self.clear_map, is_danger=True)
        self.clear_map_btn.config(state=tk.DISABLED)
        self.clear_map_btn.pack(pady=5, fill=tk.X)
        


    def setup_debug_panel(self):
        """Setup debug/log panel in horizontal layout"""
        debug_frame = ttk.Frame(self.top_container, padding=5)
        debug_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.logbox = create_styled_text(debug_frame, width=Config.DIMENSIONS["DEBUG_LOG_WIDTH"], 
                                       height=Config.DIMENSIONS["DEBUG_LOG_HEIGHT"], state=tk.DISABLED)
        self.logbox.pack(fill=tk.BOTH, expand=True)

    def setup_map_panel(self):
        """Setup map display panel at bottom"""
        map_frame = ttk.Frame(self.bottom_frame)
        map_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create embedded map widget (full width, taller)
        self.embedded_map = MapDisplay(map_frame, width=1200, height=500)

    def log(self, msg: str):
        """Add message to debug log"""
        self.logbox.configure(state=tk.NORMAL)
        self.logbox.insert(tk.END, msg + "\n")
        self.logbox.see(tk.END)
        self.logbox.configure(state=tk.DISABLED)
        self.root.update_idletasks()



    def open_detailed_map(self):
        """Open the detailed map in browser"""
        self.embedded_map.open_in_browser()

    def clear_map(self):
        """Clear the map display"""
        if hasattr(self, 'embedded_map'):
            self.embedded_map.clear_markers()
            self.embedded_map.show_waiting_message()
        self.detailed_map_btn.config(state=tk.DISABLED)
        self.clear_map_btn.config(state=tk.DISABLED)
        self.btn.config(state=tk.NORMAL)  # Re-enable the LAUNCH button
        self.log("🗑️ Map cleared")

    def on_locations(self, coords):
        """Handle detected locations"""
        # Build map
        build_round_map(coords)
        self.log("🎯 Detected locations-batch with 5 rounds.")
        self.log("🗺️ Generated map with 5 numbered pins")
        
        # Display detailed location information
        self.log("📍 Location Details:")
        for i, (lat, lon) in enumerate(coords[:5], 1):
            self.log(f"{i}. Coordinates: {lat:.6f}, {lon:.6f}")
            
            # Get location info synchronously for each coordinate
            location_info = get_location_info(lat, lon)
            self.log(f"   Location: {location_info['location']}")
        
        # Update the embedded map
        self.embedded_map.update_map(coords)
        
        # Enable buttons
        self.detailed_map_btn.config(state=tk.NORMAL)
        self.clear_map_btn.config(state=tk.NORMAL)

    def start_listener(self):
        """Start the OpenGuessr listener"""
        if self.running:
            return
        self.running = True
        self.btn.config(state=tk.DISABLED)


        def runner():
            # Dedicated asyncio loop in this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(watch_openguessr(self.log, self.on_locations))
            except Exception as e:
                self.log(f"ERROR: {e}")

            finally:
                self.running = False
                self.btn.config(state=tk.NORMAL)


        self.thread = threading.Thread(target=runner, daemon=True)
        self.thread.start()
        self.log("Listener started. A Chromium window will open.")


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()