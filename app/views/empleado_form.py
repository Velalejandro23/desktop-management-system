from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QHBoxLayout,
    QComboBox, QFileDialog, QDateEdit, QDoubleSpinBox
)
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import QDate
from app.database.db import get_session
from app.models.empleado import Empleado


class EmpleadoForm(QDialog):
    def __init__(self, empleado_id=None):
        super().__init__()
        self.empleado_id = empleado_id
        self.setWindowTitle("Empleado")
        self.resize(420, 550)

        self.init_ui()

        if empleado_id:
            self.cargar_datos()

    # ---------------- UI ----------------
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        title_label = QLabel("Gestión de Empleados")
        title_label.setObjectName("titulo")
        main_layout.addWidget(title_label)

        nombre_apellidos_layout = QHBoxLayout()
        nombre_apellidos_layout.setSpacing(10)
        
        nombre_label = QLabel("Nombre *")
        self.nombre = QLineEdit()
        
        apellidos_label = QLabel("Apellidos *")
        self.apellidos = QLineEdit()

        nombre_apellidos_layout.addWidget(nombre_label)
        nombre_apellidos_layout.addWidget(self.nombre)
        nombre_apellidos_layout.addWidget(apellidos_label)
        nombre_apellidos_layout.addWidget(self.apellidos)
        main_layout.addLayout(nombre_apellidos_layout)

        main_layout.addWidget(QLabel("Tipo de documento"))
        self.tipo_documento = QComboBox()
        self.tipo_documento.addItems([
            "Cédula de ciudadanía",
            "Tarjeta de identidad",
            "Cédula extranjera",
            "Pasaporte"
        ])
        main_layout.addWidget(self.tipo_documento)
        
        main_layout.addWidget(QLabel("Documento *"))
        self.documento = QLineEdit()
        self.documento.setValidator(QIntValidator())
        main_layout.addWidget(self.documento)

        main_layout.addWidget(QLabel("Teléfono"))
        self.telefono = QLineEdit()
        self.telefono.setPlaceholderText("Ej: 3001234567")
        self.telefono.setValidator(QIntValidator())
        main_layout.addWidget(self.telefono)

        main_layout.addWidget(QLabel("Cargo"))
        self.cargo = QLineEdit()
        main_layout.addWidget(self.cargo)

        main_layout.addWidget(QLabel("Tipo de Contrato"))
        self.tipo_contrato = QComboBox()
        self.tipo_contrato.addItems([
            "Término Fijo",
            "Término Indefinido",
            "Prestación de Servicios",
            "Obra y Labor"
        ])
        main_layout.addWidget(self.tipo_contrato)

        main_layout.addWidget(QLabel("Estado"))
        self.estado = QComboBox()
        self.estado.addItems(["Activo", "Inactivo"])
        main_layout.addWidget(self.estado)

        main_layout.addWidget(QLabel("Fecha de ingreso"))
        self.fecha_ingreso = QDateEdit()
        self.fecha_ingreso.setCalendarPopup(True)
        self.fecha_ingreso.setDate(QDate.currentDate())
        main_layout.addWidget(self.fecha_ingreso)

        main_layout.addWidget(QLabel("Foto"))
        foto_layout = QHBoxLayout()
        self.foto = QLineEdit()
        self.foto.setReadOnly(True)
        btn_foto = QPushButton("Seleccionar foto")
        btn_foto.clicked.connect(self.seleccionar_foto)
        foto_layout.addWidget(self.foto)
        foto_layout.addWidget(btn_foto)
        main_layout.addLayout(foto_layout)

        button_layout = QHBoxLayout()
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.clicked.connect(self.guardar)
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject) # Esto cierra el dialogo

        button_layout.addWidget(btn_guardar)
        button_layout.addWidget(btn_cancelar)
        
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    # ---------------- FUNCIONES ----------------

    def seleccionar_foto(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar foto", "", "Imágenes (*.png *.jpg *.jpeg)"
        )
        if ruta:
            self.foto.setText(ruta)

    def cargar_datos(self):
        session = get_session()
        emp = session.get(Empleado, self.empleado_id)
        if not emp:
            QMessageBox.warning(self, "Error", "Empleado no encontrado.")
            session.close()
            self.reject()
            return

        self.nombre.setText(emp.nombre)
        self.apellidos.setText(emp.apellidos)
        self.tipo_documento.setCurrentText(emp.tipo_documento)
        self.documento.setText(emp.documento)
        self.telefono.setText(emp.telefono or "")
        self.cargo.setText(emp.cargo or "")
        self.tipo_contrato.setCurrentText(emp.tipo_contrato or "")
        self.estado.setCurrentIndex(0 if emp.estado else 1)
        self.fecha_ingreso.setDate(emp.fecha_ingreso)
        self.foto.setText(emp.foto or "")

        session.close()

    def guardar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return

        if not self.apellidos.text().strip():
            QMessageBox.warning(self, "Error", "Los apellidos son obligatorios")
            return

        if not self.documento.text().strip():
            QMessageBox.warning(self, "Error", "El documento es obligatorio")
            return

        session = get_session()

        # Validar documento duplicado
        existing_empleado = session.query(Empleado).filter_by(documento=self.documento.text()).first()
        if existing_empleado and (not self.empleado_id or existing_empleado.id != self.empleado_id):
            QMessageBox.warning(self, "Error", "Ya existe un empleado con este número de documento.")
            session.close()
            return

        if self.empleado_id:
            emp = session.get(Empleado, self.empleado_id)
            if not emp: # Should not happen if cargar_datos works correctly, but as a safeguard
                QMessageBox.warning(self, "Error", "Empleado no encontrado.")
                session.close()
                self.reject()
                return
        else:
            emp = Empleado()

        emp.nombre = self.nombre.text()
        emp.apellidos = self.apellidos.text()
        emp.tipo_documento = self.tipo_documento.currentText()
        emp.documento = self.documento.text()
        emp.telefono = self.telefono.text()
        emp.cargo = self.cargo.text()
        emp.tipo_contrato = self.tipo_contrato.currentText()
        emp.estado = 1 if self.estado.currentIndex() == 0 else 0
        emp.fecha_ingreso = self.fecha_ingreso.date().toPython()
        emp.foto = self.foto.text()

        session.add(emp)
        session.commit()
        session.close()

        self.accept()
