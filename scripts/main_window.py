from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from map_widget import MapWidget
from menu_tab import DraggableMenuBar
from editor_toolbar import EditorToolBar
from data_utils import MapManager, settingManager
import os

class MainWindow(QMainWindow):
    def __init__(self, crt_dir):
        super().__init__()
        # class variable initialization
        self.map_manager = MapManager(self)
        self.sm = settingManager(crt_dir)
        self.crt_dir = crt_dir

        # map widget setting
        self.map_widget = MapWidget(self, parent=self)

        # main window setting
        self.setCentralWidget(self.map_widget)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, EditorToolBar(self, parent=self))
        self.setMenuBar(DraggableMenuBar(self, parent=self))

        self.setWindowTitle("Brushee GUI")
        pos_x = self.sm.stgs["window"]["pos_x"]
        pos_y = self.sm.stgs["window"]["pos_y"]
        width = self.sm.stgs["window"]["width"]
        height = self.sm.stgs["window"]["height"]
        self.setGeometry(pos_x, pos_y, width, height)
        self.setWindowFlags(Qt.FramelessWindowHint)
        icon_path = os.path.join(self.crt_dir,
                                 "icon",
                                 "main_window",
                                 "main_icon.png")
        self.setWindowIcon(QIcon(icon_path))

    def toggle_maximize_restore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def closeEvent(self, event):
        self.sm.save_settings()
        event.accept()
