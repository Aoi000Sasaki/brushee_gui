from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from map_widget import MapWidget
from menu_tab import DraggableMenuBar
from editor_toolbar import EditorToolBar
from data_utils import MapManager, settingManager
import os

# TODO:
# x_pix -> x_p x_coord -> x_c
# optimize map scaling and origin when initialize
# show id beside item
# separate initialize ui and class variable
# raise exception
# warn or not
# タブの見出し語を簡潔に（日本語化）

class MainWindow(QMainWindow):
    def __init__(self, crt_dir):
        super().__init__()
        # class variable initialization
        self.setting_manager = settingManager(crt_dir)
        self.map_manager = MapManager(self)
        self.sm = self.setting_manager.stgs["main_window"]
        self.crt_dir = crt_dir

        # map widget setting
        self.map_widget = MapWidget(self, parent=self)

        # main window setting
        self.setCentralWidget(self.map_widget)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, EditorToolBar(self, parent=self))
        self.setMenuBar(DraggableMenuBar(self, parent=self))

        self.setWindowTitle("Brushee GUI")
        pos_x = self.sm["pos_x"]
        pos_y = self.sm["pos_y"]
        width = self.sm["width"]
        height = self.sm["height"]
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
        self.setting_manager.save_settings()
        event.accept()
