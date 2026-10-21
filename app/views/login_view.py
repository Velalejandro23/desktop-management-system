from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QPixmap,QIcon
from PySide6.QtCore import Qt
from app.utils.paths import resource_path
from app.services.auth_service import autenticar
from app.views.main_view import MainView

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SISMAEP - Login")
        self.setWindowIcon(QIcon(resource_path("assets/logo.png")))
        self.setFixedSize(450, 500)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        # Company Logo
        logo_label = QLabel()
        pixmap = QPixmap(resource_path("assets/logo.png"))
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            print(f"Warning: Logo image '{resource_path('assets/logo.png')}' not found.")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        layout.addSpacing(20)

        # Welcome Message
        titulo = QLabel("Bienvenido a SISMAEP")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Inicia sesión para gestionar tus proyectos")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("font-size: 16px; color: #555;")
        layout.addWidget(subtitulo)
        layout.addSpacing(30)

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        self.usuario_input.setMinimumHeight(35) # Aumentar altura
        self.usuario_input.setStyleSheet("padding-left: 10px;") # Pequeño padding

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35) # Aumentar altura
        self.password_input.setStyleSheet("padding-left: 10px;") # Pequeño padding

        btn_login = QPushButton("Iniciar sesión")
        btn_login.clicked.connect(self.login)
        btn_login.setMinimumHeight(40) # Aumentar altura del botón

        layout.addWidget(self.usuario_input)
        layout.addSpacing(15)
        layout.addWidget(self.password_input)
        layout.addSpacing(30)
        layout.addWidget(btn_login)

        self.setLayout(layout)

    def login(self):
        usuario = self.usuario_input.text()
        password = self.password_input.text()

        if not usuario or not password:
            QMessageBox.warning(self, "Error", "Debe completar todos los campos")
            return

        user = autenticar(usuario, password)

        if user:
            QMessageBox.information(self, "Acceso correcto", f"Bienvenido {user.usuario}")

            # show active novelties in read-only dialog before opening main window
            from app.views.display_novedades_readonly_dialog import DisplayNovedadesReadOnlyDialog

            dialog = DisplayNovedadesReadOnlyDialog(module_name="Main", parent=self)
            dialog.exec()

            self.main = MainView()
            self.main.show()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos")
