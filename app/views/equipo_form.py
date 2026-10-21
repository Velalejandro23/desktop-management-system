from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLineEdit,
    QPushButton, QMessageBox, QSpinBox, QComboBox, QDoubleSpinBox, QTextEdit, QHBoxLayout, QLabel,
    QFileDialog # Added QFileDialog
)
from PySide6.QtCore import Qt # Add Qt import for AlignCenter
from app.database.db import get_session
from app.models.equipo import Equipo

class EquipoForm(QDialog):
    def __init__(self, equipo_id=None):
        super().__init__()
        self.equipo_id = equipo_id
        self.setWindowTitle("Gestión de Equipos")
        self.resize(420, 550) # Matching EmpleadoForm size

        self.init_ui()

        if equipo_id:
            self.cargar_datos()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("Gestión de Equipo")
        title_label.setObjectName("titulo") # Reusing existing style
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)

        # Fields
        main_layout.addWidget(QLabel("Nombre *"))
        self.nombre = QLineEdit()
        main_layout.addWidget(self.nombre)

        main_layout.addWidget(QLabel("Tipo *"))
        self.tipo = QLineEdit()
        main_layout.addWidget(self.tipo)

        main_layout.addWidget(QLabel("Cantidad"))
        self.cantidad = QSpinBox()
        self.cantidad.setRange(0, 999999)
        self.cantidad.setGroupSeparatorShown(True)
        main_layout.addWidget(self.cantidad)

        main_layout.addWidget(QLabel("Estado"))
        self.estado = QComboBox()
        self.estado.addItems(["Disponible", "En uso", "En mantenimiento", "De baja"])
        main_layout.addWidget(self.estado)

        main_layout.addWidget(QLabel("Valor Unitario"))
        self.valor_unitario = QDoubleSpinBox()
        self.valor_unitario.setRange(0.0, 9999999999.99) # Increased range for larger numbers
        self.valor_unitario.setDecimals(0)
        self.valor_unitario.setPrefix("$ ")
        self.valor_unitario.setGroupSeparatorShown(True)
        main_layout.addWidget(self.valor_unitario)

        main_layout.addWidget(QLabel("Observaciones"))
        self.observaciones = QTextEdit()
        main_layout.addWidget(self.observaciones)

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
        eq = session.get(Equipo, self.equipo_id)
        if not eq:
            QMessageBox.warning(self, "Error", "Equipo no encontrado.")
            session.close()
            self.reject()
            return

        self.nombre.setText(eq.nombre)
        self.tipo.setText(eq.tipo)
        self.cantidad.setValue(eq.cantidad or 0)
        self.estado.setCurrentText(eq.estado or "Disponible")
        self.valor_unitario.setValue(eq.valor_unitario or 0.0)
        self.observaciones.setPlainText(eq.observaciones or "")
        self.imagen.setText(eq.imagen or "") # Load imagen
        session.close()

    def guardar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return

        if not self.tipo.text().strip():
            QMessageBox.warning(self, "Error", "El tipo es obligatorio.")
            return
        
        session = get_session()

        # Validar equipo duplicado
        existing_equipo = session.query(Equipo).filter_by(nombre=self.nombre.text().strip(), tipo=self.tipo.text().strip()).first()
        if existing_equipo and (not self.equipo_id or existing_equipo.id != self.equipo_id):
            QMessageBox.warning(self, "Error", "Ya existe un equipo con este nombre y tipo.")
            session.close()
            return

        equipo = None
        if self.equipo_id:
            equipo = session.get(Equipo, self.equipo_id)
            if not equipo: # Safeguard, should not happen if cargar_datos works
                QMessageBox.warning(self, "Error", "Equipo no encontrado.")
                session.close()
                self.reject()
                return
        else:
            equipo = Equipo()

        equipo.nombre = self.nombre.text().strip()
        equipo.tipo = self.tipo.text().strip()
        equipo.cantidad = self.cantidad.value()
        equipo.estado = self.estado.currentText()
        equipo.valor_unitario = self.valor_unitario.value()
        equipo.observaciones = self.observaciones.toPlainText()
        equipo.imagen = self.imagen.text() # Save imagen

        session.add(equipo) # Use add for both new and existing equipment
        session.commit()
        session.close()
        self.accept()
