from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLineEdit,
    QPushButton, QMessageBox, QDoubleSpinBox, QComboBox, QHBoxLayout, QLabel, QSpinBox,
    QFileDialog # Added QFileDialog
)
from PySide6.QtCore import Qt # Add Qt import for AlignCenter
from app.database.db import get_session
from app.models.material import Material

class MaterialForm(QDialog):
    def __init__(self, material_id=None):
        super().__init__()
        self.material_id = material_id
        self.setWindowTitle("Gestión de Materiales")
        self.resize(420, 550) # Matching EmpleadoForm size

        self.init_ui()

        if material_id:
            self.cargar_datos()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("Gestión de Material")
        title_label.setObjectName("titulo") # Reusing existing style
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)

        # Fields
        main_layout.addWidget(QLabel("Nombre *"))
        self.nombre = QLineEdit()
        main_layout.addWidget(self.nombre)

        main_layout.addWidget(QLabel("Categoría"))
        self.categoria = QLineEdit()
        main_layout.addWidget(self.categoria)

        main_layout.addWidget(QLabel("Unidad"))
        self.unidad = QComboBox()
        self.unidad.addItems(["unidades", "kg", "metros", "litros", "cajas", "paquetes"])
        main_layout.addWidget(self.unidad)

        main_layout.addWidget(QLabel("Cantidad"))
        self.cantidad = QSpinBox()
        self.cantidad.setRange(0, 99999) # Assuming a reasonable range for quantity
        main_layout.addWidget(self.cantidad)

        main_layout.addWidget(QLabel("Marca"))
        self.marca = QLineEdit()
        main_layout.addWidget(self.marca)

        main_layout.addWidget(QLabel("Imagen"))
        imagen_layout = QHBoxLayout()
        self.imagen = QLineEdit()
        self.imagen.setReadOnly(True)
        btn_imagen = QPushButton("Seleccionar Imagen")
        btn_imagen.clicked.connect(self.seleccionar_imagen)
        imagen_layout.addWidget(self.imagen)
        imagen_layout.addWidget(btn_imagen)
        main_layout.addLayout(imagen_layout)

        # Buttons
        button_layout = QHBoxLayout()
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.clicked.connect(self.guardar)
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        button_layout.addWidget(btn_guardar)
        button_layout.addWidget(btn_cancelar)
        
        main_layout.addStretch() # Pushes buttons to the bottom
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def seleccionar_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)"
        )
        if ruta:
            self.imagen.setText(ruta)

    def cargar_datos(self):
        session = get_session()
        mat = session.get(Material, self.material_id)
        if not mat:
            QMessageBox.warning(self, "Error", "Material no encontrado.")
            session.close()
            self.reject()
            return

        self.nombre.setText(mat.nombre)
        self.categoria.setText(mat.categoria or "")
        self.unidad.setCurrentText(mat.unidad or "unidades")
        self.cantidad.setValue(mat.cantidad)
        self.marca.setText(mat.marca or "") # Load marca
        self.imagen.setText(mat.imagen or "") # Load imagen
        session.close()

    def guardar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return
        
        session = get_session()

        # Validar material duplicado
        existing_material = session.query(Material).filter_by(nombre=self.nombre.text().strip()).first()
        if existing_material and (not self.material_id or existing_material.id != self.material_id):
            QMessageBox.warning(self, "Error", "Ya existe un material con este nombre.")
            session.close()
            return

        material = None
        if self.material_id:
            material = session.get(Material, self.material_id)
            if not material: # Safeguard, should not happen if cargar_datos works
                QMessageBox.warning(self, "Error", "Material no encontrado.")
                session.close()
                self.reject()
                return
        else:
            material = Material()

        material.nombre = self.nombre.text().strip()
        material.categoria = self.categoria.text().strip()
        material.unidad = self.unidad.currentText()
        material.cantidad = self.cantidad.value()
        material.marca = self.marca.text().strip() # Save marca
        material.imagen = self.imagen.text() # Save imagen

        session.add(material) # Use add for both new and existing materials
        session.commit()
        session.close()
        self.accept()
