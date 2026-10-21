import sys
import os
from PySide6.QtWidgets import QApplication
from app.views.login_view import LoginView


def resource_path(relative_path):
    """
    Obtiene la ruta correcta tanto en desarrollo como en el ejecutable (.exe)
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def load_stylesheet():
    path = resource_path("ui/styles.qss")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Aplicar el stylesheet global
    stylesheet = load_stylesheet()
    app.setStyleSheet(stylesheet)

    login = LoginView()
    login.show()

    sys.exit(app.exec())
