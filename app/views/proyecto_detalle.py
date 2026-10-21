from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,QPushButton,
    QTableWidget, QTableWidgetItem, QTabWidget, QWidget, QHeaderView,
    QAbstractItemView, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from app.database.db import get_session
from app.models.proyecto import Proyecto
from app.models.proyecto_empleado import ProyectoEmpleado
from app.models.proyecto_material import ProyectoMaterial
from app.models.proyecto_equipo import ProyectoEquipo
from app.models.empleado import Empleado
from app.models.material import Material
from app.models.equipo import Equipo
from app.models.gasto import Gasto # Import Gasto model
from app.models.ingreso_proyecto import IngresoProyecto # Import IngresoProyecto model
from app.utils.formatting import format_cop
import datetime

class ProyectoDetalleView(QDialog):
    def __init__(self, proyecto_id, parent=None):
        super().__init__(parent)
        self.proyecto_id = proyecto_id
        self.setWindowTitle("Detalles del Proyecto")
        self.resize(800, 600)

        self.init_ui()
        self.load_project_details()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Scroll Area for Project Info
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        project_info_widget = QWidget()
        self.project_info_layout = QVBoxLayout(project_info_widget)
        scroll_area.setWidget(project_info_widget)
        main_layout.addWidget(scroll_area)

        # Basic Project Details (using QLabel for display)
        self.lbl_nombre = QLabel("<b>Nombre:</b> ")
        self.lbl_cliente = QLabel("<b>Cliente:</b> ")
        self.lbl_descripcion = QLabel("<b>Descripción:</b> ")
        self.lbl_fechas = QLabel("<b>Fechas:</b> ")
        self.lbl_estado = QLabel("<b>Estado:</b> ")
        self.lbl_presupuesto = QLabel("<b>Presupuesto:</b> ")
        self.lbl_anticipo = QLabel("<b>Anticipo:</b> ")
        self.lbl_costo_total = QLabel("<b>Costo Total Calculado:</b> ")
        self.lbl_gastos_totales = QLabel("<b>Gastos Totales:</b> ") # New Label for total expenses
        self.lbl_balance_anticipo = QLabel("<b>Balance vs Anticipo:</b> ") # New Label for balance against advance
        self.lbl_balance_presupuesto = QLabel("<b>Balance vs Presupuesto:</b> ") # New Label for balance against budget
        self.lbl_ingresos_adicionales = QLabel("<b>Ingresos Adicionales:</b> ") # New Label for additional income
        self.lbl_ganancia_proyecto = QLabel("<b>Ganancia del Proyecto:</b> ") # New Label for project profit

        self.project_info_layout.addWidget(self.lbl_nombre)
        self.project_info_layout.addWidget(self.lbl_cliente)
        self.project_info_layout.addWidget(self.lbl_descripcion)
        self.project_info_layout.addWidget(self.lbl_fechas)
        self.project_info_layout.addWidget(self.lbl_estado)
        self.project_info_layout.addWidget(self.lbl_presupuesto)
        self.project_info_layout.addWidget(self.lbl_anticipo)
        self.project_info_layout.addWidget(self.lbl_costo_total)
        self.project_info_layout.addWidget(self.lbl_gastos_totales) # Add to layout
        self.project_info_layout.addWidget(self.lbl_balance_anticipo) # Add to layout
        self.project_info_layout.addWidget(self.lbl_balance_presupuesto) # Add to layout
        self.project_info_layout.addWidget(self.lbl_ingresos_adicionales) # Add to layout
        self.project_info_layout.addWidget(self.lbl_ganancia_proyecto) # Add to layout
        self.project_info_layout.addStretch()

        # Tabs for Associations
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_empleados_tab(), "Empleados Asignados")
        self.tabs.addTab(self._create_materiales_tab(), "Materiales Asignados")
        self.tabs.addTab(self._create_equipos_tab(), "Equipos Asignados")
        self.tabs.addTab(self._create_gastos_tab(), "Gastos Registrados") # New tab for Expenses
        self.tabs.addTab(self._create_ingresos_tab(), "Ingresos Registrados") # New tab for Incomes
        main_layout.addWidget(self.tabs)

        # Close Button
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        main_layout.addWidget(btn_close)

    def _create_empleados_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.table_empleados = QTableWidget()
        self.table_empleados.setColumnCount(2)
        self.table_empleados.setHorizontalHeaderLabels(["ID", "Nombre Empleado"])
        self.table_empleados.setColumnHidden(0, True)
        self.table_empleados.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_empleados.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_empleados.setAlternatingRowColors(True)
        self.table_empleados.verticalHeader().setDefaultSectionSize(40)
        self.table_empleados.verticalHeader().setVisible(False)
        self.table_empleados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_empleados)
        return tab

    def _create_materiales_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.table_materiales = QTableWidget()
        self.table_materiales.setColumnCount(3)
        self.table_materiales.setHorizontalHeaderLabels(["ID", "Nombre Material", "Cantidad"])
        self.table_materiales.setColumnHidden(0, True)
        self.table_materiales.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_materiales.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_materiales.setAlternatingRowColors(True)
        self.table_materiales.verticalHeader().setDefaultSectionSize(40)
        self.table_materiales.verticalHeader().setVisible(False)
        self.table_materiales.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_materiales)
        return tab

    def _create_equipos_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.table_equipos = QTableWidget()
        self.table_equipos.setColumnCount(3) # Changed from 5 to 3 columns
        self.table_equipos.setHorizontalHeaderLabels(["ID", "Nombre Equipo", "Cantidad"]) # Changed headers
        self.table_equipos.setColumnHidden(0, True)
        self.table_equipos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_equipos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_equipos.setAlternatingRowColors(True)
        self.table_equipos.verticalHeader().setDefaultSectionSize(40)
        self.table_equipos.verticalHeader().setVisible(False)
        self.table_equipos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_equipos)
        return tab

    def _create_gastos_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.table_gastos = QTableWidget()
        self.table_gastos.setColumnCount(3)
        self.table_gastos.setHorizontalHeaderLabels(["Descripción", "Cantidad", "Fecha"])
        self.table_gastos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_gastos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_gastos.setAlternatingRowColors(True)
        self.table_gastos.verticalHeader().setDefaultSectionSize(40)
        self.table_gastos.verticalHeader().setVisible(False)
        self.table_gastos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_gastos)
        return tab

    def _create_ingresos_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.table_ingresos = QTableWidget()
        self.table_ingresos.setColumnCount(3) # Descripción, Cantidad, Fecha
        self.table_ingresos.setHorizontalHeaderLabels(["Descripción", "Cantidad", "Fecha"])
        self.table_ingresos.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_ingresos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_ingresos.setAlternatingRowColors(True)
        self.table_ingresos.verticalHeader().setDefaultSectionSize(40)
        self.table_ingresos.verticalHeader().setVisible(False)
        self.table_ingresos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_ingresos)
        return tab

    def load_project_details(self):
        session = get_session()
        proyecto = session.query(Proyecto).filter_by(id=self.proyecto_id).first()
        if not proyecto:
            QMessageBox.warning(self, "Error", "Proyecto no encontrado para detalles.")
            session.close()
            self.reject()
            return

        self.lbl_nombre.setText(f"<b>Nombre:</b> {proyecto.nombre}")
        self.lbl_cliente.setText(f"<b>Cliente:</b> {proyecto.cliente or 'N/A'}")
        self.lbl_descripcion.setText(f"<b>Descripción:</b> {proyecto.descripcion or 'N/A'}")
        self.lbl_fechas.setText(f"<b>Fechas:</b> {proyecto.fecha_inicio.strftime('%Y-%m-%d')} a {proyecto.fecha_fin.strftime('%Y-%m-%d')}")
        self.lbl_estado.setText(f"<b>Estado:</b> {proyecto.estado}")
        self.lbl_presupuesto.setText(f"<b>Presupuesto:</b> $ {format_cop(proyecto.presupuesto)}")
        self.lbl_anticipo.setText(f"<b>Anticipo:</b> $ {format_cop(proyecto.anticipo)}")
        self.lbl_costo_total.setText(f"<b>Costo Total Calculado (Gastos):</b> $ {format_cop(proyecto.costo_total)}")

        # Load assigned employees
        self.table_empleados.setRowCount(0)
        row = 0
        for pe in proyecto.empleados_asignados:
            # Skip if empleado has been deleted
            if pe.empleado is None:
                continue
            self.table_empleados.insertRow(row)
            self.table_empleados.setItem(row, 0, QTableWidgetItem(str(pe.empleado.id)))
            self.table_empleados.setItem(row, 1, QTableWidgetItem(f"{pe.empleado.nombre} {pe.empleado.apellidos}"))
            row += 1

        # Load assigned materials
        self.table_materiales.setRowCount(0)
        aggregated_materiales_display = {}
        for pm in proyecto.materiales_asignados:
            # Skip if material has been deleted
            if pm.material is None:
                continue
            material_id = pm.material.id
            if material_id not in aggregated_materiales_display:
                aggregated_materiales_display[material_id] = {
                    "nombre_material": pm.material.nombre,
                    "cantidad": 0
                }
            aggregated_materiales_display[material_id]["cantidad"] += pm.cantidad
        
        for row, (material_id, agg_data) in enumerate(aggregated_materiales_display.items()):
            self.table_materiales.insertRow(row)
            self.table_materiales.setItem(row, 0, QTableWidgetItem(str(material_id)))
            self.table_materiales.setItem(row, 1, QTableWidgetItem(agg_data["nombre_material"]))
            self.table_materiales.setItem(row, 2, QTableWidgetItem(str(agg_data["cantidad"])))

        # Load assigned equipment
        self.table_equipos.setRowCount(0)
        # Calculate total assigned quantity for each equipment to display correctly
        aggregated_equipos_display = {}
        for peq in proyecto.equipos_asignados:
            # Skip if equipo has been deleted
            if peq.equipo is None:
                continue
            equipo_id = peq.equipo.id
            if equipo_id not in aggregated_equipos_display:
                aggregated_equipos_display[equipo_id] = {
                    "nombre_equipo": peq.equipo.nombre,
                    "cantidad": 0
                }
            aggregated_equipos_display[equipo_id]["cantidad"] += peq.cantidad
        
        for row, (equipo_id, agg_data) in enumerate(aggregated_equipos_display.items()):
            self.table_equipos.insertRow(row)
            self.table_equipos.setItem(row, 0, QTableWidgetItem(str(equipo_id)))
            self.table_equipos.setItem(row, 1, QTableWidgetItem(agg_data["nombre_equipo"]))
            self.table_equipos.setItem(row, 2, QTableWidgetItem(str(agg_data["cantidad"])))
        
        # Load registered expenses
        self.table_gastos.setRowCount(0)
        total_gastos = 0.0
        for row, gasto in enumerate(proyecto.gastos_registrados):
            self.table_gastos.insertRow(row)
            self.table_gastos.setItem(row, 0, QTableWidgetItem(gasto.descripcion))
            self.table_gastos.setItem(row, 1, QTableWidgetItem(f"$ {format_cop(gasto.cantidad)}"))
            self.table_gastos.setItem(row, 2, QTableWidgetItem(gasto.fecha.strftime('%Y-%m-%d')))
            total_gastos += gasto.cantidad
        
        self.lbl_gastos_totales.setText(f"<b>Gastos Totales:</b> $ {format_cop(total_gastos)}")

        # Load registered incomes
        self.table_ingresos.setRowCount(0)
        total_ingresos_adicionales = 0.0
        for row, ingreso in enumerate(proyecto.ingresos_registrados):
            self.table_ingresos.insertRow(row)
            self.table_ingresos.setItem(row, 0, QTableWidgetItem(ingreso.descripcion))
            self.table_ingresos.setItem(row, 1, QTableWidgetItem(f"$ {format_cop(ingreso.cantidad)}"))
            self.table_ingresos.setItem(row, 2, QTableWidgetItem(ingreso.fecha.strftime('%Y-%m-%d')))
            total_ingresos_adicionales += ingreso.cantidad
        
        self.lbl_ingresos_adicionales.setText(f"<b>Ingresos Adicionales:</b> $ {format_cop(total_ingresos_adicionales)}")

        # Calculate and display financial balances
        balance_anticipo = proyecto.anticipo - total_gastos
        self.lbl_balance_anticipo.setText(f"<b>Balance vs Anticipo:</b> $ {format_cop(balance_anticipo)}")
        if balance_anticipo < 0:
            self.lbl_balance_anticipo.setStyleSheet("color: red")
        else:
            self.lbl_balance_anticipo.setStyleSheet("")

        # proyecto.costo_total now only includes Gasto.cantidad
        balance_presupuesto = proyecto.presupuesto - proyecto.costo_total # Original Costo Total was sum of all costs, now it's just expenses
        self.lbl_balance_presupuesto.setText(f"<b>Balance vs Presupuesto:</b> $ {format_cop(balance_presupuesto)}")
        if balance_presupuesto < 0:
            self.lbl_balance_presupuesto.setStyleSheet("color: red")
        else:
            self.lbl_balance_presupuesto.setStyleSheet("")

        # Calculate total project profit (Anticipo + Ingresos Adicionales - Gastos Totales)
        total_ganancias = proyecto.anticipo + total_ingresos_adicionales - total_gastos
        
        # Conditional display of profit
        if proyecto.estado == "Completado":
            self.lbl_ganancia_proyecto.setText(f"<b>Ganancia del Proyecto:</b> $ {format_cop(total_ganancias)}")
            if total_ganancias < 0:
                self.lbl_ganancia_proyecto.setStyleSheet("color: red")
            else:
                self.lbl_ganancia_proyecto.setStyleSheet("color: green")
        else:
            self.lbl_ganancia_proyecto.setText("<b>Ganancia del Proyecto:</b> Disponible al completar")
            self.lbl_ganancia_proyecto.setStyleSheet("")
        
        session.close()
