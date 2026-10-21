from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QSpinBox, QWidget
)
from PySide6.QtCore import Qt

class ReturnItemsDialog(QDialog):
    def __init__(self, equipos_dict, materiales_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Devolver Elementos al Stock")
        self.resize(600, 500)

        # equipos_dict: {equipo_id: {"nombre_equipo": str, "cantidad": int}}
        # materiales_dict: {material_id: {"nombre_material": str, "cantidad": int}}
        self.equipos = equipos_dict
        self.materiales = materiales_dict
        self.equipo_controls = {} # equipo_id -> spinbox
        self.material_controls = {} # material_id -> spinbox

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Seleccione la cantidad de elementos a devolver:"))

        self.table = QTableWidget()
        self.table.setColumnCount(4) # Tipo, Nombre, Asignados, Devolver
        self.table.setHorizontalHeaderLabels(["Tipo", "Nombre", "Asignados", "Devolver"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Aceptar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def load_data(self):
        total_rows = len(self.equipos) + len(self.materiales)
        self.table.setRowCount(total_rows)
        row = 0
        
        # Load Equipment
        for equipo_id, data in self.equipos.items():
            # Tipo
            self.table.setItem(row, 0, QTableWidgetItem("Equipo"))
            # Nombre
            self.table.setItem(row, 1, QTableWidgetItem(data['nombre_equipo']))
            # Asignados
            item_asig = QTableWidgetItem(str(data['cantidad']))
            item_asig.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item_asig)

            # Spinbox para devolver
            spin = QSpinBox()
            spin.setRange(0, data['cantidad'])
            spin.setValue(data['cantidad'])
            spin.setAlignment(Qt.AlignCenter)
            
            container = QHBoxLayout()
            container.addWidget(spin)
            container.setContentsMargins(10, 2, 10, 2)
            widget = QWidget()
            widget.setLayout(container)
            
            self.table.setCellWidget(row, 3, widget)
            self.equipo_controls[equipo_id] = spin
            row += 1

        # Load Materials
        for material_id, data in self.materiales.items():
            # Tipo
            self.table.setItem(row, 0, QTableWidgetItem("Material"))
            # Nombre
            self.table.setItem(row, 1, QTableWidgetItem(data['nombre_material']))
            # Asignados
            item_asig = QTableWidgetItem(str(data['cantidad']))
            item_asig.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item_asig)

            # Spinbox para devolver
            spin = QSpinBox()
            spin.setRange(0, data['cantidad'])
            spin.setValue(data['cantidad'])
            spin.setAlignment(Qt.AlignCenter)
            
            container = QHBoxLayout()
            container.addWidget(spin)
            container.setContentsMargins(10, 2, 10, 2)
            widget = QWidget()
            widget.setLayout(container)
            
            self.table.setCellWidget(row, 3, widget)
            self.material_controls[material_id] = spin
            row += 1

    def get_returns(self):
        # Returns dict { "equipos": {equipo_id: qty}, "materiales": {material_id: qty} }
        return {
            "equipos": {eid: spin.value() for eid, spin in self.equipo_controls.items() if spin.value() > 0},
            "materiales": {mid: spin.value() for mid, spin in self.material_controls.items() if spin.value() > 0}
        }
