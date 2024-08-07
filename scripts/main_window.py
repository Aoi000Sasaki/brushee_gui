from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from map_widget import MapWidget
from menu_tab import DraggableMenuBar
from editor_toolbar import EditorToolBar
from data_utils import MapManager, settingManager
import os

# TODO:
# use pub-sub or event throw
# debug message print after finish process
# x_pix -> x_p x_coord -> x_c
# color data write to yaml (setting file)
# use assert
# use os path
# optimize map scaling and origin when initialize
# delete deep if-else using return
# show item info when hover
# show id beside item
# separate initialize ui and class variable

class MainWindow(QMainWindow):
    def __init__(self, crt_dir):
        super().__init__()
        # class variable initialization
        self.map_manager = MapManager(self)
        setting_manager = settingManager(crt_dir)
        self.sm = setting_manager.stgs["main_window"]
        self.crt_dir = crt_dir

        # map widget setting
        self.map_widget = MapWidget(self, parent=self)

        # main window setting
        self.setCentralWidget(self.map_widget)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, EditorToolBar(self, parent=self))
        self.setMenuBar(DraggableMenuBar(self, parent=self))

        self.setWindowTitle("Brushee GUI")
        pos_x = self.sm.stgs["pos_x"]
        pos_y = self.sm.stgs["pos_y"]
        width = self.sm.stgs["width"]
        height = self.sm.stgs["height"]
        self.setGeometry(pos_x, pos_y, width, height)
        self.setWindowFlags(Qt.FramelessWindowHint)
        icon_path = os.path.join(os.path.dirname(os.getcwd()),
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
