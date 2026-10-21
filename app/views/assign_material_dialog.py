from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox, QDoubleSpinBox, QLabel, QLineEdit, QHeaderView  
)
from PySide6.QtCore import Qt
from app.database.db import get_session
from app.models.material import Material

class AssignMaterialDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asignar Material al Proyecto")
        self.resize(600, 400)
        self.selected_material_data = None
        self.materials = []

        self.init_ui()
        self.load_materials()
    def init_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(QLabel("Seleccione un material y asigne la cantidad:"))

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Buscar material...")
        self.buscador.textChanged.connect(self.filtrar)
        main_layout.addWidget(self.buscador)

        self.table_materials = QTableWidget()
        self.table_materials.setColumnCount(4)
        self.table_materials.setHorizontalHeaderLabels(["ID", "Nombre", "Unidad", "Disponible"])
        self.table_materials.setColumnHidden(0, True) # Hide ID
        self.table_materials.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_materials.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_materials.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_materials.setAlternatingRowColors(True)
        self.table_materials.verticalHeader().setDefaultSectionSize(40)
        self.table_materials.verticalHeader().setVisible(False)
        self.table_materials.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table_materials)

        self.table_materials.selectionModel().selectionChanged.connect(self.on_selection_changed)

        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Cantidad a asignar:"))
        self.quantity_spinbox = QDoubleSpinBox()
        self.quantity_spinbox.setRange(0.01, 999999.99)
        self.quantity_spinbox.setDecimals(2)
        self.quantity_spinbox.setValue(1.0) # Default to 1.0 unit
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

    def get_selected_material(self):
        return self.selected_material_data

    def filtrar(self, texto):
        texto = texto.lower()
        for fila in range(self.table_materials.rowCount()):
            coincide = False
            for columna in range(self.table_materials.columnCount()):
                item = self.table_materials.item(fila, columna)
                if item and texto in item.text().lower():
                    coincide = True
                    break
            self.table_materials.setRowHidden(fila, not coincide)

        self.table_materials.selectionModel().selectionChanged.connect(self.on_selection_changed)

        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Cantidad a asignar:"))
        self.quantity_spinbox = QDoubleSpinBox()
        self.quantity_spinbox.setRange(0.01, 999999.99)
        self.quantity_spinbox.setDecimals(2)
        self.quantity_spinbox.setValue(1.0) # Default to 1.0 unit
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

    def load_materials(self):
        session = get_session()
        self.materials = session.query(Material).all()
        session.close()

        # Determine currently assigned quantities from parent (if available)
        assigned_totals = {}
        if self.parent() and hasattr(self.parent(), 'assigned_materiales'):
            for item in getattr(self.parent(), 'assigned_materiales'):
                mid = item.get('material_id')
                assigned_totals[mid] = assigned_totals.get(mid, 0) + float(item.get('cantidad', 0))

        # Only show materials that have remaining available quantity
        display_materials = []
        for mat in self.materials:
            assigned = assigned_totals.get(mat.id, 0.0)
            available = max(0.0, float(mat.cantidad or 0.0) - assigned)
            if available > 0:
                display_materials.append((mat, available))

        self.table_materials.setRowCount(len(display_materials))
        for row, (mat, available) in enumerate(display_materials):
            self.table_materials.setItem(row, 0, QTableWidgetItem(str(mat.id)))
            self.table_materials.setItem(row, 1, QTableWidgetItem(mat.nombre.title()))
            self.table_materials.setItem(row, 2, QTableWidgetItem(mat.unidad or ""))
            self.table_materials.setItem(row, 3, QTableWidgetItem(str(available)))

    def accept_assignment(self):
        selected_rows = self.table_materials.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, seleccione un material.")
            return

        row = selected_rows[0].row()
        material_id = int(self.table_materials.item(row, 0).text())
        nombre_material = self.table_materials.item(row, 1).text()
        available_quantity = float(self.table_materials.item(row, 3).text())
        
        assigned_quantity = self.quantity_spinbox.value()

        if assigned_quantity > available_quantity:
            QMessageBox.warning(self, "Cantidad Insuficiente", f"Solo hay {available_quantity} {self.table_materials.item(row, 2).text()} de {nombre_material} disponible.")
            return

        session = get_session()
        material_obj = session.get(Material, material_id)
        # Removed: cost_per_unit = material_obj.costo_unitario if material_obj else 0.0
        session.close()

        self.selected_material_data = {
            "material_id": material_id,
            "nombre_material": nombre_material,
            "cantidad": assigned_quantity,
            "costo": 0.0 # Set cost to 0.0 as per user's clarification ("sin costos")
        }
        self.accept()

    def get_selected_material(self):
        return self.selected_material_data

    def on_selection_changed(self, selected, deselected):
        sel = self.table_materials.selectionModel().selectedRows()
        if not sel:
            return
        row = sel[0].row()
        try:
            available = float(self.table_materials.item(row, 3).text())
        except Exception:
            available = 0.0
        if available >= 0.01:
            self.quantity_spinbox.setRange(0.01, available)
            self.quantity_spinbox.setEnabled(True)
            # Keep current value or set to 0.01 if greater than available
            if self.quantity_spinbox.value() > available:
                self.quantity_spinbox.setValue(available)
        else:
            self.quantity_spinbox.setRange(0.0, 0.0)
            self.quantity_spinbox.setValue(0.0)
            self.quantity_spinbox.setEnabled(False)