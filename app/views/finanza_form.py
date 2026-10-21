from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLineEdit,
    QPushButton, QMessageBox, QDoubleSpinBox, QComboBox, QDateEdit
)
from PySide6.QtCore import QDate, Signal # Added Signal
from app.database.db import get_session
from app.models.finanza import Finanza
from app.models.proyecto import Proyecto
import datetime

class FinanzaForm(QDialog):
    data_changed = Signal() # Define the custom signal

    def __init__(self, finanza_id=None):
        super().__init__()
        self.finanza_id = finanza_id
        if self.finanza_id:
            self.setWindowTitle("Editar Movimiento Financiero")
            self.finanza = get_session().get(Finanza, self.finanza_id)
        else:
            self.setWindowTitle("Nuevo Movimiento Financiero")
            self.finanza = None

        self.init_ui()
        if self.finanza:
            self.cargar_datos()

    def init_ui(self):
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.tipo = QComboBox()
        self.tipo.addItems(["Ingreso", "Egreso"])
        self.concepto = QLineEdit()
        self.monto = QDoubleSpinBox()
        self.monto.setRange(0.0, 999999999999.99)
        self.monto.setDecimals(0)
        self.monto.setPrefix("$ ")
        self.monto.setGroupSeparatorShown(True)
        self.fecha = QDateEdit(QDate.currentDate())
        self.fecha.setCalendarPopup(True)

        self.proyecto_combo = QComboBox()
        self._cargar_proyectos_a_combo()


        form_layout.addRow("Tipo:", self.tipo)
        form_layout.addRow("Concepto:", self.concepto)
        form_layout.addRow("Monto:", self.monto)
        form_layout.addRow("Fecha:", self.fecha)
        form_layout.addRow("Proyecto:", self.proyecto_combo)
        
        layout.addLayout(form_layout)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(self.btn_guardar)

    def _cargar_proyectos_a_combo(self):
        session = get_session()
        self.proyectos = session.query(Proyecto).all()
        session.close()

        self.proyecto_combo.addItem("Ninguno", None) # Option for no project
        for p in self.proyectos:
            self.proyecto_combo.addItem(p.nombre, p.id)

    def cargar_datos(self):
        self.tipo.setCurrentText(self.finanza.tipo or "Ingreso")
        self.concepto.setText(self.finanza.concepto)
        self.monto.setValue(self.finanza.monto or 0)
        self.fecha.setDate(QDate.fromPython(self.finanza.fecha or datetime.date.today()))
        
        # Select the correct project in the combo box
        if self.finanza.proyecto_id:
            index = self.proyecto_combo.findData(self.finanza.proyecto_id)
            if index != -1:
                self.proyecto_combo.setCurrentIndex(index)
        else:
            self.proyecto_combo.setCurrentIndex(0) # "Ninguno"

    def guardar(self):
        if not self.concepto.text():
            QMessageBox.warning(self, "Atención", "El concepto es obligatorio.")
            return
        if self.monto.value() <= 0:
            QMessageBox.warning(self, "Atención", "El monto debe ser mayor que cero.")
            return

        session = get_session()
        if self.finanza_id:
            finanza = session.get(Finanza, self.finanza_id)
        else:
            finanza = Finanza()

        finanza.tipo = self.tipo.currentText()
        finanza.concepto = self.concepto.text()
        finanza.monto = self.monto.value()
        finanza.fecha = self.fecha.date().toPython()
        finanza.proyecto_id = self.proyecto_combo.currentData() # Get the project ID

        if not self.finanza_id:
            session.add(finanza)
        
        session.commit()
        session.close()
        self.data_changed.emit() # Emit signal after successful save
        self.accept()
