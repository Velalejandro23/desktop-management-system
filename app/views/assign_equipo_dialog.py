from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox,
    QSpinBox, QLabel, QLineEdit, QHeaderView
)
from PySide6.QtCore import Qt, QDate # QDate might not be needed if no date pickers
from app.database.db import get_session
from app.models.equipo import Equipo
import datetime # Might not be needed if no date handling

class AssignEquipoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asignar Equipo al Proyecto")
        self.resize(600, 400) # Adjusted size
        self.selected_equipo_data = None
        self.equipos = []

        self.init_ui()
        self.load_equipos()
    def init_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(QLabel("Seleccione un equipo y la cantidad a asignar:")) # Updated message

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Buscar equipo...")
        self.buscador.textChanged.connect(self.filtrar)
        main_layout.addWidget(self.buscador)

        self.table_equipos = QTableWidget()
        self.table_equipos.setColumnCount(4)
        self.table_equipos.setHorizontalHeaderLabels(["ID", "Nombre", "Tipo", "Cantidad Total"]) # Updated header
        self.table_equipos.setColumnHidden(0, True) # Hide ID
        self.table_equipos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_equipos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_equipos.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_equipos.setAlternatingRowColors(True)
        self.table_equipos.verticalHeader().setDefaultSectionSize(40)
        self.table_equipos.verticalHeader().setVisible(False)
        self.table_equipos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table_equipos)

        self.table_equipos.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Replaced details_layout with quantity_layout
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Cantidad a asignar:"))
        self.quantity_spinbox = QSpinBox() # New QSpinBox for quantity
        self.quantity_spinbox.setRange(1, 999999) # Assuming integer quantity
        self.quantity_spinbox.setValue(1) # Default to 1 unit
        quantity_layout.addWidget(self.quantity_spinbox)
        main_layout.addLayout(quantity_layout)

        button_layout = QHBoxLayout()
        btn_accept = QPushButton("Aceptar")
        btn_accept.clicked.connect(self.accept_assignment)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(btn_accept)
        button_layout.addWidget(btn_cancel)
        main_layout.addLayout(button_layout)

    def filtrar(self, texto):
        texto = texto.lower()
        for fila in range(self.table_equipos.rowCount()):
            coincide = False
            for columna in range(self.table_equipos.columnCount()):
                item = self.table_equipos.item(fila, columna)
                if item and texto in item.text().lower():
                    coincide = True
                    break
            self.table_equipos.setRowHidden(fila, not coincide)

    def load_equipos(self):
        session = get_session()
        self.equipos = session.query(Equipo).all() # Load all equipment
        session.close()
        # Determine currently assigned quantities from parent (if available)
        assigned_totals = {}
        if self.parent() and hasattr(self.parent(), 'assigned_equipos'):
            for item in getattr(self.parent(), 'assigned_equipos'):
                eid = item.get('equipo_id')
                assigned_totals[eid] = assigned_totals.get(eid, 0) + int(item.get('cantidad', 0))

        self.table_equipos.setRowCount(len(self.equipos))
        for row, eq in enumerate(self.equipos):
            assigned = assigned_totals.get(eq.id, 0)
            available = max(0, int(eq.cantidad) - assigned)
            self.table_equipos.setItem(row, 0, QTableWidgetItem(str(eq.id)))
            self.table_equipos.setItem(row, 1, QTableWidgetItem(eq.nombre.title()))
            self.table_equipos.setItem(row, 2, QTableWidgetItem(eq.tipo.title()))
            self.table_equipos.setItem(row, 3, QTableWidgetItem(str(available))) # Display remaining available quantity

    def accept_assignment(self):
        selected_rows = self.table_equipos.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, seleccione un equipo.")
            return

        row = selected_rows[0].row()
        equipo_id = int(self.table_equipos.item(row, 0).text())
        nombre_equipo = self.table_equipos.item(row, 1).text()
        available_quantity = int(self.table_equipos.item(row, 3).text()) # Get available quantity after current form assignments

        assigned_quantity = self.quantity_spinbox.value()

        if assigned_quantity <= 0:
            QMessageBox.warning(self, "Cantidad Inválida", "La cantidad a asignar debe ser mayor que cero.")
            return

        if assigned_quantity > available_quantity:
            QMessageBox.warning(self, "Cantidad Insuficiente", f"Solo hay {available_quantity} unidades de {nombre_equipo} disponible.")
            return

        self.selected_equipo_data = {
            "equipo_id": equipo_id,
            "nombre_equipo": nombre_equipo,
            "cantidad": assigned_quantity, # New quantity field
            "costo_uso": 0.0 # Costo de uso ya no es necesario
        }
        self.accept()

    def get_selected_equipo(self):
        return self.selected_equipo_data

    def on_selection_changed(self, selected, deselected):
        sel = self.table_equipos.selectionModel().selectedRows()
        if not sel:
            return
        row = sel[0].row()
        try:
            available = int(self.table_equipos.item(row, 3).text())
        except Exception:
            available = 0
        if available >= 1:
            self.quantity_spinbox.setRange(1, available)
            self.quantity_spinbox.setValue(1)
            self.quantity_spinbox.setEnabled(True)
        else:
            self.quantity_spinbox.setRange(0, 0)
            self.quantity_spinbox.setValue(0)
            self.quantity_spinbox.setEnabled(False)