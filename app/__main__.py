import sys
from PySide6.QtWidgets import QApplication
from app.views.login_view import LoginView

def main():
    app = QApplication(sys.argv)
    login = LoginView()
    login.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
