from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMessageBox, QMenuBar, QWidget, QSizePolicy, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import os
import datetime

class DraggableMenuBar(QMenuBar):
    def __init__(self, main_window, parent=None):
        super().__init__(parent=parent)
        # class variable initialization
        self.main_window = main_window
        self.old_pos = None

        # main icon setting (top left corner)
        main_icon_label = QPushButton()
        main_icon_path = os.path.join(os.path.dirname(os.getcwd()),
                                      "icon",
                                      "main_window",
                                      "main_icon.png")
        main_icon_label.setIcon(QIcon(main_icon_path))
        main_icon_label.setIconSize(QSize(20, 20))
        main_icon_label.setFlat(True)
        main_icon_label.setStyleSheet("border: none;")
        self.setCornerWidget(main_icon_label, Qt.TopLeftCorner)

        # button setting (top right corner)
        self.button_items = [
            {"icon": "minimize.png",
             "callback": self.main_window.showMinimized},
            {"icon": "maximize.png",
             "callback": self.main_window.toggle_maximize_restore},
            {"icon": "close.png",
             "callback": self.main_window.close}
        ]
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        for item in self.button_items:
            button = QPushButton()
            icon_path = os.path.join(os.path.dirname(os.getcwd()),
                                     "icon",
                                     "main_window",
                                     item["icon"])
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(24, 24))
            button.setFlat(True)
            button.clicked.connect(item["callback"])
            button_layout.addWidget(button)
            item = button
        button_widget = QWidget(self.main_window)
        button_widget.setLayout(button_layout)
        self.setCornerWidget(button_widget, Qt.TopRightCorner)

        # menu bar setting
        self.menu_items = [
            FileMenu(self.main_window, parent=self),
            EditMenu(self.main_window, parent=self),
            ViewMenu(self.main_window, parent=self),
            HelpMenu(self.main_window, parent=self)
        ]
        for item in self.menu_items:
            self.addMenu(item)

    # spacer = QWidget(self)
    # spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    # self.setCornerWidget(spacer, Qt.TopRightCorner)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for item in self.menu_items:
                if item.rect().contains(event.pos()):
                    self.old_pos = None
                    return super().mousePressEvent(event)
            for item in self.button_items:
                if item.rect().contains(event.pos()):
                    self.old_pos = None
                    return super().mousePressEvent(event)
            self.old_pos = event.globalPos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.old_pos is not None:
            delta = event.globalPos() - self.old_pos
            parent = self.parentWidget()
            parent.move(parent.x() + delta.x(), parent.y() + delta.y())
            self.old_pos = event.globalPos()
            event.accept()
        super().mouseMoveEvent(event)

