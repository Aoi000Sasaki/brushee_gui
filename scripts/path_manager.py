from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPolygonF, QPen, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsLineItem
from PyQt5.QtCore import Qt
import math
import yaml

triangle_base = 0.3

class PathManager:
  def __init__(self, main_window):
    self.main_window = main_window
    self.path_elements = []
    self.pathfile_path = None
    self.is_saved = True

  def reset(self):
    self.path_elements = []
    self.data_loded = None
    self.pathfile_path = None
    self.is_saved = True

  def load_pathfile(self, pathfile_path):
    self.reset()
    self.pathfile_path = pathfile_path
    with open(self.pathfile_path, "r") as file:
      self.data_loded = yaml.safe_load(file)
    self.map_yamlfile_path = self.data_loded["OCC_MAP_NAME"]

    # TODO: add edge and other data handling

  def show_loaded_path(self):
    if self.data_loded is None:
      print(f"{self.__class__} : No path data loaded")
      return
    else:
      print(f"{self.__class__} : Show loaded path data")
      for node in self.data_loded["NODE"]:
        self.draw_node(node)

  def draw_node(self, node):
    map_widget = self.main_window.map_widget
    map_manager = self.main_window.map_manager
    x = node["pose"]["x"]
    y = node["pose"]["y"]
    x_pix, y_pix = map_manager.coord2pixel((x, y))

    top = (x, y + triangle_base)
    left = (x - triangle_base/2, y - triangle_base/2)
    right = (x + triangle_base/2, y - triangle_base/2)
    top = map_manager.coord2pixel(top)
    left = map_manager.coord2pixel(left)
    right = map_manager.coord2pixel(right)
    polygon = QPolygonF([
      QPointF(top[0], top[1]),
      QPointF(right[0], right[1]),
      QPointF(left[0], left[1])
    ])

    # TODO: review colorize method (consider direction resetting)
    if node["pose"]["direction"] == "head":
      pen = QPen(QColor(0, 128, 0))
      brush = QBrush(QColor(144, 238, 144))
    elif node["pose"]["direction"] == "keep":
      pen = QPen(QColor(0, 0, 255))
      brush = QBrush(QColor(173, 216, 230))
    else:
      pen = QPen(QColor(128, 128, 128))
      brush = QBrush(QColor(211, 211, 211))


    triangle_item = map_widget.scene.addPolygon(polygon, pen, brush)
    triangle_item.setTransformOriginPoint(x_pix, y_pix)

    internal_data = {
      "x_pix": x_pix,
      "y_pix": y_pix,
      "angle": 0
    }
    path_element = PathElement("NODE", node,
                               internal_data=internal_data,
                               item=triangle_item)

    self.path_elements.append(path_element)
    self.update_node_directions()

  # NOTE: set is_saved to False in this method (this method is called by every node operation)
  def update_node_directions(self):
    is_first = True
    latt_node_elem = None
    crt_node_elem = None

    for element in self.path_elements:
      if element.attribute == "NODE":
        crt_node_elem = element
      if is_first:
        crt_node_elem.internal_data["angle"] = math.pi/2
        angle = math.degrees(crt_node_elem.internal_data["angle"])
        crt_node_elem.item.setRotation(angle)
        is_first = False
      else:
        if latt_node_elem.data["pose"]["direction"] == "head":
          dx = crt_node_elem.internal_data["x_pix"] - latt_node_elem.internal_data["x_pix"]
          dy = crt_node_elem.internal_data["y_pix"] - latt_node_elem.internal_data["y_pix"]
          angle = math.atan2(dy, dx) + math.pi/2
          latt_node_elem.internal_data["angle"] = angle
        elif latt_node_elem.data["pose"]["direction"] == "keep":
          angle = latt_node_elem.internal_data["angle"]
        else:
          print(f"{self.__class__} : Unknown direction")
          angle = latt_node_elem.internal_data["angle"]

        crt_node_elem.internal_data["angle"] = angle
        angle = math.degrees(angle)
        latt_node_elem.item.setRotation(angle)

      latt_node_elem = crt_node_elem
      self.is_saved = False


    # NOTE: for mtg visualize code is poor
    node_elems = [element for element in self.path_elements if element.attribute == "NODE"]
    is_node_elem_first = True
    latest_node_elem = None
    for element in self.path_elements:
      if element.attribute == "EDGE_TEST":
        self.main_window.map_widget.scene.removeItem(element.item)
        self.path_elements.remove(element)
    for ne in node_elems:
      if is_node_elem_first:
        is_node_elem_first = False
        latest_node_elem = ne
        continue
      s_x = latest_node_elem.internal_data["x_pix"]
      s_y = latest_node_elem.internal_data["y_pix"]
      e_x = ne.internal_data["x_pix"]
      e_y = ne.internal_data["y_pix"]
      line_item = QGraphicsLineItem(s_x, s_y, e_x, e_y)
      pen = QPen(QColor(255, 165, 0))
      line_item.setPen(pen)
      data = {
        "id": -1,
        "type": -1,
        "pose": {
          "x": -1,
          "y": -1,
          "direction": "head"
        }
      }
      edge_element = PathElement("EDGE_TEST", data, item=line_item)
      self.main_window.map_widget.scene.addItem(line_item)
      self.path_elements.append(edge_element)
      latest_node_elem = ne
    # NOTE: poor code end


  def add_node(self, point):
    map_manager = self.main_window.map_manager
    x, y = map_manager.pixel2coord((point.x(), point.y()))
    node_n = len(self.path_elements)
    ids = [self.path_elements[i].data["id"] for i in range(node_n)]
    while True:
      if not node_n in ids:
        break
      node_n += 1

    node = {
      "id": node_n,
      "pose": {
        "x": x,
        "y": y,
        "direction": "head"
      },
      "type": 1
    }
    self.draw_node(node)

  def delete_node(self, node_element):
    if not node_element in self.path_elements:
      print(f"{self.__class__} : {node_element} not found")
      return
    self.main_window.map_widget.scene.removeItem(node_element.item)
    self.path_elements.remove(node_element)
    self.update_node_directions()

  def move_node(self, node_element, distination):
    map_manager = self.main_window.map_manager
    dx = distination.x() - node_element.internal_data["x_pix"]
    dy = distination.y() - node_element.internal_data["y_pix"]

    node_element.item.moveBy(dx, dy)
    node_element.internal_data["x_pix"] = distination.x()
    node_element.internal_data["y_pix"] = distination.y()
    x, y = map_manager.pixel2coord((distination.x(), distination.y()))
    node_element.data["pose"]["x"] = x
    node_element.data["pose"]["y"] = y

    self.update_node_directions()

  def switch_direction_mode(self, node_element):
    if node_element.data["pose"]["direction"] == "head":
      node_element.data["pose"]["direction"] = "keep"
      pen = QPen(QColor(0, 0, 255))
      brush = QBrush(QColor(173, 216, 230))
      node_element.item.setPen(pen)
      node_element.item.setBrush(brush)
    elif node_element.data["pose"]["direction"] == "keep":
      node_element.data["pose"]["direction"] = "head"
      pen = QPen(QColor(0, 128, 0))
      brush = QBrush(QColor(144, 238, 144))
      node_element.item.setPen(pen)
      node_element.item.setBrush(brush)
    else:
      print(f"{self.__class__} : Unknown direction")

    self.update_node_directions()

  # TODO: do not need attribute
  def get_clicked_item(self, point):
    for element in self.path_elements:
      if element.item.contains(point):
        return element.attribute, element

    return None, None

  def save_pathfile(self):
    pathfile_data = {
      "OCC_MAP_NAME": self.map_yamlfile_path
    }
    for element in self.path_elements:
      if element.attribute not in pathfile_data:
        pathfile_data[element.attribute] = []
      pathfile_data[element.attribute].append(element.data)

    with open(self.pathfile_path, "w") as file:
      yaml.dump(pathfile_data, file)
      self.is_saved = True

  # TODO: add check pattern if needed
  def check_validation(self, yamlfile_path):
    with open(yamlfile_path, "r") as file:
      path_data = yaml.load(file, Loader=yaml.FullLoader)
    if "OCC_MAP_NAME" not in path_data:
      print(f"{self.__class__} : OCC_MAP_NAME not found")
      return False
    if "NODE" not in path_data:
      print(f"{self.__class__} : NODE not found")
      return False

    node_data = path_data["NODE"]
    if len(node_data) == 0:
      return True
    for node in node_data:
      if "id" not in node:
        print(f"{self.__class__} : id not found")
        return False
      if "type" not in node:
        print(f"{self.__class__} : type not found")
        return False
      if "pose" not in node:
        print(f"{self.__class__} : pose not found")
        return False
      if "x" not in node["pose"]:
        print(f"{self.__class__} : x not found")
        return False
      if "y" not in node["pose"]:
        print(f"{self.__class__} : y not found")
        return False
      if "direction" not in node["pose"]:
        print(f"{self.__class__} : direction not found")
        return False

    return True

class PathElement:
  def __init__(self, attribute, data, internal_data=None, item=None):
    self.attribute = attribute
    self.data = data
    self.internal_data = internal_data
    self.item = item

    self.style_applied = False

  def apply_temp_style(self, pen=None, brush=None):
    if not self.style_applied:
      self.style_applied = True
      self.original_pen = self.item.pen()
      self.original_brush = self.item.brush()
    if pen is not None:
      self.item.setPen(pen)
    if brush is not None:
      self.item.setBrush(brush)

  def apply_original_style(self):
    if self.style_applied :
      self.style_applied = False
      self.item.setPen(self.original_pen)
      self.item.setBrush(self.original_brush)

  # TODO: not node specific
  @property
  def info_text(self):
    text = (
    f"ID: {self.data['id']}\n"
    f"Type: {self.data['type']}\n"
    f"X: {self.data['pose']['x']:.2f}\n"
    f"Y: {self.data['pose']['y']:.2f}\n"
    f"Direction: {self.data['pose']['direction']}"
    )

    return text
