from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QDateTimeEdit, QFormLayout, QGroupBox, QMessageBox, QDateEdit, QTimeEdit, QHBoxLayout
)
from PySide6.QtCore import QDateTime, QTime, Qt

class AddVisitDialog(QDialog):
    def __init__(self, fecha):
        super().__init__()
        self.setWindowTitle("Nueva Visita")
        self.setMinimumWidth(400)
        self.init_ui(fecha)

    def init_ui(self, fecha):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # --- Campos Principales ---
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.titulo = QLineEdit()
        self.titulo.setPlaceholderText("Ej: Visita de mantenimiento a Cliente X")
        form_layout.addRow(QLabel("Título:"), self.titulo)

        self.descripcion = QTextEdit()
        self.descripcion.setPlaceholderText("Añade detalles sobre la visita...")
        self.descripcion.setMinimumHeight(80)
        form_layout.addRow(QLabel("Descripción:"), self.descripcion)

        main_layout.addLayout(form_layout)

        # --- Grupo de Fechas ---
        date_group_box = QGroupBox("Horario de la Visita")
        date_layout = QFormLayout()

        # Fecha y Hora de inicio
        self.fecha_inicio_date = QDateEdit(fecha)
        self.fecha_inicio_date.setCalendarPopup(True)
        self.fecha_inicio_time = QTimeEdit(QTime(8, 0)) # Default to 8:00
        fecha_inicio_h_layout = QHBoxLayout()
        fecha_inicio_h_layout.addWidget(self.fecha_inicio_date)
        fecha_inicio_h_layout.addWidget(self.fecha_inicio_time)
        date_layout.addRow("Inicio:", fecha_inicio_h_layout)

        # Fecha y Hora de fin
        self.fecha_fin_date = QDateEdit(fecha)
        self.fecha_fin_date.setCalendarPopup(True)
        self.fecha_fin_time = QTimeEdit(QTime(9, 0)) # Default to 9:00
        fecha_fin_h_layout = QHBoxLayout()
        fecha_fin_h_layout.addWidget(self.fecha_fin_date)
        fecha_fin_h_layout.addWidget(self.fecha_fin_time)
        date_layout.addRow("Fin:", fecha_fin_h_layout)
        
        date_group_box.setLayout(date_layout)
        main_layout.addWidget(date_group_box)

        # --- Nuevos Campos ---
        new_fields_group_box = QGroupBox("Detalles Adicionales")
        new_fields_layout = QFormLayout()

        self.recibe_persona = QLineEdit()
        self.recibe_persona.setPlaceholderText("Ej: Juan Pérez")
        new_fields_layout.addRow(QLabel("Recibe:"), self.recibe_persona)

        self.direccion = QLineEdit()
        self.direccion.setPlaceholderText("Ej: Calle Falsa 123")
        new_fields_layout.addRow(QLabel("Dirección:"), self.direccion)

        self.tipo_visita = QLineEdit()
        self.tipo_visita.setPlaceholderText("Ej: Mantenimiento, Venta, Soporte")
        new_fields_layout.addRow(QLabel("Tipo de Visita:"), self.tipo_visita)

        self.objetivo = QTextEdit()
        self.objetivo.setPlaceholderText("Describa el objetivo de la visita...")
        self.objetivo.setMinimumHeight(60)
        new_fields_layout.addRow(QLabel("Objetivo:"), self.objetivo)

        self.persona_hace_visita = QLineEdit()
        self.persona_hace_visita.setPlaceholderText("Ej: María García")
        new_fields_layout.addRow(QLabel("Persona que visita:"), self.persona_hace_visita)

        new_fields_group_box.setLayout(new_fields_layout)
        main_layout.addWidget(new_fields_group_box)

        # --- Botón de Guardar ---
        btn_guardar = QPushButton("Guardar Visita")
        btn_guardar.setObjectName("newVisitButton") # Re-use existing green style
        btn_guardar.clicked.connect(self.accept)

        main_layout.addWidget(btn_guardar)

        self.setLayout(main_layout)

    def accept(self):
        # Combina las fechas y horas para validación
        self.fecha_inicio = QDateTime(self.fecha_inicio_date.date(), self.fecha_inicio_time.time())
        self.fecha_fin = QDateTime(self.fecha_fin_date.date(), self.fecha_fin_time.time())
        
        recibe_persona_text = self.recibe_persona.text()
        direccion_text = self.direccion.text()
        tipo_visita_text = self.tipo_visita.text()
        objetivo_text = self.objetivo.toPlainText()
        persona_hace_visita_text = self.persona_hace_visita.text()

        # Validación de entrada
        if not self.titulo.text().strip():
            QMessageBox.warning(self, "Campo Requerido", "El título de la visita no puede estar vacío.")
            return
        if not recibe_persona_text.strip():
            QMessageBox.warning(self, "Campo Requerido", "La persona que recibe la visita no puede estar vacía.")
            return
        if not direccion_text.strip():
            QMessageBox.warning(self, "Campo Requerido", "La dirección de la visita no puede estar vacía.")
            return
        if not tipo_visita_text.strip():
            QMessageBox.warning(self, "Campo Requerido", "El tipo de visita no puede estar vacío.")
            return
        if not objetivo_text.strip():
            QMessageBox.warning(self, "Campo Requerido", "El objetivo de la visita no puede estar vacío.")
            return
        if not persona_hace_visita_text.strip():
            QMessageBox.warning(self, "Campo Requerido", "La persona que hará la visita no puede estar vacía.")
            return

        # Validación de fechas
        if self.fecha_inicio >= self.fecha_fin:
            QMessageBox.warning(self, "Error de Fechas", "La fecha de inicio debe ser anterior a la fecha de fin.")
            return

        # Asigna los valores de texto a los atributos de la instancia
        self.recibe_persona_text = recibe_persona_text
        self.direccion_text = direccion_text
        self.tipo_visita_text = tipo_visita_text
        self.objetivo_text = objetivo_text
        self.persona_hace_visita_text = persona_hace_visita_text

        # Si todo es válido, llama al accept original para cerrar el diálogo
        super().accept()