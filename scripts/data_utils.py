import os
import yaml
import numpy as np
from PIL import Image
from PyQt5.QtGui import QImage, QPixmap, QPen, QColor, QBrush
import math

# NOTE: not use "path", use "overlay" instead
# NOTE: "node", "edge", ... is part of "element"
class MapManager():
    def __init__(self, main_window):
        self.main_window = main_window
        setting_manager = main_window.setting_manager
        self.sm = setting_manager.stgs["map_manager"]
        self.data_loaded = None
        self.elements = []
        self.elements_path = None
        self.map_yaml_path = None
        self.map_pgm_path = None # need ?
        self.map_png_path = None # need ?
        self.is_saved = True

    def load_elements(self, elements_path):
        self.elements_path = elements_path
        with open(elements_path, 'r') as file:
            self.data_loaded = yaml.safe_load(file)
        if "OCC_MAP_NAME" in self.data_loaded:
            self.map_yaml_path = self.data_loaded["OCC_MAP_NAME"]


    def show_loaded_elements(self):
        if self.data_loaded is None:
            print("Error: No elements loaded")
            return
        else:
            for node in self.data_loaded["NODE"]:
                self.register_node(node)

    # TODO: key not found error
    def load_map(self, map_yaml_path):
        if not os.path.exists(map_yaml_path):
            print(f"Error: {map_yaml_path} not exists")
            return False

        self.map_yaml_path = map_yaml_path
        with open(map_yaml_path, 'r') as file:
            map_info = yaml.safe_load(file)

        self.resolution = map_info['resolution']
        self.origin = map_info['origin']
        self.negate = map_info['negate']
        self.occupied_thresh = map_info['occupied_thresh']
        self.free_thresh = map_info['free_thresh']
        map_pgm_name = map_info['image']
        map_dir = os.path.dirname(map_yaml_path)
        self.map_pgm_path = os.path.join(map_dir, map_pgm_name)
        self.load_map_pgm(self.map_pgm_path)

        return True

    def load_map_pgm(self, map_pgm_path):
        with open(map_pgm_path, 'rb') as file:
            self.map_type = file.readline()
            file.readline()  # to read comment line
            self.w_p, self.h_p = map(int, file.readline().split())
            self.max_val = int(file.readline())
            if self.map_type == b'P5\n':
                self.bytes_map = file.read()
                self.convert2pil()
            else:
                print(f"Error: Unsupported map type: {self.map_type}")
                self.bytes_map = None
                self.pil_map = None

    def convert2pil(self):
        map_np = np.zeros((self.h_p, self.w_p), dtype=np.uint8)
        for i in range(len(self.bytes_map)):
            if self.negate:
                cell = (self.max_val - self.bytes_map[i]) / self.max_val
            else:
                cell = self.bytes_map[i] / self.max_val

            if cell > self.occupied_thresh:
                map_np[i // self.w_p, i % self.w_p] = self.max_val
            elif cell < self.free_thresh:
                map_np[i // self.w_p, i % self.w_p] = 0
            else:
                map_np[i // self.w_p, i % self.w_p] = int(cell * self.max_val)

        self.pil_map = Image.fromarray(map_np)

    # reset graphics view and show map by calling graphics_view.set_map()
    # (scene.clear is called in set_map())
    # NOTE: this function should be called before show_loaded_elements()
    def show_loaded_map(self):
        map_q = QImage(self.pil_map.tobytes(), self.pil_map.width, self.pil_map.height, QImage.Format_Grayscale8)
        map_pix = QPixmap.fromImage(map_q)
        gv = self.main_window.map_widget.graphics_view
        gv.set_map(map_pix)

    # reset only manager data
    # elements in scene and map data are reset when call show_loaded_map()
    def reset_data(self):
        self.data_loaded = None
        self.elements = []
        self.elements_path = None
        self.map_yaml_path = None
        self.map_pgm_path = None
        self.map_png_path = None
        self.is_saved = True

    def coord2pixel(self, coord):
        x_p, y_p = coord
        x_c = (x_p - self.origin[0]) / self.resolution
        y_c = -(y_p + self.origin[1]) / self.resolution
        return x_c, y_c

    def pixel2coord(self, pixel):
        x_c, y_c = pixel
        x_p = x_c * self.resolution + self.origin[0]
        y_p = -y_c * self.resolution - self.origin[1]
        return x_p, y_p

    def get_clicked_element(self, point):
        for element in self.elements:
            if element.item.contains(point):
                return element

        return None

    def add_node(self, point):
        x_c, y_c = self.pixel2coord((point.x(), point.y()))

        node = {
            "id": -1, # 仮設定。update_nodes()で先頭のnodeからidを振り直す。
            "pose": {
                "x": x_c,
                "y": y_c,
                "direction": "head"
            },
            "type": 1
        }

        self.register_node(node)

    def register_node(self, node):
        gv = self.main_window.map_widget.graphics_view
        x_c = node["pose"]["x"]
        y_c = node["pose"]["y"]
        x_p, y_p = self.coord2pixel((x_c, y_c))

        direction = node["pose"]["direction"]
        node_item = gv.draw_node(x_c, y_c, direction)

        internal_data = {
            "x_p": x_p,
            "y_p": y_p,
            "angle": 0
        }
        element = Element("NODE", node, internal_data=internal_data, item=node_item)

        self.elements.append(element)
        self.update_elements()

        print(f"Add node {node['id']} at ({x_c:.2f}, {y_c:.2f})")

    def delete_element(self, element, update=True):
        # TODO: use try-except
        if not element in self.elements:
            print("Error: Element not in elements")
            return
        gv = self.main_window.map_widget.graphics_view
        gv.scene.removeItem(element.item)
        self.elements.remove(element)

        if update:
            self.update_elements()
            print(f"Delete {element.attribute} {element.data['id']}")

    def switch_node_direction(self, element):
        sm = self.main_window.setting_manager
        sm_node = sm.stgs["map_graphics_view"]["node"]
        if element.data["pose"]["direction"] == "head":
            element.data["pose"]["direction"] = "keep"
            pen = QPen(QColor(sm_node["kn_pen"]))
            pen.setWidth(sm_node["kn_pen_w"])
            brush = QBrush(QColor(sm_node["kn_brush"]))
        elif element.data["pose"]["direction"] == "keep":
            element.data["pose"]["direction"] = "head"
            pen = QPen(QColor(sm_node["hn_pen"]))
            pen.setWidth(sm_node["hn_pen_w"])
            brush = QBrush(QColor(sm_node["hn_brush"]))
        else:
            print("Error: Invalid direction")

        element.item.setPen(pen)
        element.item.setBrush(brush)
        self.update_elements()

        print(f"Switch direction of node {element.data['id']}")

    def move_element(self, element, point, finalize=False):
        x_c, y_c = self.pixel2coord((point.x(), point.y()))
        if not finalize:
            dx = point.x() - element.internal_data["x_p"]
            dy = point.y() - element.internal_data["y_p"]
            element.item.moveBy(dx, dy)
            element.item.update()
        else:
            gv = self.main_window.map_widget.graphics_view
            direction = element.data["pose"]["direction"]
            new_elem = gv.draw_node(x_c, y_c, direction)
            gv.scene.removeItem(element.item)
            element.item = new_elem

        element.internal_data["x_p"] = point.x()
        element.internal_data["y_p"] = point.y()
        element.data["pose"]["x"] = x_c
        element.data["pose"]["y"] = y_c

        self.update_elements()

        print(f"Move {element.attribute} {element.data['id']} to ({x_c:.2f}, {y_c:.2f})")

    def update_elements(self):
        self.update_edges()
        self.update_nodes()
        self.is_saved = False

    def update_edges(self):
        # delete all edges (POWER IMPLEMENTATION)
        elements_to_delete = []
        for element in self.elements:
            if element.attribute == "EDGE":
                elements_to_delete.append(element)

        for element in elements_to_delete:
            self.delete_element(element, update=False)

        # draw edges connecting each node
        node_elems = [element for element in self.elements if element.attribute == "NODE"]
        for idx, elem in enumerate(node_elems):
            if idx == 0:
                continue
            prev_elem = node_elems[idx - 1]
            gv = self.main_window.map_widget.graphics_view
            start = [prev_elem.internal_data["x_p"],
                     prev_elem.internal_data["y_p"]]
            end = [elem.internal_data["x_p"],
                   elem.internal_data["y_p"]]
            edge = gv.draw_edge(start, end)

            data = {
                "start_node_id": prev_elem.data["id"],
                "end_node_id": elem.data["id"],
                "command": 0,
                "skippable": False
            }
            element = Element("EDGE", data, item=edge)
            self.elements.append(element)

    def update_nodes(self):
        node_elems = [element for element in self.elements if element.attribute == "NODE"]

        for idx, elem in enumerate(node_elems):
            elem.data["id"] = idx
            if idx == 0:
                elem.internal_data["angle"] = math.pi/2
                angle = math.degrees(elem.internal_data["angle"])
                elem.item.setRotation(angle)
            else:
                prev_elem = node_elems[idx - 1]
                if prev_elem.data["pose"]["direction"] == "head":
                    prev_elem = node_elems[idx - 1]
                    dx = elem.internal_data["x_p"] - prev_elem.internal_data["x_p"]
                    dy = elem.internal_data["y_p"] - prev_elem.internal_data["y_p"]
                    angle = math.atan2(dy, dx) + math.pi/2
                    prev_elem.internal_data["angle"] = angle
                elif prev_elem.data["pose"]["direction"] == "keep":
                    angle = prev_elem.internal_data["angle"]
                else:
                    print("Error: Invalid direction")
                    angle = prev_elem.internal_data["angle"]

                elem.internal_data["angle"] = angle
                angle = math.degrees(angle)
                prev_elem.item.setRotation(angle)

    def save_elements(self):
        save_data = {
            "OCC_MAP_NAME": self.map_yaml_path,
            "PATH_FRAME": self.sm["path_frame"],
            "MAP_DIRECTION": self.sm["map_direction"]
        }
        for element in self.elements:
            if element.attribute not in save_data:
                save_data[element.attribute] = []
            save_data[element.attribute].append(element.data)

        with open(self.elements_path, 'w') as file:
            yaml.dump(save_data, file, sort_keys=False)
            self.is_saved = True
        print(f"Save elements to {self.elements_path}")

    def check_validation(self, elements_path):
        with open(elements_path, 'r') as file:
            elements = yaml.safe_load(file)

        # check validation
        if "NODE" in elements and len(elements["NODE"]) != 0:
            node_elems = elements["NODE"]
            for node_elem in node_elems:
                if "id" not in node_elem:
                    print("Error: 'id' not in node_elem")
                    return False
                if "pose" not in node_elem:
                    print("Error: 'pose' not in node_elem")
                    return False
                if "type" not in node_elem:
                    print("Error: 'type' not in node_elem")
                if "x" not in node_elem["pose"]:
                    print("Error: 'x' not in node_elem['pose']")
                    return False
                if "y" not in node_elem["pose"]:
                    print("Error: 'y' not in node_elem['pose']")
                    return False
                if "direction" not in node_elem["pose"]:
                    print("Error: 'direction' not in node_elem['pose']")
                    return False

        return True

class Element():
    def __init__(self, attribute, data, internal_data=None, item=None):
        self.attribute = attribute
        self.data = data
        self.internal_data = internal_data
        self.item = item
        self.temp_style_applied = False

    def apply_temp_style(self, pen=None, brush=None):
        if not self.temp_style_applied:
            self.temp_style_applied = True
            self.original_pen = self.item.pen()
            self.original_brush = self.item.brush()

        if pen is not None:
            self.item.setPen(pen)
        if brush is not None:
            self.item.setBrush(brush)

    def apply_original_style(self):
        if self.temp_style_applied:
            self.temp_style_applied = False
            self.item.setPen(self.original_pen)
            self.item.setBrush(self.original_brush)

    @property
    def info_text(self):
        text = ""
        if self.attribute == "NODE":
            text += "Node\n"
            text += f"ID: {self.data['id']}\n"
            text += f"Type: {self.data['type']}\n"
            text += f"X: {self.data['pose']['x']:.2f}\n"
            text += f"Y: {self.data['pose']['y']:.2f}\n"
            text += f"Direction: {self.data['pose']['direction']}"
        elif self.attribute == "EDGE":
            text += "Edge\n"
            text += f"Start node ID: {self.data['start_node_id']}\n"
            text += f"End node ID: {self.data['end_node_id']}\n"
            text += f"Command: {self.data['command']}\n"
            text += f"Skippable: {self.data['skippable']}"

        return text

class settingManager():
    def __init__(self, crt_dir):
        self.crt_dir = crt_dir
        self.settings_file = os.path.join(crt_dir, "settings", "settings.yaml")
        self.stgs = self.load_settings(self.settings_file)

    def save_settings(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w") as file:
            yaml.dump(self.stgs, file)

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
                    'mov_brush': "#FF6464",
                    'hn_brush': '#90EE90',
                    'hn_pen': '#008000',
                    'hn_pen_w': 1,
                    'kn_brush': '#ADD8E6',
                    'kn_pen': '#0000FF',
                    'kn_pen_w': 1,
                    'on_brush': '#D3D3D3',
                    'on_pen': '#808080',
                    'on_pen_w': 1
                },
                'edge': {
                    'pen': '#FFA500'
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
