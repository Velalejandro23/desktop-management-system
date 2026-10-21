from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from app.models.novedad import Novedad # For type hinting
from app.services import novedad_service
from app.database.db import get_session

class DisplayNovedadesReadOnlyDialog(QDialog):
    def __init__(self, module_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Novedades para {module_name}")
        self.module_name = module_name

        # load novedades from DB
        db = get_session()
        try:
            self.novedades = novedad_service.get_active_novedades_by_module(db, module_name)
        finally:
            db.close()

        print(f"[DEBUG] DisplayNovedadesReadOnlyDialog loaded module={module_name} count={len(self.novedades)}")

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        if not self.novedades:
            main_layout.addWidget(QLabel("No hay novedades activas para este módulo."))
        else:
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            
            for novedad in self.novedades:
                novedad_label = QLabel(
                    f"<b>Fecha:</b> {novedad.created_at.strftime('%Y-%m-%d %H:%M')}<br>"
                    f"<b>Mensaje:</b> {novedad.message}<br>"
                    f"<i>Expira: {novedad.expires_at.strftime('%Y-%m-%d')}</i>"
                )
                novedad_label.setWordWrap(True)
                content_layout.addWidget(novedad_label)
                content_layout.addStretch(1) # Add a stretch to push content to top
            
            scroll_area.setWidget(content_widget)
            main_layout.addWidget(scroll_area)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button, alignment=Qt.AlignCenter)
