from PyQt5.QtWidgets import QToolBar, QButtonGroup, QToolButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
import os

class EditorToolBar(QToolBar):
    def __init__(self, mainwindow, parent=None):
        super().__init__(parent=parent)
        # class variable initialization
        self.mainwindow = mainwindow
        self.graphics_view = mainwindow.map_widget.graphics_view
        setting_manager = mainwindow.setting_manager
        self.sm = setting_manager.stgs["editor_toolbar"]

        # toolbar button setting
        toolbar_buttons = [
        {"icon": "select.png",
         "status_tip": "Select",
         "tooltip": "Select",
         "callback": self.select},
        {"icon": "add_node.png",
         "status_tip": "Add node",
         "tooltip": "Add node",
         "callback": self.add_node},
        {"icon": "move_node.png",
         "status_tip": "Move node",
         "tooltip": "Move node",
         "callback": self.move_node},
        {"icon": "delete_node.png",
         "status_tip": "Delete node",
         "tooltip": "Delete node",
         "callback": self.delete_node},
        {"icon": "paint_map.png",
         "status_tip": "Paint map",
         "tooltip": "Paint map",
         "callback": self.paint_map},
        {"icon": "erase_map.png",
         "status_tip": "Erase map",
         "tooltip": "Erase map",
         "callback": self.erase_map}
        ]
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        for button in toolbar_buttons:
            button = QToolButton()
            icon_path = os.path.join(os.path.dirname(os.getcwd()),
                                     "icon",
                                     "editor_toolbar",
                                     button["icon"])
            button.setIcon(QIcon(icon_path))
            button.setStatusTip(button["status_tip"])
            button.setToolTip(button["tooltip"])
            button.clicked.connect(button["callback"])
            button.setCheckable(True)
            if button["status_tip"] == "Select":
                button.setChecked(True)
            self.addWidget(button)
            self.button_group.addButton(button)

        # editor toolbar setting
        self.setIconSize(QSize(32, 32))
        self.setMovable(False)

    def select(self):
        self.graphics_view.edit_mode = "SELECT"

    def add_node(self):
        self.graphics_view.edit_mode = "ADD_NODE"

    def move_node(self):
        self.graphics_view.edit_mode = "MOVE_NODE"

    def delete_node(self):
        self.graphics_view.edit_mode = "DELETE_NODE"

    def paint_map(self):
        self.graphics_view.edit_mode = "PAINT_MAP"

    def erase_map(self):
        self.graphics_view.edit_mode = "ERASE_MAP"
