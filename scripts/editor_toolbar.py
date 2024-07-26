from PyQt5.QtWidgets import QToolBar, QButtonGroup, QToolButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class EditorToolBar(QToolBar):
  def __init__(self, mainwindow, parent=None):
    super().__init__(parent=parent)
    self.mainwindow = mainwindow
    self.setIconSize(QSize(32, 32))
    self.setMovable(False)
    self.setFloatable(False)

    toolbar_items = [
      {"icon": "../icon/editor_toolbar/select.png",
       "status_tip": "Select",
       "tooltip": "Select",
       "callback": self.select},
      {"icon": "../icon/editor_toolbar/add_node.png",
       "status_tip": "Add node",
       "tooltip": "Add node",
       "callback": self.add_node},
      {"icon": "../icon/editor_toolbar/move_node.png",
       "status_tip": "Move node",
       "tooltip": "Move node",
       "callback": self.move_node},
      {"icon": "../icon/editor_toolbar/delete_node.png",
       "status_tip": "Delete node",
       "tooltip": "Delete node",
       "callback": self.delete_node},
      {"icon": "../icon/editor_toolbar/paint_map.png",
       "status_tip": "Paint map",
       "tooltip": "Paint map",
       "callback": self.paint_map},
      {"icon": "../icon/editor_toolbar/erase_map.png",
       "status_tip": "Erase map",
       "tooltip": "Erase map",
       "callback": self.erase_map}
    ]

    button_group = QButtonGroup(self)
    button_group.setExclusive(True)

    for item in toolbar_items:
      button = QToolButton()
      button.setIcon(QIcon(item["icon"]))
      button.setStatusTip(item["status_tip"])
      button.setToolTip(item["tooltip"])
      button.clicked.connect(item["callback"])
      button.setCheckable(True)

      if item["status_tip"] == "Select":
        button.setChecked(True)
      self.addWidget(button)
      button_group.addButton(button)

    self.mainwindow.map_widget.edit_mode = "SELECT"

  def select(self):
    print(f"{self.__class__} : Select")
    self.mainwindow.map_widget.edit_mode = "SELECT"

  def add_node(self):
    print(f"{self.__class__} : Add node")
    self.mainwindow.map_widget.edit_mode = "ADD_NODE"

  def move_node(self):
    print(f"{self.__class__} : Move node")
    self.mainwindow.map_widget.edit_mode = "MOVE_NODE"

  def delete_node(self):
    print(f"{self.__class__} : Delete")
    self.mainwindow.map_widget.edit_mode = "DELETE_NODE"

  def paint_map(self):
    print(f"{self.__class__} : Paint map")
    self.mainwindow.map_widget.edit_mode = "PAINT_MAP"

  def erase_map(self):
    print(f"{self.__class__} : Erase map")
    self.mainwindow.map_widget.edit_mode = "ERASE_MAP"
