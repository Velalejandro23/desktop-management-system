from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QHBoxLayout, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from app.database.db import get_session
from app.models.visita import Visita

class VisitaDetalle(QDialog):
    visita_deleted = Signal() # Define the custom signal

    def __init__(self, visita_id, parent=None):
        super().__init__(parent)
        self.visita_id = visita_id
        self.setWindowTitle("Detalles de la Visita")
        self.setMinimumSize(400, 300)
        self.init_ui()
        self.cargar_detalles_visita()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        self.details_layout = QVBoxLayout(content_widget)
        self.details_layout.setAlignment(Qt.AlignTop)

        # Add delete button
        btn_layout = QHBoxLayout()
        btn_eliminar = QPushButton("🗑️ Eliminar Visita")
        btn_eliminar.setStyleSheet("background-color: #e74c3c; color: white;")
        btn_eliminar.clicked.connect(self._eliminar_visita)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_eliminar)
        btn_layout.addStretch() # Center the button
        main_layout.addLayout(btn_layout)


    def cargar_detalles_visita(self):
        session = get_session()
        visita = session.query(Visita).filter_by(id=self.visita_id).first()
        session.close()

        if visita:
            self.add_detail_row("Título:", visita.titulo)
            self.add_detail_row("Descripción:", visita.descripcion)
            self.add_detail_row("Fecha Inicio:", visita.fecha_inicio.strftime("%Y-%m-%d %H:%M"))
            self.add_detail_row("Fecha Fin:", visita.fecha_fin.strftime("%Y-%m-%d %H:%M"))
            self.add_detail_row("Recibe Persona:", visita.recibe_persona)
            self.add_detail_row("Dirección:", visita.direccion)
            self.add_detail_row("Tipo de Visita:", visita.tipo_visita)
            self.add_detail_row("Objetivo:", visita.objetivo)
            self.add_detail_row("Persona que Visita:", visita.persona_hace_visita)
            # self.add_detail_row("Proyecto ID:", str(visita.proyecto_id)) # Uncomment if needed
            self.add_detail_row("Estado:", visita.estado)
        else:
            self.details_layout.addWidget(QLabel("Visita no encontrada."))

    def _eliminar_visita(self):
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            "¿Estás seguro de que deseas eliminar esta visita? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            session = get_session()
            try:
                visita = session.query(Visita).filter_by(id=self.visita_id).first()
                if visita:
                    session.delete(visita)
                    session.commit()
                    QMessageBox.information(self, "Eliminación Exitosa", "La visita ha sido eliminada correctamente.")
                    self.visita_deleted.emit() # Emit signal after successful deletion
                    self.accept() # Close the dialog
                else:
                    QMessageBox.warning(self, "Error", "Visita no encontrada en la base de datos.")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Error", f"Ocurrió un error al eliminar la visita: {e}")
            finally:
                session.close()

    def add_detail_row(self, label_text, value_text):
        row_layout = QHBoxLayout()
        label = QLabel(f"<b>{label_text}</b>")
        value = QLabel(value_text)
        value.setWordWrap(True) # Allow text to wrap for long descriptions/objectives

        row_layout.addWidget(label)
        row_layout.addWidget(value)
        row_layout.addStretch() # Push content to the left
        self.details_layout.addLayout(row_layout)
