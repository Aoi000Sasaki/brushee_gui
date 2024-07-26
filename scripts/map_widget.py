from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QMessageBox, QToolTip
from PyQt5.QtGui import QPixmap, QImage, QPolygonF, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QEvent, QTimer
import math

# TODO: load from setting file
zoom_factor = 1.5
triangle_base_size = 0.3 # base size in meter
is_print = False
drag_click_threshold = 10
# TODO: resize triangle size according to grid size

class MapWidget(QWidget):
  def __init__(self, main_window, parent=None):
    super().__init__(parent=parent)
    self.main_window = main_window
    self.path_manager = main_window.path_manager
    self.map_manager = main_window.map_manager

    self.scene = QGraphicsScene()
    self.graphics_view = MapGraphicsView(self)
    self.graphics_view.setScene(self.scene)
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(self.graphics_view)
    self.setLayout(layout)
    self.setMouseTracking(True)
    self.edit_mode = None
    self.is_map_set = False

  def set_map(self, pixmap):
    self.scene.clear()
    self.scene.addPixmap(pixmap)
    self.is_map_set = True

  def draw_triangle(self, polygon, color=Qt.red) -> QPolygonF:
    return self.scene.addPolygon(polygon, QPen(color))

  def zoom_in(self):
    self.graphics_view.scale(zoom_factor, zoom_factor)

  def zoom_out(self):
    self.graphics_view.scale(1/zoom_factor, 1/zoom_factor)

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Plus:
      self.zoom_in()
    elif event.key() == Qt.Key_Minus:
      self.zoom_out()
    else:
      super().keyPressEvent(event)

class MapGraphicsView(QGraphicsView):
  def __init__(self, map_widget):
    super().__init__(map_widget)
    self.map_widget = map_widget
    self.map_manager = map_widget.main_window.map_manager
    self.path_manager = map_widget.main_window.path_manager
    self.setMouseTracking(True)
    self.start_point = None
    self.end_point = None
    self.current_point = None

    self.moving_node = None
    self.is_moving = False

    self.tooltip_timer = QTimer()
    self.tooltip_timer.setSingleShot(False)
    self.tooltip_timer.timeout.connect(self.show_tooltip)
    self.tooltip_pos = None
    self.tooltip_text = None

  # TODO: Avoid using class variables to store state to prevent `None` errors
  def mousePressEvent(self, event):
    self.start_point = self.mapToScene(event.pos())

    if self.map_widget.is_map_set:
      if self.map_widget.edit_mode == "ADD_NODE":
        self.add_node_event()

      elif self.map_widget.edit_mode == "DELETE_NODE":
        self.delete_node_event()

      elif self.map_widget.edit_mode == "MOVE_NODE":
        if not self.is_moving:
          attribute, self.moving_node = self.path_manager.get_clicked_item(self.start_point)
          if attribute == "NODE":
            pen = QPen(QColor(255, 0, 0))
            pen.setWidth(2)
            brush = QBrush(QColor(255, 100, 100))
            self.moving_node.apply_temp_style(pen, brush)

      elif self.map_widget.edit_mode == "SELECT":
        self.select_event()

    self.update()
    return super().mousePressEvent(event)

  def mouseReleaseEvent(self, event):
    self.end_point = self.mapToScene(event.pos())

    if self.map_widget.is_map_set:
      if self.map_widget.edit_mode == "MOVE_NODE":
        self.move_node_event()

    self.update()
    return super().mouseReleaseEvent(event)

  def mouseMoveEvent(self, event):
    self.current_point = self.mapToScene(event.pos())

    if self.map_widget.is_map_set:
      if self.map_widget.edit_mode == "MOVE_NODE":
        if not self.is_moving and self.moving_node:
          attribute = self.moving_node.attribute
          if attribute == "NODE":
            self.path_manager.move_node(self.moving_node, self.current_point)

      elif self.map_widget.edit_mode == "SELECT":
        self.update_tooltip(event)

    self.update()
    return super().mouseMoveEvent(event)

  def add_node_event(self):
    self.path_manager.add_node(self.start_point)

  def delete_node_event(self):
    attribute, node_element = self.path_manager.get_clicked_item(self.start_point)
    if attribute == "NODE":
      pen = QPen(QColor(255, 0, 0))
      pen.setWidth(2)
      brush = QBrush(QColor(255, 100, 100))
      node_element.apply_temp_style(pen, brush)
      id = node_element.data["id"]
      message = f"Do you want to delete node {id}?"
      reply = QMessageBox.question(None, "Delete Node", message, QMessageBox.Yes | QMessageBox.No)
      if reply == QMessageBox.Yes:
        self.path_manager.delete_node(node_element)
        print(f"{self.__class__} : Delete node {id}")
      else:
        print(f"{self.__class__} : Cancel")
        node_element.apply_original_style()

  # TODO: general moving method (node, edge, obstacle?)
  def move_node_event(self):
    if self.is_moving:
      id = self.moving_node.data["id"]
      self.path_manager.move_node(self.moving_node, self.start_point)
      print(f"{self.__class__} : Move node {id} (by clicking)")
      self.moving_node.apply_original_style()
      self.moving_node = None
      self.is_moving = False
      return

    if self.moving_node is None:
      return
    if self.moving_node.attribute != "NODE":
      return

    id = self.moving_node.data["id"]
    dx = self.end_point.x() - self.start_point.x()
    dy = self.end_point.y() - self.start_point.y()
    distance = math.sqrt(dx**2 + dy**2)

    if distance > drag_click_threshold:
      self.path_manager.move_node(self.moving_node, self.end_point)
      print(f"{self.__class__} : Move node {id} (by dragging)")
      self.moving_node.apply_original_style()
      self.moving_node = None
    else:
      self.is_moving = True

  def select_event(self):
    attribute, node_element = self.path_manager.get_clicked_item(self.start_point)
    if attribute == "NODE":
      id = node_element.data["id"]
      self.path_manager.switch_direction_mode(node_element)
      print(f"{self.__class__} : Select node {id} and switch direction mode")

  def update_tooltip(self, event):
    _, item = self.path_manager.get_clicked_item(self.current_point)
    if item is not None:
      if not QToolTip.isVisible():
        self.tooltip_pos = event.globalPos()
        self.tooltip_text = item.info_text
        QToolTip.showText(self.tooltip_pos, self.tooltip_text)
        self.tooltip_timer.start(10)
    else:
      self.tooltip_timer.stop()
      QToolTip.hideText()

  def show_tooltip(self):
    QToolTip.showText(self.tooltip_pos, self.tooltip_text)
