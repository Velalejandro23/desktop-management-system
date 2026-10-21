from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QScrollArea, QWidget, QFrame
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize
from app.database.db import get_session
from app.models.equipo import Equipo
from app.models.proyecto_equipo import ProyectoEquipo # Import to query relationships
from app.models.proyecto import Proyecto # Import to get project name
from app.utils.formatting import format_cop
import os # For checking if image file exists

class EquipoDetalle(QDialog):
    def __init__(self, equipo_id):
        super().__init__()
        self.equipo_id = equipo_id
        self.setWindowTitle("Detalle del Equipo")
        self.resize(500, 650) # Slightly larger to accommodate more details

        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Title
        title_label = QLabel("Detalle de Equipo")
        title_label.setObjectName("titulo")
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        self.form_layout = QVBoxLayout(scroll_content_widget)
        self.form_layout.setSpacing(8)

        # Equipo Image
        self.imagen_label = QLabel("No Image")
        self.imagen_label.setAlignment(Qt.AlignCenter)
        self.imagen_label.setFixedSize(200, 200) # Fixed size for image display
        self.imagen_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.form_layout.addWidget(self.imagen_label)
        self.form_layout.addSpacing(10)

        # Fields
        self.add_detail_field("Nombre:", "nombre")
        self.add_detail_field("Tipo:", "tipo")
        self.add_detail_field("Cantidad Total:", "cantidad")
        self.add_detail_field("Estado General:", "estado")
        self.add_detail_field("Valor Unitario:", "valor_unitario")
        self.add_detail_field("Observaciones:", "observaciones")
        
        # Separator for projects in use
        self.form_layout.addWidget(self._create_separator("Proyectos en Uso"))
        self.proyectos_en_uso_layout = QVBoxLayout()
        self.form_layout.addLayout(self.proyectos_en_uso_layout)


        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)

        # Close Button
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)

    def add_detail_field(self, label_text, attribute_name):
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(120) # Align labels, slightly wider for equipo details
        value_label = QLabel()
        value_label.setObjectName(f"value_{attribute_name}") # For setting text later
        h_layout.addWidget(label)
        h_layout.addWidget(value_label)
        h_layout.addStretch()
        self.form_layout.addLayout(h_layout)
        setattr(self, f"_{attribute_name}_value_label", value_label) # Store reference

    def _create_separator(self, text):
        frame = QFrame()
        frame.setFrameShape(QFrame.HLine)
        frame.setFrameShadow(QFrame.Sunken)
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        layout.addWidget(label)
        layout.addWidget(frame)
        container = QWidget()
        container.setLayout(layout)
        return container

    def cargar_datos(self):
        session = get_session()
        equipo = session.get(Equipo, self.equipo_id)
        if not equipo:
            QMessageBox.warning(self, "Error", "Equipo no encontrado.")
            session.close()
            self.reject()
            return

        # Set text for fields
        self._nombre_value_label.setText(equipo.nombre.title())
        self._tipo_value_label.setText((equipo.tipo or "N/A").title())
        self._cantidad_value_label.setText(str(equipo.cantidad))
        self._estado_value_label.setText(equipo.estado or "N/A")
        self._valor_unitario_value_label.setText(f"$ {format_cop(equipo.valor_unitario)}")
        self._observaciones_value_label.setText(equipo.observaciones or "Ninguna")

        # Load image
        if equipo.imagen and os.path.exists(equipo.imagen):
            pixmap = QPixmap(equipo.imagen)
            if not pixmap.isNull():
                self.imagen_label.setPixmap(pixmap.scaled(
                    self.imagen_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                self.imagen_label.setText("Error al cargar imagen")
        else:
            self.imagen_label.setText("No hay imagen disponible")

        # Handle "Proyectos en Uso"
        proyectos_asignados_en_uso = session.query(ProyectoEquipo).filter(
            ProyectoEquipo.equipo_id == self.equipo_id
        ).all()

        if proyectos_asignados_en_uso:
            for pe in proyectos_asignados_en_uso:
                proyecto = session.get(Proyecto, pe.proyecto_id)
                if proyecto:
                    self.proyectos_en_uso_layout.addWidget(QLabel(
                        f"- {proyecto.nombre} (Cantidad: {pe.cantidad})"
                    ))
        else:
            self.proyectos_en_uso_layout.addWidget(QLabel("Este equipo no está asignado a ningún proyecto actualmente."))

        session.close()
