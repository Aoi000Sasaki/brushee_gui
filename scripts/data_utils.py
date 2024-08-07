import os
import yaml


# NOTE: not use "path", use "overlay" instead
# NOTE: "node", "edge", ... is part of "element"
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
            'main_window': {
                'pos_x': 100,
                'pos_y': 100,
                'width': 1200,
                'height': 800
            },
            'map_widget': {
                'zoom_factor': 1.5
            },
            'map_graphics_view': {
                'move_mode': {
                    'click_th': 10
                },
                'node': {
                    'triangle_base_size': 0.3,
                    'del_pen': "#FF0000",
                    'del_pen_w': 2,
                    'del_brush': "#FF6464",
                    'mov_pen': "#FF0000",
                    'mov_pen_w': 2,
                    'mov_brush': "#FF6464"
                }
            }
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
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if sub_key not in settings[key]:
                                settings[key][sub_key] = sub_value
                            elif isinstance(sub_value, dict):
                                for sub_sub_key, sub_sub_value in sub_value.items():
                                    if sub_sub_key not in settings[key][sub_key]:
                                        settings[key][sub_key][sub_sub_key] = sub_sub_value
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings

    def save_settings(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w") as file:
            yaml.dump(self.stgs, file)