# TODO: not crash when cansel
class FileMenu(QMenu):
    def __init__(self, main_window, parent=None):
        super().__init__("&File", parent=parent)
        # class variable initialization
        self.main_window = main_window
        self.map_manager = main_window.map_manager

        # file menu setting
        # TODO: the word "overlay" ... good ??
        filemenu_items = [
            {"name": "Open Exiting Overlay File",
             "shortcut": "Ctrl+O",
             "status_tip": "Open an overlay file",
             "triggered": self.open_exiting_file},
            {"name": "Create New Overlay File",
             "shortcut": "Ctrl+N",
             "status_tip": "Create a new overlay file",
             "triggered": self.create_new_file},
            {"name": "Overwrite Overlay File",
             "shortcut": "Ctrl+S",
             "status_tip": "Overwrite the current overlay file",
             "triggered": self.overwrite_file},
            {"name": "Save As Overlay File",
             "shortcut": "Ctrl+Shift+S",
             "status_tip": "Save the current overlay file as a new file",
             "triggered": self.save_as_file}
        ]
        for item in filemenu_items:
            action = QAction(item["name"], self)
            action.setShortcut(item["shortcut"])
            action.setStatusTip(item["status_tip"])
            action.triggered.connect(item["triggered"])
            self.addAction(action)

    def open_exiting_file(self):
        if not self.map_manager.is_saved:
            message = f"Do you want

  def open_exiting_path(self):
    print(f"{self.__class__} : Open exiting path")

    if not self.path_manager.is_saved:
      print(f"{self.__class__} : Path is not saved")
      message = f"Do you want to save the current path ({self.path_manager.pathfile_path})?"
      reply = QMessageBox.question(None, "Save Path", message, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
      if reply == QMessageBox.Yes:
        self.overwrite_path()
      elif reply == QMessageBox.Cancel:
        print(f"{self.__class__} : Cancel")
        return

    current_dir = self.main_window.current_dir
    fname = QFileDialog.getOpenFileName(None, "Open Path", current_dir, "Path Files (*.yaml)")
    pathfile_path = fname[0]
    child_dir = os.path.dirname(pathfile_path)
    parent_dir = os.path.dirname(child_dir)
    self.main_window.current_dir = parent_dir

    if self.path_manager.check_validation(pathfile_path):
      print(f"{self.__class__} : {pathfile_path} is valid path file")
      self.path_manager.load_pathfile(pathfile_path)
    else:
      print(f"{self.__class__} : {pathfile_path} is invalid path file, Does not load path file")
      return

    map_yamlfile_path = self.path_manager.map_yamlfile_path
    is_map_load = self.map_manager.load_map_yamlfile(map_yamlfile_path)

    if not is_map_load:
      print(f"{self.__class__} : can't load map file {map_yamlfile_path}")
      self.open_map()

    self.map_manager.show_map()
    self.path_manager.show_loaded_path()

  def create_new_path(self):
    print(f"{self.__class__} : Create new path")

    if not self.path_manager.is_saved:
      print(f"{self.__class__} : Path is not saved")
      message = f"Do you want to save the current path ({self.path_manager.pathfile_path})?"
      reply = QMessageBox.question(None, "Save Path", message, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
      if reply == QMessageBox.Yes:
        self.overwrite_path()
      elif reply == QMessageBox.Cancel:
        print(f"{self.__class__} : Cancel")
        return

    self.path_manager.reset()
    self.open_map()
    self.map_manager.show_map()

  def open_map(self):
    print(f"{self.__class__} : Open map")

    current_dir = self.main_window.current_dir
    fname = QFileDialog.getOpenFileName(None, "Open Map", current_dir, "Map Files (*.yaml)")
    yamlfile_path = fname[0]
    child_dir = os.path.dirname(yamlfile_path)
    parent_dir = os.path.dirname(child_dir)
    self.main_window.current_dir = parent_dir

    self.map_manager.load_map_yamlfile(yamlfile_path)
    self.path_manager.map_yamlfile_path = yamlfile_path
    print(f"{self.__class__} : Load map file {yamlfile_path}")

  def overwrite_path(self):
    print(f"{self.__class__} : Overwrite path")

    if self.path_manager.pathfile_path is not None:
      print(f"{self.__class__} : Overwrite path")
      message = f"Do you want to overwrite {self.path_manager.pathfile_path}?"
      reply = QMessageBox.question(None, "Overwrite Path", message, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
      if reply == QMessageBox.Yes:
        self.path_manager.save_pathfile()
        print(f"{self.__class__} : Overwrite {self.path_manager.pathfile_path}")
      else:
        print(f"{self.__class__} : Cancel overwrite path")

    else:
      self.save_as_path()

  def save_as_path(self):
    print(f"{self.__class__} : Save as path")

    current_dir = self.main_window.current_dir
    date_str = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    default_fname = "path-" + date_str + ".yaml"
    default_path = os.path.join(current_dir, default_fname)
    fname, _ = QFileDialog.getSaveFileName(None, "Save As Path", default_path, "Path Files (*.yaml)")
    if ".yaml" not in fname:
      pathfile_path = fname + ".yaml"
    else:
      pathfile_path = fname
    child_dir = os.path.dirname(pathfile_path)
    parent_dir = os.path.dirname(child_dir)
    self.main_window.current_dir = parent_dir

    self.path_manager.pathfile_path = pathfile_path
    self.path_manager.save_pathfile()
    print(f"{self.__class__} : Save as {pathfile_path}")

class EditMenu(QMenu):
  def __init__(self, main_window, parent=None):
    super().__init__("&Edit", parent=parent)
    self.main_window = main_window

class ViewMenu(QMenu):
  def __init__(self, main_window, parent=None):
    super().__init__("&View", parent=parent)
    self.main_window = main_window

class HelpMenu(QMenu):
  def __init__(self, main_window, parent=None):
    super().__init__("&Help", parent=parent)
    self.main_window = main_window
