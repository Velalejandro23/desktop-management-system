from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QFrame
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from app.database.db import get_session
from app.models.empleado import Empleado


class EmpleadoDetalle(QDialog):
    def __init__(self, empleado_id):
        super().__init__()
        self.setWindowTitle("Ficha del Empleado")
        self.setFixedSize(520, 300)

        session = get_session()
        emp = session.get(Empleado, empleado_id)

        # ---------------- CONTENEDOR PRINCIPAL ----------------
        contenedor = QFrame()
        contenedor.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #dcdcdc;
            }
        """)

        layout_principal = QHBoxLayout(contenedor)
        layout_principal.setContentsMargins(15, 15, 15, 15)
        layout_principal.setSpacing(15)

        # ---------------- FOTO ----------------
        self.lbl_foto = QLabel()
        self.lbl_foto.setFixedSize(130, 160)
        self.lbl_foto.setAlignment(Qt.AlignCenter)
        self.lbl_foto.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #f4f4f4;
            }
        """)

        if emp.foto:
            pix = QPixmap(emp.foto)
            self.lbl_foto.setPixmap(
                pix.scaled(130, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self.lbl_foto.setText("Sin\nfoto")

        # ---------------- DATOS ----------------
        datos_layout = QVBoxLayout()
        datos_layout.setSpacing(6)

        titulo = QLabel("DATOS DEL EMPLEADO")
        titulo.setFont(QFont("Arial", 12, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)

        datos_layout.addWidget(titulo)

        def campo(nombre, valor):
            lbl = QLabel(f"<b>{nombre}:</b> {valor}")
            lbl.setStyleSheet("font-size: 13px;")
            return lbl

        datos_layout.addWidget(campo("Nombre", emp.nombre))
        datos_layout.addWidget(campo("Documento", emp.documento))
        datos_layout.addWidget(campo("Cargo", emp.cargo))
        datos_layout.addWidget(campo("Tipo de Contrato", emp.tipo_contrato))
        datos_layout.addWidget(campo("Teléfono", emp.telefono))
        datos_layout.addWidget(campo("Estado", "Activo" if emp.estado else "Inactivo"))
        datos_layout.addWidget(campo("Ingreso", str(emp.fecha_ingreso)))
        datos_layout.addStretch()

        # ---------------- ENSAMBLAR ----------------
        layout_principal.addWidget(self.lbl_foto)
        layout_principal.addLayout(datos_layout)

        layout_final = QVBoxLayout(self)
        layout_final.addWidget(contenedor)

        session.close()
