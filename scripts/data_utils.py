import os
import yaml

class MapManager():
    def __init__(self, main_window):
        self.main_window = main_window

class settingManager():
    def __init__(self, crt_dir):
        self.crt_dir = crt_dir
        self.settings_file = os.path.join(crt_dir, "settings", "settings.yaml")
        self.stgs = self.load_settings(self.settings_file)

    def load_settings(self, sf_path):
        default_settings = {
            'zoom_factor': 1.5,
            'triangle_base_size': 0.3,
            'is_print': False,
            'drag_click_threshold': 10
        }
        if not os.path.exists(sf_path):
            return default_settings

        try:
            with open(sf_path, "r") as file:
                settings = yaml.safe_load(file)
                if settings is None:
                    settings = {}
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings

    def save_settings(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w") as file:
            yaml.dump(self.stgs, file)
