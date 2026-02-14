import sys
import os
import yaml
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

def load_config(config_path="app/config.yaml"):
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    app = QApplication(sys.argv)
    
    # Apply theme if needed (can be done in MainWindow or here)
    
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
