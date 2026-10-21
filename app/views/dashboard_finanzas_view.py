# app/views/dashboard_finanzas_view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QLineEdit, QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QDate
from app.services.finanzas_service import FinanzasService
from app.database.db import get_session
from datetime import date, timedelta
from app.utils.formatting import format_cop

class DashboardFinanzasView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard Financiero")
        self.resize(1600, 900)

        self.finanzas_service = None # Initialize to None, will be set in refresh_dashboard
        self.current_start_date = None
        self.current_end_date = None

        self._init_ui()
        self.refresh_dashboard() # Call refresh_dashboard to load initial data

    def refresh_dashboard(self):
        # Close existing session if it exists
        if self.finanzas_service:
            self.finanzas_service.close_session()
        # Create a new session for fresh data
        self.finanzas_service = FinanzasService(get_session())
        self.project_combo.clear() # Clear existing projects
        self.project_combo.addItem("Seleccione un proyecto...", -1) # Default item
        self._load_projects_to_combo()
        self._load_data()
        self._update_project_finances()
        self._filter_expenses_by_description()


    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- Date Filter Section ---
        date_filter_layout = QHBoxLayout()
        self.btn_filter_week = QPushButton("Esta Semana")
        self.btn_filter_month = QPushButton("Este Mes")
        self.btn_filter_year = QPushButton("Este Año")
        self.btn_filter_all = QPushButton("Todo el Tiempo")
        
        date_filter_layout.addWidget(self.btn_filter_week)
        date_filter_layout.addWidget(self.btn_filter_month)
        date_filter_layout.addWidget(self.btn_filter_year)
        date_filter_layout.addWidget(self.btn_filter_all)
        date_filter_layout.addStretch()
        main_layout.addLayout(date_filter_layout)

        # --- General Balance Section ---
        general_balance_group = QGroupBox("Balance General de la Empresa")
        general_balance_layout = QFormLayout()
        self.lbl_total_income = QLabel("Ingresos Totales: $0.00")
        self.lbl_total_expenses = QLabel("Gastos Totales: $0.00")
        self.lbl_profit = QLabel("Saldo Disponible (Ganancia): $0.00")
        general_balance_layout.addRow(self.lbl_total_income)
        general_balance_layout.addRow(self.lbl_total_expenses)
        general_balance_layout.addRow(self.lbl_profit)
        general_balance_group.setLayout(general_balance_layout)
        main_layout.addWidget(general_balance_group)

        # --- Top 3 Profitable Projects Section ---
        top_projects_group = QGroupBox("Top 3 Proyectos Más Rentables")
        self.top_projects_table = QTableWidget(3, 3) # Rows for top 3, cols for Name, Income, Expenses, Profit
        self.top_projects_table.setHorizontalHeaderLabels(["Proyecto", "Ganancia", "Ingresos", "Gastos"])
        self.top_projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.top_projects_table.setEditTriggers(QTableWidget.NoEditTriggers) # Make table read-only
        top_projects_group.setLayout(QVBoxLayout())
        top_projects_group.layout().addWidget(self.top_projects_table)
        main_layout.addWidget(top_projects_group)

        # --- Project Specific Section ---
        project_specific_group = QGroupBox("Finanzas por Proyecto")
        project_specific_layout = QFormLayout()
        
        self.project_combo = QComboBox()
        self.project_combo.addItem("Seleccione un proyecto...", -1) # Default item
        
        project_specific_layout.addRow("Proyecto:", self.project_combo)
        self.lbl_project_income = QLabel("Ingresos del Proyecto: $0.00")
        self.lbl_project_expenses = QLabel("Gastos del Proyecto: $0.00")
        self.lbl_project_profit = QLabel("Rentabilidad del Proyecto: $0.00")
        project_specific_layout.addRow(self.lbl_project_income)
        project_specific_layout.addRow(self.lbl_project_expenses)
        project_specific_layout.addRow(self.lbl_project_profit)
        project_specific_group.setLayout(project_specific_layout)
        main_layout.addWidget(project_specific_group)

        # --- Expense Description Filter Section ---
        expense_filter_group = QGroupBox("Filtrar Gastos por Descripción")
        expense_filter_layout = QHBoxLayout()
        self.txt_expense_description = QLineEdit()
        self.txt_expense_description.setPlaceholderText("Ej: nomina, materiales")
        self.btn_filter_expense_desc = QPushButton("Buscar Gastos")
        self.lbl_expense_desc_total = QLabel("Total Gastos por Descripción: $0.00")
        
        expense_filter_layout.addWidget(self.txt_expense_description)
        expense_filter_layout.addWidget(self.btn_filter_expense_desc)
        expense_filter_group.setLayout(QVBoxLayout())
        expense_filter_group.layout().addLayout(expense_filter_layout)
        expense_filter_group.layout().addWidget(self.lbl_expense_desc_total)
        main_layout.addWidget(expense_filter_group)

        main_layout.addStretch() # Push everything to the top

        self._connect_signals()
        # self._load_projects_to_combo() # Removed: Called by refresh_dashboard after service init

    def _connect_signals(self):
        self.btn_filter_week.clicked.connect(lambda: self._set_date_range("week"))
        self.btn_filter_month.clicked.connect(lambda: self._set_date_range("month"))
        self.btn_filter_year.clicked.connect(lambda: self._set_date_range("year"))
        self.btn_filter_all.clicked.connect(lambda: self._set_date_range("all"))
        self.project_combo.currentIndexChanged.connect(self._update_project_finances)
        self.btn_filter_expense_desc.clicked.connect(self._filter_expenses_by_description)

    def _set_date_range(self, period):
        today = date.today()
        if period == "week":
            self.current_start_date = today - timedelta(days=today.weekday()) # Monday of current week
            self.current_end_date = today + timedelta(days=6 - today.weekday()) # Sunday of current week
        elif period == "month":
            self.current_start_date = today.replace(day=1)
            next_month = today.replace(day=28) + timedelta(days=4)  # Go to the 4th day of next month
            self.current_end_date = next_month - timedelta(days=next_month.day) # Last day of current month
        elif period == "year":
            self.current_start_date = date(today.year, 1, 1)
            self.current_end_date = date(today.year, 12, 31)
        else: # "all"
            self.current_start_date = None
            self.current_end_date = None
        
        self._load_data()
        self._update_project_finances() # Update project specific data as well
        self._filter_expenses_by_description() # Update expenses by description

    def _load_projects_to_combo(self):
        projects = self.finanzas_service.get_all_projects()
        for project in projects:
            self.project_combo.addItem(project.nombre, project.id)

    def _load_data(self):
        # Load General Balance
        balance_data = self.finanzas_service.get_company_general_balance(self.current_start_date, self.current_end_date)
        self.lbl_total_income.setText(f"Ingresos Totales: $ {format_cop(balance_data['total_income'])}")
        self.lbl_total_expenses.setText(f"Gastos Totales: $ {format_cop(balance_data['total_expenses'])}")
        self.lbl_profit.setText(f"Saldo Disponible (Ganancia): $ {format_cop(balance_data['profit'])}")

        # Load Top 3 Profitable Projects
        top_projects = self.finanzas_service.get_top_profitable_projects(
            limit=3,
            start_date=self.current_start_date,
            end_date=self.current_end_date
        )
        self.top_projects_table.setRowCount(len(top_projects))
        for i, item in enumerate(top_projects):
            project_id = item["proyecto"].id
            project_name = item["proyecto"].nombre
            profit = item["profit"]
            
            project_finances = self.finanzas_service.get_project_profitability(
                project_id,
                self.current_start_date,
                self.current_end_date
            )
            income = project_finances["project_income"]
            expenses = project_finances["project_expenses"]

            self.top_projects_table.setItem(i, 0, QTableWidgetItem(project_name))
            self.top_projects_table.setItem(i, 1, QTableWidgetItem(f"$ {format_cop(profit)}"))
            self.top_projects_table.setItem(i, 2, QTableWidgetItem(f"$ {format_cop(income)}"))
            self.top_projects_table.setItem(i, 3, QTableWidgetItem(f"$ {format_cop(expenses)}"))

    def _update_project_finances(self):
        project_id = self.project_combo.currentData()
        if project_id and project_id != -1:
            project_finances = self.finanzas_service.get_project_profitability(
                project_id,
                self.current_start_date,
                self.current_end_date
            )
            self.lbl_project_income.setText(f"Ingresos del Proyecto: $ {format_cop(project_finances['project_income'])}")
            self.lbl_project_expenses.setText(f"Gastos del Proyecto: $ {format_cop(project_finances['project_expenses'])}")
            self.lbl_project_profit.setText(f"Rentabilidad del Proyecto: $ {format_cop(project_finances['profit'])}")
        else:
            self.lbl_project_income.setText(f"Ingresos del Proyecto: $ {format_cop(0)}")
            self.lbl_project_expenses.setText(f"Gastos del Proyecto: $ {format_cop(0)}")
            self.lbl_project_profit.setText(f"Rentabilidad del Proyecto: $ {format_cop(0)}")

    def _filter_expenses_by_description(self):
        description = self.txt_expense_description.text().strip()
        if description:
            # We can optionally filter by project as well if a project is selected
            selected_project_id = self.project_combo.currentData()
            project_id_to_filter = selected_project_id if selected_project_id != -1 else None

            total_expenses = self.finanzas_service.get_expenses_by_description(
                description,
                project_id=project_id_to_filter,
                start_date=self.current_start_date,
                end_date=self.current_end_date
            )
            self.lbl_expense_desc_total.setText(f"Total Gastos por '{description}': $ {format_cop(total_expenses)}")
        else:
            self.lbl_expense_desc_total.setText(f"Total Gastos por Descripción: $ {format_cop(0)}")

    def closeEvent(self, event):
        if self.finanzas_service:
            self.finanzas_service.close_session()
        super().closeEvent(event)

