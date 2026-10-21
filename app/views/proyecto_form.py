from PySide6.QtWidgets import (
    QDialog, QFormLayout, QVBoxLayout, QLineEdit,QHeaderView,QPushButton, QMessageBox, QDoubleSpinBox, QComboBox, QTextEdit, QDateEdit,
    QHBoxLayout, QLabel, QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QSpinBox, QInputDialog
)
from PySide6.QtCore import QDate, Qt, Signal # Added Qt for alignment

from app.database.db import get_session
from app.models.proyecto import Proyecto
# Import association models and related entity models
from app.models.proyecto_empleado import ProyectoEmpleado
from app.models.proyecto_material import ProyectoMaterial
from app.models.proyecto_equipo import ProyectoEquipo
from app.models.empleado import Empleado
from app.models.material import Material
from app.models.equipo import Equipo
from app.models.gasto import Gasto # Import Gasto model
from app.models.ingreso_proyecto import IngresoProyecto # Import IngresoProyecto model
import datetime

class ProyectoForm(QDialog):
    financial_data_changed = Signal() # Define the custom signal

    def __init__(self, proyecto_id=None):
        super().__init__()
        self.proyecto_id = proyecto_id
        self.setWindowTitle("Gestión de Proyectos")
        self.resize(1100, 900) # Increased size for complex form

        # Lists to hold current assignments
        self.assigned_empleados = []
        self.assigned_materiales = []
        self.assigned_equipos = []
        self.assigned_gastos = [] # New list to hold assigned expenses
        self.assigned_ingresos = [] # New list to hold assigned incomes

        self.init_ui()

        if proyecto_id:
            self.cargar_datos()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("Gestión de Proyecto")
        title_label.setObjectName("titulo")
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)

        # Basic Project Fields (grouped in a form layout for neatness)
        project_details_layout = QFormLayout()

        self.nombre = QLineEdit()
        project_details_layout.addRow("Nombre del Proyecto *", self.nombre)

        self.cliente = QLineEdit()
        project_details_layout.addRow("Cliente", self.cliente)

        self.descripcion = QTextEdit()
        self.descripcion.setFixedHeight(60) # Smaller height for overview
        project_details_layout.addRow("Descripción", self.descripcion)

        self.fecha_inicio = QDateEdit(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        project_details_layout.addRow("Fecha de Inicio", self.fecha_inicio)

        self.fecha_fin = QDateEdit(QDate.currentDate().addDays(30))
        self.fecha_fin.setCalendarPopup(True)
        project_details_layout.addRow("Fecha de Fin", self.fecha_fin)

        self.estado = QComboBox()
        self.estado.addItems(["Planificado", "En progreso", "Completado", "Suspendido", "Cancelado"])
        project_details_layout.addRow("Estado", self.estado)

        self.presupuesto = QDoubleSpinBox()
        self.presupuesto.setRange(0.0, 999999999999.99)
        self.presupuesto.setDecimals(0)
        self.presupuesto.setPrefix("$ ")
        self.presupuesto.setGroupSeparatorShown(True)
        project_details_layout.addRow("Presupuesto", self.presupuesto)

        self.anticipo = QDoubleSpinBox()
        self.anticipo.setRange(0.0, 999999999999.99)
        self.anticipo.setDecimals(0)
        self.anticipo.setPrefix("$ ")
        self.anticipo.setGroupSeparatorShown(True)
        project_details_layout.addRow("Anticipo", self.anticipo)

        main_layout.addLayout(project_details_layout)
        main_layout.addSpacing(20)

        # Tab Widget for Associations
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_empleados_tab(), "Empleados")
        self.tabs.addTab(self._create_materiales_tab(), "Materiales")
        self.tabs.addTab(self._create_equipos_tab(), "Equipos")
        self.tabs.addTab(self._create_gastos_tab(), "Gastos") # New tab for Expenses
        self.tabs.addTab(self._create_ingresos_tab(), "Ingresos") # New tab for Incomes
        main_layout.addWidget(self.tabs)

        # Buttons
        button_layout = QHBoxLayout()
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.clicked.connect(self.guardar)
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        button_layout.addWidget(btn_guardar)
        button_layout.addWidget(btn_cancelar)
        
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_ingresos_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.table_ingresos = QTableWidget()
        self.table_ingresos.setColumnCount(4) # ID, Descripción, Cantidad, Fecha
        self.table_ingresos.setHorizontalHeaderLabels(["ID", "Descripción", "Cantidad", "Fecha"])
        self.table_ingresos.setColumnHidden(0, True) # Hide ID column
        self.table_ingresos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_ingresos)

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Ingreso")
        btn_add.clicked.connect(self._add_ingreso)
        btn_remove = QPushButton("➖ Quitar Ingreso")
        btn_remove.clicked.connect(self._remove_ingreso)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)

        self.refresh_ingresos_table()
        return tab

    def _create_empleados_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Table for assigned employees
        self.table_empleados = QTableWidget()
        self.table_empleados.setColumnCount(2) # Removed 'Salario/Hora' and 'Horas'
        self.table_empleados.setHorizontalHeaderLabels(["ID", "Nombre"]) # Removed 'Salario/Hora' and 'Horas'
        self.table_empleados.setColumnHidden(0, True) # Hide ID column
        self.table_empleados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_empleados)

        # Buttons for employees
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Empleado")
        btn_add.clicked.connect(self._add_empleado)
        btn_remove = QPushButton("➖ Quitar Empleado")
        btn_remove.clicked.connect(self._remove_empleado)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)

        self.refresh_empleados_table()
        return tab

    def _create_materiales_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Table for assigned materials
        self.table_materiales = QTableWidget()
        self.table_materiales.setColumnCount(3) # Removed 'Costo' column
        self.table_materiales.setHorizontalHeaderLabels(["ID", "Material", "Cantidad"]) # Removed 'Costo' header
        self.table_materiales.setColumnHidden(0, True) # Hide ID column
        self.table_materiales.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_materiales)

        # Buttons for materials
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Material")
        btn_add.clicked.connect(self._add_material)
        btn_remove = QPushButton("➖ Quitar Material")
        btn_remove.clicked.connect(self._remove_material)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)

        self.refresh_materiales_table()
        return tab

    def _create_equipos_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Table for assigned equipment
        self.table_equipos = QTableWidget()
        self.table_equipos.setColumnCount(3) # Changed from 5 to 3 columns (ID, Equipo, Cantidad)
        self.table_equipos.setHorizontalHeaderLabels(["ID", "Equipo", "Cantidad"]) # Changed headers
        self.table_equipos.setColumnHidden(0, True) # Hide ID column
        self.table_equipos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_equipos)

        # Buttons for equipment
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Equipo")
        btn_add.clicked.connect(self._add_equipo)
        btn_remove = QPushButton("➖ Quitar Equipo")
        btn_remove.clicked.connect(self._remove_equipo)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)

        self.refresh_equipos_table()
        return tab

    def _create_gastos_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Table for assigned expenses
        self.table_gastos = QTableWidget()
        self.table_gastos.setColumnCount(4)
        self.table_gastos.setHorizontalHeaderLabels(["ID", "Descripción", "Cantidad", "Fecha"])
        self.table_gastos.setColumnHidden(0, True) # Hide ID column
        self.table_gastos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_gastos)

        # Buttons for expenses
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Gasto")
        btn_add.clicked.connect(self._add_gasto)
        btn_remove = QPushButton("➖ Quitar Gasto")
        btn_remove.clicked.connect(self._remove_gasto)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)

        self.refresh_gastos_table()
        return tab

    # Helper methods for refreshing tables and handling add/remove (implement later)
    def refresh_empleados_table(self):
        self.table_empleados.setRowCount(0)
        for row, assignment in enumerate(self.assigned_empleados):
            self.table_empleados.insertRow(row)
            self.table_empleados.setItem(row, 0, QTableWidgetItem(str(assignment["empleado_id"])))
            self.table_empleados.setItem(row, 1, QTableWidgetItem(assignment["nombre_empleado"]))
            # Removed: self.table_empleados.setItem(row, 2, QTableWidgetItem(f"${assignment['salario_hora']:.2f}"))
            # Removed: self.table_empleados.setItem(row, 3, QTableWidgetItem(str(assignment["horas"])))

    def _add_empleado(self):
        from app.views.assign_empleado_dialog import AssignEmpleadoDialog
        dialog = AssignEmpleadoDialog(self)
        if dialog.exec():
            empleado_data = dialog.get_selected_empleado()
            if empleado_data:
                # Check for duplicate assignment
                if any(e['empleado_id'] == empleado_data['empleado_id'] for e in self.assigned_empleados):
                    QMessageBox.warning(self, "Error de Asignación", "Este empleado ya ha sido asignado al proyecto.")
                    return
                # empleado_data now only contains 'empleado_id' and 'nombre_empleado'
                self.assigned_empleados.append(empleado_data)
                self.refresh_empleados_table()

    def _remove_empleado(self):
        selected_rows = self.table_empleados.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Quitar Empleado", "Seleccione un empleado de la tabla para quitar.")
            return
        
        # Remove from self.assigned_empleados and refresh
        for index in sorted(selected_rows, reverse=True):
            del self.assigned_empleados[index.row()]
        self.refresh_empleados_table()
        QMessageBox.information(self, "Quitar Empleado", "Empleado quitado de la lista temporal.")


    def refresh_materiales_table(self):
        self.table_materiales.setRowCount(0)
        for row, assignment in enumerate(self.assigned_materiales):
            self.table_materiales.insertRow(row)
            self.table_materiales.setItem(row, 0, QTableWidgetItem(str(assignment["material_id"])))
            self.table_materiales.setItem(row, 1, QTableWidgetItem(assignment["nombre_material"]))
            self.table_materiales.setItem(row, 2, QTableWidgetItem(str(assignment["cantidad"])))
            # Removed: self.table_materiales.setItem(row, 3, QTableWidgetItem(f"${assignment['costo']:.2f}"))

    def _add_material(self):
        from app.views.assign_material_dialog import AssignMaterialDialog
        dialog = AssignMaterialDialog(self)
        if dialog.exec():
            material_data = dialog.get_selected_material() # Contains 'material_id', 'nombre_material', 'cantidad'
            if material_data:
                material_id = material_data["material_id"]
                assigned_quantity = material_data["cantidad"]

                session = get_session()
                material_obj = session.get(Material, material_id)
                session.close()

                if not material_obj:
                    QMessageBox.warning(self, "Error", "Material no encontrado en la base de datos.")
                    return
                
                # Calculate current total quantity assigned for this material in this project
                current_assigned_total = sum(
                    item["cantidad"] for item in self.assigned_materiales if item["material_id"] == material_id
                )
                
                if (current_assigned_total + assigned_quantity) > material_obj.cantidad:
                    QMessageBox.warning(self, "Cantidad Excedida", 
                                        f"No se puede asignar {assigned_quantity} unidades de {material_data['nombre_material']}. "
                                        f"Ya hay {current_assigned_total} asignadas y solo quedan {material_obj.cantidad - current_assigned_total} disponibles del stock total ({material_obj.cantidad}).")
                    return
                
                # Add the new assignment
                self.assigned_materiales.append(material_data)
                self.refresh_materiales_table()

    def _remove_material(self):
        selected_rows = self.table_materiales.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Quitar Material", "Seleccione un material de la tabla para quitar.")
            return
        
        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            assignment = self.assigned_materiales[row]
            current_qty = assignment["cantidad"]
            
            if current_qty > 1:
                qty_to_remove, ok = QInputDialog.getInt(
                    self, "Quitar Material", 
                    f"¿Cuántas unidades de {assignment['nombre_material']} desea retirar? (Máx: {current_qty})",
                    current_qty, 1, current_qty
                )
                if ok:
                    if qty_to_remove >= current_qty:
                        del self.assigned_materiales[row]
                    else:
                        assignment["cantidad"] -= qty_to_remove
            else:
                del self.assigned_materiales[row]
                
        self.refresh_materiales_table()


    def refresh_equipos_table(self):
        self.table_equipos.setRowCount(0)
        for row, assignment in enumerate(self.assigned_equipos):
            self.table_equipos.insertRow(row)
            self.table_equipos.setItem(row, 0, QTableWidgetItem(str(assignment["equipo_id"])))
            self.table_equipos.setItem(row, 1, QTableWidgetItem(assignment["nombre_equipo"]))
            self.table_equipos.setItem(row, 2, QTableWidgetItem(str(assignment["cantidad"]))) # Display assigned quantity
            # Removed: self.table_equipos.setItem(row, 2, QTableWidgetItem(assignment["fecha_asignacion"].strftime('%Y-%m-%d')))
            # Removed: self.table_equipos.setItem(row, 3, QTableWidgetItem(assignment["fecha_retiro"].strftime('%Y-%m-%d') if assignment["fecha_retiro"] else "N/A"))
            # Removed: self.table_equipos.setItem(row, 4, QTableWidgetItem(f"${assignment['costo_uso']:.2f}"))

    def _add_equipo(self):
        from app.views.assign_equipo_dialog import AssignEquipoDialog
        dialog = AssignEquipoDialog(self)
        if dialog.exec():
            equipo_data = dialog.get_selected_equipo() # Contains 'equipo_id', 'nombre_equipo', 'cantidad', 'costo_uso'
            if equipo_data:
                equipo_id = equipo_data["equipo_id"]
                assigned_quantity = equipo_data["cantidad"]

                session = get_session()
                equipo_obj = session.get(Equipo, equipo_id)
                session.close()

                if not equipo_obj:
                    QMessageBox.warning(self, "Error", "Equipo no encontrado en la base de datos.")
                    return

                # Calculate current total quantity assigned for this equipo in this project
                current_assigned_total = sum(
                    item["cantidad"] for item in self.assigned_equipos if item["equipo_id"] == equipo_id
                )
                
                if (current_assigned_total + assigned_quantity) > equipo_obj.cantidad:
                    QMessageBox.warning(self, "Cantidad Excedida", 
                                        f"No se puede asignar {assigned_quantity} unidades de {equipo_data['nombre_equipo']}. "
                                        f"Ya hay {current_assigned_total} asignadas y solo quedan {equipo_obj.cantidad - current_assigned_total} disponibles del stock total ({equipo_obj.cantidad}).")
                    return
                
                # Add the new assignment
                self.assigned_equipos.append(equipo_data)
                self.refresh_equipos_table()

    def _remove_equipo(self):
        selected_rows = self.table_equipos.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Quitar Equipo", "Seleccione un equipo de la tabla para quitar.")
            return
        
        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            assignment = self.assigned_equipos[row]
            current_qty = assignment["cantidad"]
            
            if current_qty > 1:
                qty_to_remove, ok = QInputDialog.getInt(
                    self, "Quitar Equipo", 
                    f"¿Cuántas unidades de {assignment['nombre_equipo']} desea retirar? (Máx: {current_qty})",
                    current_qty, 1, current_qty
                )
                if ok:
                    if qty_to_remove >= current_qty:
                        del self.assigned_equipos[row]
                    else:
                        assignment["cantidad"] -= qty_to_remove
            else:
                del self.assigned_equipos[row]
                
        self.refresh_equipos_table()
    
    def refresh_gastos_table(self):
        self.table_gastos.setRowCount(0)
        for row, gasto in enumerate(self.assigned_gastos):
            self.table_gastos.insertRow(row)
            self.table_gastos.setItem(row, 0, QTableWidgetItem(str(gasto.get("id", "")))) # Gasto ID if exists
            self.table_gastos.setItem(row, 1, QTableWidgetItem(gasto["descripcion"]))
            self.table_gastos.setItem(row, 2, QTableWidgetItem(f"${gasto['cantidad']:.2f}"))
            self.table_gastos.setItem(row, 3, QTableWidgetItem(gasto["fecha"].strftime('%Y-%m-%d')))

    def _add_gasto(self):
        # A simple dialog to get expense description and amount
        from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QPushButton, QMessageBox
        class AddGastoDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Añadir Gasto")
                layout = QFormLayout(self)

                self.descripcion_input = QLineEdit()
                layout.addRow("Descripción del Gasto:", self.descripcion_input)

                self.cantidad_input = QDoubleSpinBox()
                self.cantidad_input.setRange(0.0, 999999999999.99)
                self.cantidad_input.setDecimals(0)
                self.cantidad_input.setPrefix("$ ")
                self.cantidad_input.setGroupSeparatorShown(True)
                layout.addRow("Cantidad:", self.cantidad_input)

                self.fecha_input = QDateEdit(QDate.currentDate())
                self.fecha_input.setCalendarPopup(True)
                layout.addRow("Fecha del Gasto:", self.fecha_input)

                btn_guardar = QPushButton("Guardar")
                btn_guardar.clicked.connect(self.accept)
                layout.addRow(btn_guardar)

            def get_gasto_data(self):
                return {
                    "descripcion": self.descripcion_input.text(),
                    "cantidad": self.cantidad_input.value(),
                    "fecha": self.fecha_input.date().toPython()
                }

        dialog = AddGastoDialog(self)
        if dialog.exec():
            gasto_data = dialog.get_gasto_data()
            if not gasto_data["descripcion"].strip():
                QMessageBox.warning(self, "Error", "La descripción del gasto no puede estar vacía.")
                return
            if gasto_data["cantidad"] <= 0:
                QMessageBox.warning(self, "Error", "La cantidad del gasto debe ser mayor que cero.")
                return
            self.assigned_gastos.append(gasto_data)
            self.refresh_gastos_table()

    def _remove_gasto(self):
        selected_rows = self.table_gastos.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Quitar Gasto", "Seleccione un gasto de la tabla para quitar.")
            return
        
        for index in sorted(selected_rows, reverse=True):
            del self.assigned_gastos[index.row()]
        self.refresh_gastos_table()
        QMessageBox.information(self, "Quitar Gasto", "Gasto quitado de la lista temporal.")

    def refresh_ingresos_table(self):
        self.table_ingresos.setRowCount(0)
        for row, ingreso in enumerate(self.assigned_ingresos):
            self.table_ingresos.insertRow(row)
            self.table_ingresos.setItem(row, 0, QTableWidgetItem(str(ingreso.get("id", "")))) # Ingreso ID if exists
            self.table_ingresos.setItem(row, 1, QTableWidgetItem(ingreso["descripcion"]))
            self.table_ingresos.setItem(row, 2, QTableWidgetItem(f"${ingreso['cantidad']:.2f}"))
            self.table_ingresos.setItem(row, 3, QTableWidgetItem(ingreso["fecha"].strftime('%Y-%m-%d')))

    def _add_ingreso(self):
        from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QPushButton, QMessageBox, QDateEdit
        from PySide6.QtCore import QDate
        class AddIngresoDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Añadir Ingreso")
                layout = QFormLayout(self)

                self.descripcion_input = QLineEdit()
                layout.addRow("Descripción del Ingreso:", self.descripcion_input)

                self.cantidad_input = QDoubleSpinBox()
                self.cantidad_input.setRange(0.0, 999999999999.99)
                self.cantidad_input.setDecimals(0)
                self.cantidad_input.setPrefix("$ ")
                self.cantidad_input.setGroupSeparatorShown(True)
                layout.addRow("Cantidad:", self.cantidad_input)

                self.fecha_input = QDateEdit(QDate.currentDate())
                self.fecha_input.setCalendarPopup(True)
                layout.addRow("Fecha del Ingreso:", self.fecha_input)

                btn_guardar = QPushButton("Guardar")
                btn_guardar.clicked.connect(self.accept)
                layout.addRow(btn_guardar)

            def get_ingreso_data(self):
                return {
                    "descripcion": self.descripcion_input.text(),
                    "cantidad": self.cantidad_input.value(),
                    "fecha": self.fecha_input.date().toPython()
                }

        dialog = AddIngresoDialog(self)
        if dialog.exec():
            ingreso_data = dialog.get_ingreso_data()
            if not ingreso_data["descripcion"].strip():
                QMessageBox.warning(self, "Error", "La descripción del ingreso no puede estar vacía.")
                return
            if ingreso_data["cantidad"] <= 0:
                QMessageBox.warning(self, "Error", "La cantidad del ingreso debe ser mayor que cero.")
                return
            self.assigned_ingresos.append(ingreso_data)
            self.refresh_ingresos_table()

    def _remove_ingreso(self):
        selected_rows = self.table_ingresos.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Quitar Ingreso", "Seleccione un ingreso de la tabla para quitar.")
            return
        
        for index in sorted(selected_rows, reverse=True):
            del self.assigned_ingresos[index.row()]
        self.refresh_ingresos_table()
        QMessageBox.information(self, "Quitar Ingreso", "Ingreso quitado de la lista temporal.")


    def cargar_datos(self):
        session = get_session()
        proyecto = session.query(Proyecto).filter_by(id=self.proyecto_id).first()
        if not proyecto:
            QMessageBox.warning(self, "Error", "Proyecto no encontrado.")
            session.close()
            self.reject()
            return

        self.nombre.setText(proyecto.nombre)
        self.cliente.setText(proyecto.cliente or "")
        self.descripcion.setPlainText(proyecto.descripcion or "")
        fecha_inicio = proyecto.fecha_inicio or datetime.date.today()
        self.fecha_inicio.setDate(QDate(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day))

        fecha_fin = proyecto.fecha_fin or datetime.date.today()
        self.fecha_fin.setDate(QDate(fecha_fin.year, fecha_fin.month, fecha_fin.day))

        self.estado.setCurrentText(proyecto.estado or "Planificado")
        self.presupuesto.setValue(proyecto.presupuesto or 0.0)
        self.anticipo.setValue(proyecto.anticipo or 0.0)

        # Load assigned employees
        self.assigned_empleados = []
        for pe in proyecto.empleados_asignados:
            # Skip if empleado has been deleted
            if pe.empleado is None:
                continue
            self.assigned_empleados.append({
                "empleado_id": pe.empleado.id,
                "nombre_empleado": f"{pe.empleado.nombre} {pe.empleado.apellidos}",
                # Removed: "salario_hora": pe.empleado.salario, # Assuming empleado.salario is per hour
                # Removed: "horas": pe.horas,
                "proyecto_empleado_id": pe.id # Keep track of association ID
            })
        self.refresh_empleados_table()

        # Load assigned materials
        self.assigned_materiales = []
        for pm in proyecto.materiales_asignados:
            # Skip if material has been deleted
            if pm.material is None:
                continue
            self.assigned_materiales.append({
                "material_id": pm.material.id,
                "nombre_material": pm.material.nombre,
                "cantidad": pm.cantidad,
                # Removed: "costo": pm.costo,
                "proyecto_material_id": pm.id # Keep track of association ID
            })
        self.refresh_materiales_table()

        # Load assigned equipment
        self.assigned_equipos = []
        for peq in proyecto.equipos_asignados:
            # Skip if equipo has been deleted
            if peq.equipo is None:
                continue
            self.assigned_equipos.append({
                "equipo_id": peq.equipo.id,
                "nombre_equipo": peq.equipo.nombre,
                "cantidad": peq.cantidad, # Load assigned quantity
                "costo_uso": 0.0, # As per new spec, costo_uso is 0.0 and not explicitly stored/managed here
                "proyecto_equipo_id": peq.id # Keep track of association ID
            })
        self.refresh_equipos_table()

        # Load assigned expenses
        self.assigned_gastos = []
        for g in proyecto.gastos_registrados:
            self.assigned_gastos.append({
                "id": g.id,
                "descripcion": g.descripcion,
                "cantidad": g.cantidad,
                "fecha": g.fecha
            })
        self.refresh_gastos_table()

        # Load assigned incomes
        self.assigned_ingresos = []
        for i in proyecto.ingresos_registrados:
            self.assigned_ingresos.append({
                "id": i.id,
                "descripcion": i.descripcion,
                "cantidad": i.cantidad,
                "fecha": i.fecha
            })
        self.refresh_ingresos_table()

        session.close()

    def guardar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre del proyecto es obligatorio.")
            return
        if not self.fecha_inicio.date().isValid():
            QMessageBox.warning(self, "Error", "La fecha de inicio es obligatoria.")
            return
        if not self.fecha_fin.date().isValid():
            QMessageBox.warning(self, "Error", "La fecha de fin es obligatoria.")
            return
        if self.fecha_inicio.date() > self.fecha_fin.date():
            QMessageBox.warning(self, "Error", "La fecha de inicio no puede ser posterior a la fecha de fin.")
            return

        session = get_session()

        # Validar proyecto duplicado
        existing_proyecto = session.query(Proyecto).filter_by(nombre=self.nombre.text().strip()).first()
        if existing_proyecto and (not self.proyecto_id or existing_proyecto.id != self.proyecto_id):
            QMessageBox.warning(self, "Error", "Ya existe un proyecto con este nombre.")
            session.close()
            return

        proyecto = None
        prev_estado = None
        if self.proyecto_id:
            proyecto = session.query(Proyecto).filter_by(id=self.proyecto_id).first()
            if not proyecto: # Safeguard
                QMessageBox.warning(self, "Error", "Proyecto no encontrado.")
                session.close()
                self.reject()
                return
            prev_estado = proyecto.estado
        else:
            proyecto = Proyecto()

        # Update basic project fields
        proyecto.nombre = self.nombre.text().strip()
        proyecto.cliente = self.cliente.text().strip()
        proyecto.descripcion = self.descripcion.toPlainText().strip()
        proyecto.fecha_inicio = self.fecha_inicio.date().toPython()
        proyecto.fecha_fin = self.fecha_fin.date().toPython()
        proyecto.estado = self.estado.currentText()
        proyecto.presupuesto = self.presupuesto.value()
        proyecto.anticipo = self.anticipo.value()
        
        # Calculate initial cost_total (will be refined with associations)
        proyecto.costo_total = 0.0

        session.add(proyecto)
        session.flush() # Flush to get project.id for new projects

        # Handle Employees (nomina)
        # First, remove old assignments if editing
        if self.proyecto_id:
            session.query(ProyectoEmpleado).filter_by(proyecto_id=self.proyecto_id).delete()
        for emp_data in self.assigned_empleados:
            empleado = session.query(Empleado).filter_by(id=emp_data["empleado_id"]).first()
            if empleado:
                pe = ProyectoEmpleado(
                    proyecto_id=proyecto.id,
                    empleado_id=emp_data["empleado_id"],
                    horas=0, # Default to 0 as hours are no longer collected via UI for assignment
                    costo=0.0 # Default to 0.0 as per user's clarification for direct linking
                )
                session.add(pe)
                # proyecto.costo_total += pe.costo # REMOVED: Not adding employee cost to project total as per user
            else:
                QMessageBox.warning(self, "Error", f"Empleado {emp_data['nombre_empleado']} no encontrado para asignación.")
        
        # Handle Materials (deduction from stock)
        # First, restore quantities for old assignments if editing
        if self.proyecto_id:
            old_pms = session.query(ProyectoMaterial).filter_by(proyecto_id=self.proyecto_id).all()
            for opm in old_pms:
                material = session.query(Material).filter_by(id=opm.material_id).first()
                if material:
                    material.cantidad += opm.cantidad # Restore old quantity
            session.query(ProyectoMaterial).filter_by(proyecto_id=self.proyecto_id).delete()

        # Aggregate assigned material quantities
        aggregated_materiales = {}
        for mat_data in self.assigned_materiales:
            material_id = mat_data["material_id"]
            if material_id not in aggregated_materiales:
                aggregated_materiales[material_id] = {
                    "nombre_material": mat_data["nombre_material"],
                    "cantidad": 0
                }
            aggregated_materiales[material_id]["cantidad"] += mat_data["cantidad"]

        for material_id, agg_data in aggregated_materiales.items():
            material = session.query(Material).filter_by(id=material_id).first()
            if material:
                # Deduct assigned quantity from stock
                material.cantidad -= agg_data["cantidad"]
                pm = ProyectoMaterial(
                    proyecto_id=proyecto.id,
                    material_id=material_id,
                    cantidad=agg_data["cantidad"], # Use aggregated quantity
                    costo=0.0 # Set cost to 0.0 as per user's clarification ("sin costos")
                )
                session.add(pm)
                # proyecto.costo_total += pm.costo # REMOVED: Not adding material cost to project total as per user
            else:
                QMessageBox.warning(self, "Error", f"Material {agg_data['nombre_material']} no encontrado para asignación.")

        # Handle Equipment (update availability)
        # First, restore quantities for old assignments if editing
        if self.proyecto_id:
            old_peqs = session.query(ProyectoEquipo).filter_by(proyecto_id=self.proyecto_id).all()
            for opeq in old_peqs:
                equipo = session.query(Equipo).filter_by(id=opeq.equipo_id).first()
                if equipo:
                    equipo.cantidad += opeq.cantidad # Restore old quantity to stock
                    # Check if all units are restored and update status if applicable
                    # This implies a more complex state management where 'estado' reflects availability
                    # For now, if all are returned, set to 'Disponible'
                    # Or, better, simply remove the "En uso" state and rely on quantity tracking
                    # I will assume equipo.cantidad is the source of truth for availability.
            session.query(ProyectoEquipo).filter_by(proyecto_id=self.proyecto_id).delete()

        # Aggregate assigned equipment quantities
        aggregated_equipos = {}
        for eq_data in self.assigned_equipos:
            equipo_id = eq_data["equipo_id"]
            if equipo_id not in aggregated_equipos:
                aggregated_equipos[equipo_id] = {
                    "nombre_equipo": eq_data["nombre_equipo"],
                    "cantidad": 0
                }
            aggregated_equipos[equipo_id]["cantidad"] += eq_data["cantidad"]

        # Prepare to track newly created ProyectoEquipo records so we can adjust them if some units are returned
        new_peqs = {}
        for equipo_id, agg_data in aggregated_equipos.items():
            equipo = session.query(Equipo).filter_by(id=equipo_id).first()
            if equipo:
                # Deduct assigned quantity from stock
                equipo.cantidad -= agg_data["cantidad"]

                peq = ProyectoEquipo(
                    proyecto_id=proyecto.id,
                    equipo_id=equipo_id,
                    cantidad=agg_data["cantidad"] # Use aggregated quantity
                )
                session.add(peq)
                # Keep reference for later adjustment if project is completed and some units are returned
                new_peqs[equipo_id] = peq
        
        # Handle Gastos (Expenses)
        if self.proyecto_id:
            # Remove existing expenses for this project before adding new ones
            session.query(Gasto).filter_by(proyecto_id=self.proyecto_id).delete()
        
        for gasto_data in self.assigned_gastos:
            gasto = Gasto(
                proyecto_id=proyecto.id,
                descripcion=gasto_data["descripcion"],
                cantidad=gasto_data["cantidad"],
                fecha=gasto_data["fecha"]
            )
            session.add(gasto)
            proyecto.costo_total += gasto.cantidad # Add expense amount to project total cost

        # Handle Ingresos (Incomes)
        total_ingresos_adicionales = 0.0
        if self.proyecto_id:
            # Remove existing incomes for this project before adding new ones
            session.query(IngresoProyecto).filter_by(proyecto_id=self.proyecto_id).delete()
        
        for ingreso_data in self.assigned_ingresos:
            ingreso = IngresoProyecto(
                proyecto_id=proyecto.id,
                descripcion=ingreso_data["descripcion"],
                cantidad=ingreso_data["cantidad"],
                fecha=ingreso_data["fecha"]
            )
            session.add(ingreso)
            total_ingresos_adicionales += ingreso.cantidad # Sum additional incomes

        # Note: The 'ganancias_totales' (anticipo + ingresos) will be calculated dynamically for display,
        # not stored directly as a column, to ensure it's always up-to-date.
        # proyecto.anticipo is already part of the project.
        # No need to add total_ingresos_adicionales to a stored project.ganancias_totales here.
        # This will be handled in FinanzasService.

        # If the project is transitioning to 'Completado', show a dialog to return items to stock
        try:
            if proyecto.estado == "Completado" and prev_estado != "Completado":
                from app.views.return_items_dialog import ReturnItemsDialog
                dialog = ReturnItemsDialog(aggregated_equipos, aggregated_materiales, parent=self)
                if dialog.exec():
                    returns = dialog.get_returns()
                    total_lost_value = 0.0
                    
                    # Handle Equipment returns
                    eq_returns = returns.get("equipos", {})
                    for equipo_id, agg in aggregated_equipos.items():
                        assigned_qty = agg.get("cantidad", 0)
                        returned_qty = eq_returns.get(equipo_id, 0)
                        # Update stock for returned units
                        if returned_qty > 0:
                            equipo = session.query(Equipo).filter_by(id=equipo_id).first()
                            if equipo:
                                equipo.cantidad += returned_qty
                        # Update ProyectoEquipo association
                        peq = session.query(ProyectoEquipo).filter_by(proyecto_id=proyecto.id, equipo_id=equipo_id).first()
                        if peq:
                            if returned_qty >= assigned_qty:
                                session.delete(peq)
                            else:
                                peq.cantidad = assigned_qty - returned_qty
                        # Calculate lost units and their value
                        lost_qty = max(0, assigned_qty - returned_qty)
                        if lost_qty > 0:
                            equipo_for_value = session.query(Equipo).filter_by(id=equipo_id).first()
                            unit_value = float(getattr(equipo_for_value, 'valor_unitario', 0.0) or 0.0)
                            total_lost_value += lost_qty * unit_value
                    
                    # Handle Material returns
                    mat_returns = returns.get("materiales", {})
                    for material_id, agg in aggregated_materiales.items():
                        assigned_qty = agg.get("cantidad", 0)
                        returned_qty = mat_returns.get(material_id, 0)
                        # Update stock for returned units
                        if returned_qty > 0:
                            material = session.query(Material).filter_by(id=material_id).first()
                            if material:
                                material.cantidad += returned_qty
                        # Update ProyectoMaterial association
                        pm = session.query(ProyectoMaterial).filter_by(proyecto_id=proyecto.id, material_id=material_id).first()
                        if pm:
                            if returned_qty >= assigned_qty:
                                session.delete(pm)
                            else:
                                pm.cantidad = assigned_qty - returned_qty

                    # If any lost value, create a Gasto record
                    if total_lost_value > 0:
                        gasto = Gasto(
                            proyecto_id=proyecto.id,
                            descripcion="Equipos perdidos",
                            cantidad=total_lost_value,
                            fecha=datetime.date.today()
                        )
                        session.add(gasto)
                        proyecto.costo_total = (proyecto.costo_total or 0.0) + total_lost_value
        except Exception as e:
            # If anything goes wrong with the dialog logic, continue and commit to avoid blocking save.
            print(f"Error en devolución de elementos: {e}")
            pass

        session.commit()
        session.close()
        self.financial_data_changed.emit() # Emit signal after successful save
        self.accept()
