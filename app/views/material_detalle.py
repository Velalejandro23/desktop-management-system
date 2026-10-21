from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QScrollArea,QWidget
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize
from app.database.db import get_session
from app.models.material import Material
import os # For checking if image file exists

class MaterialDetalle(QDialog):
    def __init__(self, material_id):
        super().__init__()
        self.material_id = material_id
        self.setWindowTitle("Detalle del Material")
        self.resize(500, 600)

        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Title
        title_label = QLabel("Detalle de Material")
        title_label.setObjectName("titulo")
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        self.form_layout = QVBoxLayout(scroll_content_widget)
        self.form_layout.setSpacing(8)

        # Material Image
        self.imagen_label = QLabel("No Image")
        self.imagen_label.setAlignment(Qt.AlignCenter)
        self.imagen_label.setFixedSize(200, 200) # Fixed size for image display
        self.imagen_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.form_layout.addWidget(self.imagen_label)
        self.form_layout.addSpacing(10)

        # Fields
        self.add_detail_field("Nombre:", "nombre")
        self.add_detail_field("Categoría:", "categoria")
        self.add_detail_field("Marca:", "marca")
        self.add_detail_field("Unidad:", "unidad")
        self.add_detail_field("Cantidad:", "cantidad")

        scroll_area.setWidget(scroll_content_widget)
        main_layout.addWidget(scroll_area)

        # Close Button
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)

    def add_detail_field(self, label_text, attribute_name):
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(100) # Align labels
        value_label = QLabel()
        value_label.setObjectName(f"value_{attribute_name}") # For setting text later
        h_layout.addWidget(label)
        h_layout.addWidget(value_label)
        h_layout.addStretch()
        self.form_layout.addLayout(h_layout)
        setattr(self, f"_{attribute_name}_value_label", value_label) # Store reference

    def cargar_datos(self):
        session = get_session()
        material = session.get(Material, self.material_id)
        if not material:
            QMessageBox.warning(self, "Error", "Material no encontrado.")
            session.close()
            self.reject()
            return

        # Set text for fields
        self._nombre_value_label.setText(material.nombre.title())
        self._categoria_value_label.setText((material.categoria or "").title())
        self._marca_value_label.setText((material.marca or "N/A").title())
        self._unidad_value_label.setText(material.unidad or "N/A")
        self._cantidad_value_label.setText(str(material.cantidad))

        # Load image
        if material.imagen and os.path.exists(material.imagen):
            pixmap = QPixmap(material.imagen)
            if not pixmap.isNull():
                self.imagen_label.setPixmap(pixmap.scaled(
                    self.imagen_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                self.imagen_label.setText("Error al cargar imagen")
        else:
            self.imagen_label.setText("No hay imagen disponible")

        session.close()
