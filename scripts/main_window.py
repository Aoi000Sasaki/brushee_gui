from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys
from map_widget import MapWidget
from map_manager import MapManager
from path_manager import PathManager
from menu_tab import DraggableMenuBar, FileMenu, EditMenu, ViewMenu, HelpMenu
from editor_toolbar import EditorToolBar

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
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Map Viewer")
    self.setGeometry(100, 100, 1200, 800)
    self.current_dir = "/home/user/ws/src/brushee_gui/path/"
    self.map_manager = MapManager(self)
    self.path_manager = PathManager(self)

    central_widget = QWidget(self)
    self.map_widget = MapWidget(self, parent=central_widget)
    layout = QHBoxLayout(central_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(self.map_widget)
    central_widget.setLayout(layout)
    self.setCentralWidget(central_widget)

    self.editor_toolbar = EditorToolBar(self, parent=self)
    self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.editor_toolbar)

    self.setMenuBar(DraggableMenuBar(self, parent=self))

    self.setWindowFlags(Qt.FramelessWindowHint)
    self.setWindowIcon(QIcon("../icon/main_window/main_icon.png"))

    print(f"{self.__class__} : initialized")

  def toggle_maximize_restore(self):
    if self.isMaximized():
      self.showNormal()
    else:
      self.showMaximized()

if __name__ == "__main__":
  app = QApplication(sys.argv)
  with open("../styles/style.css", "r") as file:
    app.setStyleSheet(file.read())
  main_window = MainWindow()
  main_window.show()

  sys.exit(app.exec_())
