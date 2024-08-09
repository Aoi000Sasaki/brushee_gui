from main_window import MainWindow
from PyQt5.QtWidgets import QApplication
import sys
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)
    crt_dir = os.path.dirname(os.getcwd())
    main_window = MainWindow(crt_dir)

    css_path = os.path.join(crt_dir, "styles", "style.css")
    with open(css_path, "r") as file:
        app.setStyleSheet(file.read())

    main_window.show()

    sys.exit(app.exec_())
