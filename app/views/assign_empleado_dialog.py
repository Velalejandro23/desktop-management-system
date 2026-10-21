from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox, QSpinBox, QLabel, QLineEdit, QHeaderView
)
from PySide6.QtCore import Qt
from app.database.db import get_session
from app.models.empleado import Empleado

class AssignEmpleadoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asignar Empleado al Proyecto")
        self.resize(500, 300) # Adjusted size
        self.selected_empleado_data = None
        self.empleados = []

        self.init_ui()
        self.load_empleados()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(QLabel("Seleccione un empleado:")) # Simplified message

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Buscar empleado...")
        self.buscador.textChanged.connect(self.filtrar)
        main_layout.addWidget(self.buscador)

        self.table_empleados = QTableWidget()
        self.table_empleados.setColumnCount(3) # Removed 'Salario' column
        self.table_empleados.setHorizontalHeaderLabels(["ID", "Nombre Completo", "Cargo"]) # Removed 'Salario' header
        self.table_empleados.setColumnHidden(0, True) # Hide ID
        self.table_empleados.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_empleados.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_empleados.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_empleados.setAlternatingRowColors(True)
        self.table_empleados.verticalHeader().setDefaultSectionSize(40)
        self.table_empleados.verticalHeader().setVisible(False)
        self.table_empleados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table_empleados)

        # Removed hours_layout and self.hours_spinbox
        # Removed hours_layout.addWidget(QLabel("Horas a asignar:"))
        # Removed self.hours_spinbox = QSpinBox()
        # Removed self.hours_spinbox.setRange(1, 9999)
        # Removed self.hours_spinbox.setValue(80) # Default to 80 hours
        # Removed hours_layout.addWidget(self.hours_spinbox)
        # Removed main_layout.addLayout(hours_layout)

        button_layout = QHBoxLayout()
        btn_accept = QPushButton("Aceptar")
        btn_accept.clicked.connect(self.accept_assignment)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(btn_accept)
        button_layout.addWidget(btn_cancel)
        main_layout.addLayout(button_layout)

    def load_empleados(self):
        session = get_session()
        self.empleados = session.query(Empleado).filter_by(estado=1).all() # Only active employees
        session.close()

        self.table_empleados.setRowCount(len(self.empleados))
        for row, emp in enumerate(self.empleados):
            self.table_empleados.setItem(row, 0, QTableWidgetItem(str(emp.id)))
            self.table_empleados.setItem(row, 1, QTableWidgetItem(f"{emp.nombre} {emp.apellidos}"))
            self.table_empleados.setItem(row, 2, QTableWidgetItem(emp.cargo or ""))
            # Removed: self.table_empleados.setItem(row, 3, QTableWidgetItem(f"${emp.salario or 0.0:.2f}"))

    def accept_assignment(self):
        selected_rows = self.table_empleados.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, seleccione un empleado.")
            return

        row = selected_rows[0].row()
        empleado_id = int(self.table_empleados.item(row, 0).text())
        nombre_completo = self.table_empleados.item(row, 1).text()
        # Removed: salario = float(self.table_empleados.item(row, 3).text().replace('$', '')) # Remove $ for conversion
        # Removed: horas = self.hours_spinbox.value()

        self.selected_empleado_data = {
            "empleado_id": empleado_id,
            "nombre_empleado": nombre_completo,
            # Removed: "salario_hora": salario,
            # Removed: "horas": horas
        }
        self.accept()

    def get_selected_empleado(self):
        return self.selected_empleado_data

    def filtrar(self, texto):
        texto = texto.lower()
        for fila in range(self.table_empleados.rowCount()):
            coincide = False
            for columna in range(self.table_empleados.columnCount()):
                item = self.table_empleados.item(fila, columna)
                if item and texto in item.text().lower():
                    coincide = True
                    break
            self.table_empleados.setRowHidden(fila, not coincide)