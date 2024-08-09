from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QMessageBox, QToolTip
from PyQt5.QtGui import QPen, QBrush, QColor, QPolygonF
from PyQt5.QtCore import Qt, QEvent, QTimer, QPointF
import math

class MapWidget(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent=parent)
        # class variable initialization
        self.main_window = main_window
        self.map_manager = main_window.map_manager
        setting_manager = main_window.setting_manager
        self.sm = setting_manager.stgs["map_widget"]

        # map graphics view setting
        self.graphics_view = MapGraphicsView(self)

        # map widget setting
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.graphics_view)
        self.setLayout(layout)
        self.setMouseTracking(True)

    def zoom_in(self):
        zoom_factor = self.sm["zoom_factor"]
        self.graphics_view.scale(zoom_factor, zoom_factor)

    def zoom_out(self):
        zoom_factor = self.sm["zoom_factor"]
        self.graphics_view.scale(1/zoom_factor, 1/zoom_factor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Plus:
            self.zoom_in()
        elif event.key() == Qt.Key_Minus:
            self.zoom_out()
        super().keyPressEvent(event)

class MapGraphicsView(QGraphicsView):
    def __init__(self, map_widget):
        super().__init__(parent=map_widget)
        # class variable initialization
        self.map_widget = map_widget
        setting_manager = map_widget.main_window.setting_manager
        self.map_manager = map_widget.main_window.map_manager
        self.sm = setting_manager.stgs["map_graphics_view"]
        self.is_map_set = False
        self.edit_mode = "SELECT"
        self.start_point = None
        self.current_point = None
        self.end_point = None
        self.moving_element = None
        self.is_moving = False

        # graphics scene setting
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # tooltip variables
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(False)
        self.tooltip_timer.timeout.connect(self.show_tooltip)
        self.tooltip_pos = None
        self.tooltip_text = None

        # map graphics view setting
        self.setMouseTracking(True)

  # TODO: Avoid using class variables to store state to prevent `None` errors
    def mousePressEvent(self, event):
        if not self.is_map_set:
            return super().mousePressEvent(event)

        self.start_point = self.mapToScene(event.pos())
        if self.edit_mode == "ADD_NODE":
            self.add_node_event()
        elif self.edit_mode == "DELETE":
            self.delete_event()
        elif self.edit_mode == "MOVE":
            self.move_event(event)
        elif self.edit_mode == "SELECT":
            self.select_event()

        self.update()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.is_map_set:
            return super().mouseMoveEvent(event)

        self.current_point = self.mapToScene(event.pos())
        if self.edit_mode == "MOVE":
            self.move_event(event)
        elif self.edit_mode == "SELECT":
            self.update_tooltip(event)
        self.update()
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if not self.is_map_set:
            return super().mouseReleaseEvent(event)

        self.end_point = self.mapToScene(event.pos())
        if self.edit_mode == "MOVE":
            self.move_event(event)

        self.update()
        return super().mouseReleaseEvent(event)

    def set_map(self, map_pix):
        self.scene.clear()
        self.scene.addPixmap(map_pix)
        self.is_map_set = True

    def add_node_event(self):
        self.map_manager.add_node(self.start_point)

    def delete_event(self):
        element = self.map_manager.get_clicked_element(self.start_point)
        if element is None:
            return
        if element.attribute == "NODE":
            pen = QColor(self.sm["node"]["del_pen"])
            pen = QPen(pen)
            pen.setWidth(self.sm["node"]["del_pen_w"])
            brush = QColor(self.sm["node"]["del_brush"])
            brush = QBrush(brush)
            element.apply_temp_style(pen, brush)

            id = element.data["id"]
            message = f"Do you want to delete node {id}?"
            reply = QMessageBox.question(None, "Delete Node", message, QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.map_manager.delete_element(element)
            else:
                print("Cancel")
                element.apply_original_style()

    def move_event(self, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.is_moving:
                return

            element = self.map_manager.get_clicked_element(self.start_point)
            if element is None:
                return
            elif element.attribute == "NODE":
                pen = QColor(self.sm["node"]["mov_pen"])
                pen = QPen(pen)
                pen.setWidth(self.sm["node"]["mov_pen_w"])
                brush = QColor(self.sm["node"]["mov_brush"])
                brush = QBrush(brush)
                element.apply_temp_style(pen, brush)
                self.moving_element = element

        if event.type() == QEvent.MouseMove:
            if self.moving_element is None:
                return

            self.map_manager.move_element(self.moving_element, self.current_point)

        if event.type() == QEvent.MouseButtonRelease:
            if self.moving_element is None:
                return

            dx = self.end_point.x() - self.start_point.x()
            dy = self.end_point.y() - self.start_point.y()
            distance = math.sqrt(dx**2 + dy**2)
            if not self.is_moving:
                if distance < self.sm["move_mode"]["click_th"]:
                    self.is_moving = True
                    return
            self.map_manager.move_element(self.moving_element, self.end_point, finalize=True)
            self.moving_element.apply_original_style()
            self.is_moving = False
            self.moving_element = None

    def select_event(self):
        element = self.map_manager.get_clicked_element(self.start_point)
        if element is None:
            return
        if element.attribute == "NODE":
            id = element.data["id"]
            self.map_manager.switch_node_direction(element)
            print(f"Select node {id} and switch direction mode")

    def update_tooltip(self, event):
        element = self.map_manager.get_clicked_element(self.current_point)
        if element is not None:
            if not QToolTip.isVisible():
                self.tooltip_pos = event.globalPos()
                self.tooltip_text = element.info_text
                QToolTip.showText(self.tooltip_pos, self.tooltip_text)
                self.tooltip_timer.start(100)
        else:
            self.tooltip_timer.stop()
            QToolTip.hideText()

    def show_tooltip(self):
        if self.tooltip_pos and self.tooltip_text:
            QToolTip.showText(self.tooltip_pos, self.tooltip_text)

    def draw_node(self, x_c, y_c, direction):
        map_manager = self.map_widget.main_window.map_manager
        triangle_base = self.sm["node"]["triangle_base_size"]

        top = (x_c, y_c + triangle_base)
        left = (x_c - triangle_base/2, y_c - triangle_base/2)
        right = (x_c + triangle_base/2, y_c - triangle_base/2)
        top = map_manager.coord2pixel(top)
        left = map_manager.coord2pixel(left)
        right = map_manager.coord2pixel(right)
        polygon = QPolygonF([
            QPointF(top[0], top[1]),
            QPointF(left[0], left[1]),
            QPointF(right[0], right[1])
        ])
        x_p, y_p = map_manager.coord2pixel((x_c, y_c))

        sm_node = self.sm["node"]
        if direction == "head":
            pen = QPen(QColor(sm_node["hn_pen"]))
            pen.setWidth(sm_node["hn_pen_w"])
            brush = QBrush(QColor(sm_node["hn_brush"]))
        elif direction == "keep":
            pen = QPen(QColor(sm_node["kn_pen"]))
            pen.setWidth(sm_node["kn_pen_w"])
            brush = QBrush(QColor(sm_node["kn_brush"]))
        else:
            pen = QPen(QColor(sm_node["on_pen"]))
            pen.setWidth(sm_node["on_pen_w"])
            brush = QBrush(QColor(sm_node["on_brush"]))

        node_item = self.scene.addPolygon(polygon, pen, brush)
        node_item.setTransformOriginPoint(x_p, y_p)

        return node_item

    def draw_edge(self, start, end):
        s_x_p, s_y_p = start
        e_x_p, e_y_p = end
        pen = QPen(QColor(self.sm["edge"]["pen"]))

        edge_item = self.scene.addLine(s_x_p, s_y_p, e_x_p, e_y_p, pen)

        return edge_item


