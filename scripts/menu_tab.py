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
            # check if user click on menu items or button items
            # then, do not move the window
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
        filemenu_items = [
            {"name": "Open Exiting Map Elements File",
             "shortcut": "Ctrl+O",
             "status_tip": "Open an exiting map elements file",
             "triggered": self.open_exiting_file},
            {"name": "Create New Map Elements File",
             "shortcut": "Ctrl+N",
             "status_tip": "Create a new map elements file",
             "triggered": self.create_new_file},
            {"name": "Overwrite Map Elements File",
             "shortcut": "Ctrl+S",
             "status_tip": "Overwrite the current map elements file",
             "triggered": self.overwrite_file},
            {"name": "Save As Map Elements File",
             "shortcut": "Ctrl+Shift+S",
             "status_tip": "Save the current map elements file as a new file",
             "triggered": self.save_as_file}
        ]
        for item in filemenu_items:
            action = QAction(item["name"], self)
            action.setShortcut(item["shortcut"])
            action.setStatusTip(item["status_tip"])
            action.triggered.connect(item["triggered"])
            self.addAction(action)

    def open_exiting_file(self):
        # check if the current map elements file is saved before discarding map elements in the window
        if not self.map_manager.is_saved:
            message = f"Do you want to save the current map elements file ({self.map_manager.elements_path})?"
            reply = QMessageBox.question(None, "Save Map Elements File", message, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.overwrite_file()
            elif reply == QMessageBox.Cancel:
                return

        # open an existing map elements file
        current_dir = self.main_window.current_dir
        fname = QFileDialog.getOpenFileName(None, "Open Map Elements File", current_dir, "Map Elements Files (*.yaml)")

        # check if the user cancels the file dialog
        if fname[0] == "":
            return

        # update the current directory
        elements_path = fname[0]
        child_dir = os.path.dirname(elements_path)
        parent_dir = os.path.dirname(child_dir)
        self.main_window.current_dir = parent_dir

        # check if the selected file is a valid map elements file
        if self.map_manager.check_validation(elements_path):
            self.map_manager.load_elements(elements_path)
        else:
            return

        # load map
        map_yaml_path = self.map_manager.map_yaml_path
        is_map_loaded = self.map_manager.load_map(map_yaml_path)
        if not is_map_loaded:
            print(f"can't load map file {map_yaml_path}")
            self.open_map()

        # show map and loaded elements
        self.map_manager.show_map()
        self.map_manager.show_loaded_elements()
        print(f"open map elements file {elements_path}")

    def create_new_file(self):
       # check if the current map elements file is saved before discarding map elements in the window
        if not self.map_manager.is_saved:
            message = f"Do you want to save the current map elements file ({self.map_manager.elements_path})?"
            reply = QMessageBox.question(None, "Save Map Elements File", message, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.overwrite_file()
            elif reply == QMessageBox.Cancel:
                return

        # create a new map elements file
        self.map_manager.reset()

        # open and show map
        self.open_map()
        self.map_manager.show_map()

    def open_map(self):
        # open a map file
        current_dir = self.main_window.current_dir
        fname = QFileDialog.getOpenFileName(None, "Open Map", current_dir, "Map Files (*.yaml)")

        # check if the user cancels the file dialog
        if fname[0] == "":
            return

        # update the current directory
        map_yaml_path = fname[0]
        child_dir = os.path.dirname(map_yaml_path)
        parent_dir = os.path.dirname(child_dir)
        self.main_window.current_dir = parent_dir

        # load map
        is_map_loaded = self.map_manager.load_map(map_yaml_path)
        if not is_map_loaded:
            print(f"can't load map file {map_yaml_path}")
            return
        else:
            print(f"load map file {map_yaml_path}")
            self.map_manager.map_yaml_path = map_yaml_path

    def overwrite_file(self):
        # check if the current map elements file is saved before overwriting
        if self.map_manager.elements_path is not None:
            message = f"Do you want to overwrite {self.map_manager.elements_path}?"
            reply = QMessageBox.question(None, "Overwrite Map Elements File", message, QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.map_manager.save_elements()
                print(f"overwrite {self.map_manager.elements_path}")
            else:
                print("Cancel overwrite map elements file")
        else:
            self.save_as_file()

    def save_as_file(self):
        # get the path to save the map elements file
        current_dir = self.main_window.current_dir
        date_str = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        default_fname = "elements-" + date_str + ".yaml"
        default_path = os.path.join(current_dir, default_fname)
        fname, _ = QFileDialog.getSaveFileName(None, "Save As Map Elements File", default_path, "Map Elements Files (*.yaml)")

        # check if fname is valid
        if fname.split(".")[-1] != "yaml":
            elements_path = fname + ".yaml"
        else:
            elements_path = fname

        # update the current directory
        child_dir = os.path.dirname(elements_path)
        parent_dir = os.path.dirname(child_dir)
        self.main_window.current_dir = parent_dir

        # save the map elements file
        self.map_manager.elements_path = elements_path
        self.map_manager.save_elements()
        print(f"save as {elements_path}")

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
