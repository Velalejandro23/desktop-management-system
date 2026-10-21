from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QSpinBox, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from app.database.db import get_session
from app.services import novedad_service

class AddNovedadDialog(QDialog):
    def __init__(self, module_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Agregar Novedad para {module_name}")
        self.module_name = module_name
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Message input
        message_label = QLabel("Mensaje de la Novedad:")
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Ingrese la novedad aquí...")
        main_layout.addWidget(message_label)
        main_layout.addWidget(self.message_input)

        # Days to expire input
        days_layout = QHBoxLayout()
        days_label = QLabel("Días para expirar:")
        self.days_spinbox = QSpinBox()
        self.days_spinbox.setMinimum(1)
        self.days_spinbox.setMaximum(30) # Max 30 days for now
        self.days_spinbox.setValue(5)
        days_layout.addWidget(days_label)
        days_layout.addWidget(self.days_spinbox)
        days_layout.addStretch()
        main_layout.addLayout(days_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_novedad)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

    def save_novedad(self):
        message = self.message_input.toPlainText().strip()
        days_to_expire = self.days_spinbox.value()

        if not message:
            QMessageBox.warning(self, "Advertencia", "El mensaje de la novedad no puede estar vacío.")
            return

        db = get_session() # Get a database session
        try:
            # Store novedades as global system entries
            novedad_service.create_novedad(
                db=db,
                module_name="System",
                message=message,
                days_to_expire=days_to_expire
            )
            QMessageBox.information(self, "Éxito", "Novedad guardada correctamente.")
            self.accept() # Close dialog with accept result
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar la novedad: {e}")
        finally:
            db.close() # Close the session
