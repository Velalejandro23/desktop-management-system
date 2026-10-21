from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QDateTimeEdit, QMessageBox, QComboBox
)
from PySide6.QtCore import QDateTime
from app.database.db import get_session
from app.models.visita import Visita
from app.models.proyecto import Proyecto


class VisitForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nueva Visita")
        self.setFixedSize(400, 450)

        layout = QVBoxLayout()

        self.titulo = QLineEdit()
        self.descripcion = QTextEdit()

        self.fecha_inicio_date = QDateEdit(QDateTime.currentDateTime().date())
        self.fecha_inicio_date.setCalendarPopup(True)
        self.fecha_inicio_time = QTimeEdit(QDateTime.currentDateTime().time())

        self.fecha_fin_date = QDateEdit(QDateTime.currentDateTime().date())
        self.fecha_fin_date.setCalendarPopup(True)
        self.fecha_fin_time = QTimeEdit(QDateTime.currentDateTime().time())

        self.recibe_persona = QLineEdit()
        self.direccion = QLineEdit()
        self.tipo_visita = QLineEdit() # Could be QComboBox for predefined types
        self.objetivo = QTextEdit()
        self.persona_hace_visita = QLineEdit()

        self.proyecto = QComboBox()
        self.estado = QComboBox()
        self.estado.addItems(["Pendiente", "En proceso", "Finalizada"])

        self.cargar_proyectos()

        btn_guardar = QPushButton("Guardar visita")
        btn_guardar.clicked.connect(self.guardar)

        layout.addWidget(QLabel("Título"))
        layout.addWidget(self.titulo)

        layout.addWidget(QLabel("Descripción"))
        layout.addWidget(self.descripcion)

        # Fecha y Hora de inicio
        fecha_inicio_layout = QHBoxLayout()
        fecha_inicio_layout.addWidget(QLabel("Fecha inicio"))
        fecha_inicio_layout.addWidget(self.fecha_inicio_date)
        fecha_inicio_layout.addWidget(QLabel("Hora inicio"))
        fecha_inicio_layout.addWidget(self.fecha_inicio_time)
        layout.addLayout(fecha_inicio_layout)

        # Fecha y Hora de fin
        fecha_fin_layout = QHBoxLayout()
        fecha_fin_layout.addWidget(QLabel("Fecha fin"))
        fecha_fin_layout.addWidget(self.fecha_fin_date)
        fecha_fin_layout.addWidget(QLabel("Hora fin"))
        fecha_fin_layout.addWidget(self.fecha_fin_time)
        layout.addLayout(fecha_fin_layout)

        layout.addWidget(QLabel("Recibe (persona)"))
        layout.addWidget(self.recibe_persona)

        layout.addWidget(QLabel("Dirección"))
        layout.addWidget(self.direccion)

        layout.addWidget(QLabel("Tipo de visita"))
        layout.addWidget(self.tipo_visita)

        layout.addWidget(QLabel("Objetivo"))
        layout.addWidget(self.objetivo)

        layout.addWidget(QLabel("Persona que hará la visita"))
        layout.addWidget(self.persona_hace_visita)

        layout.addWidget(QLabel("Proyecto"))
        layout.addWidget(self.proyecto)

        layout.addWidget(QLabel("Estado"))
        layout.addWidget(self.estado)

        layout.addWidget(btn_guardar)

        self.setLayout(layout)

    def cargar_proyectos(self):
        session = get_session()
        proyectos = session.query(Proyecto).all()
        for p in proyectos:
            self.proyecto.addItem(p.nombre, p.id)
        session.close()

    def guardar(self):
        session = get_session()

        fecha_inicio_dt = self.fecha_inicio_date.date().toPython()
        hora_inicio_dt = self.fecha_inicio_time.time().toPython()
        fecha_fin_dt = self.fecha_fin_date.date().toPython()
        hora_fin_dt = self.fecha_fin_time.time().toPython()

        fecha_inicio_combined = datetime.combine(fecha_inicio_dt, hora_inicio_dt)
        fecha_fin_combined = datetime.combine(fecha_fin_dt, hora_fin_dt)

        nueva = Visita(
            titulo=self.titulo.text(),
            descripcion=self.descripcion.toPlainText(),
            fecha_inicio=fecha_inicio_combined,
            fecha_fin=fecha_fin_combined,
            recibe_persona=self.recibe_persona.text(),
            direccion=self.direccion.text(),
            tipo_visita=self.tipo_visita.text(),
            objetivo=self.objetivo.toPlainText(),
            persona_hace_visita=self.persona_hace_visita.text(),
            proyecto_id=self.proyecto.currentData(),
            estado=self.estado.currentText()
        )

        session.add(nueva)
        session.commit()
        session.close()

        QMessageBox.information(self, "Éxito", "Visita registrada correctamente")
        self.close()
