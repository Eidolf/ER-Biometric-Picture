import sys
import os
import time
import yaml
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
# Moved MainWindow import inside main() for lazy loading/splash screen optimization

# Redirect stdout/stderr to avoid crashes in no-console mode (Windows)
# This prevents "NoneType object has no attribute write" errors from libraries
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller OneFile creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # OneDir or Dev
        if getattr(sys, 'frozen', False):
            # OneDir: Resources are in the same dir as executable
            base_path = os.path.dirname(sys.executable)
        else:
            # Dev: Resources are in root, relative to app/main.py
            # app/main.py -> app/ -> root
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)

def load_config(config_path="app/config.yaml"):
    # Fix config path using resource logic
    config_path = get_resource_path(config_path)
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    app = QApplication(sys.argv)
    
    # Splash Screen
    logo_path = get_resource_path(os.path.join("images", "logo.png"))
    
    splash = None
    if os.path.exists(logo_path):
        pixmap = QPixmap(logo_path)
        # Scale if too large
        if pixmap.width() > 500:
             pixmap = pixmap.scaledToWidth(500, Qt.SmoothTransformation)
             
        splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()
    
    # Initialize Window (Models load here)
    # Lazy import to allow Splash Screen to show immediately
    from app.ui.main_window import MainWindow
    window = MainWindow(config)
    
    window.show()
    
    # Finish splash
    if splash:
        splash.finish(window)
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
