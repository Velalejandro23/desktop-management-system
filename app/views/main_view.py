from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QButtonGroup
)
from PySide6.QtCore import Qt, Signal # Added Signal
from PySide6.QtGui import QIcon
from app.utils.paths import resource_path

from app.views.calendar_view import CalendarView
from app.views.empleados_view import EmpleadosView
from app.views.materiales_view import MaterialesView
from app.views.equipos_view import EquiposView
from app.views.proyectos_view import ProyectosView
from app.views.dashboard_finanzas_view import DashboardFinanzasView
from app.views.add_novedad_dialog import AddNovedadDialog
from app.views.display_novedades_dialog import DisplayNovedadesDialog
from app.views.display_novedades_readonly_dialog import DisplayNovedadesReadOnlyDialog # New import
from app.services import novedad_service
from app.database.db import get_session


class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SISMAEP")
        self.setWindowIcon(QIcon(resource_path("assets/logo.png")))
        self.resize(1600, 900)
        self.init_ui()
        # note: initial novedad display is handled by login view to avoid accidental deletion

    def _show_novedades_dialog(self, module_name: str):
        dialog = AddNovedadDialog(module_name=module_name, parent=self)
        dialog.exec()

    def _cleanup_and_display_novedades(self, module_name: str):
        db = get_session()
        try:
            # First, clean up expired novelties
            # novedad_service.delete_expired_novedades(db) # Temporarily commented out

            # Then, get active novelties for the current module
            active_novedades = novedad_service.get_active_novedades_by_module(db, module_name)
            if active_novedades:
                dialog = DisplayNovedadesReadOnlyDialog(module_name=module_name, parent=self)
                dialog.exec()
        except Exception as e:
            print(f"Error handling novelties: {e}") # Log error, don't block UI
        finally:
            db.close()

    def init_ui(self):
        """Initializes the main UI layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create and add the side menu and main panel
        menu_panel = self._create_menu()
        main_panel = self._create_main_panel()

        layout.addWidget(menu_panel, 1)
        layout.addWidget(main_panel, 5)

    def _create_menu(self):
        """Creates the side menu panel."""
        menu_frame = QFrame()
        menu_frame.setObjectName("menuFrame")
        
        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setContentsMargins(10, 15, 10, 15)
        menu_layout.setSpacing(15)

        # Título como Imagen
        logo_label = QLabel()
        logo_pixmap = QIcon(resource_path("assets/logo.png")).pixmap(180, 100) # Adjust size as needed
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(170, 100) # Set fixed size for the label to hold the pixmap
        # Remove objectName "menuTitulo" as styling for text won't apply
        # titulo.setObjectName("menuTitulo") 

        self.btn_calendario = QPushButton("Visitas")
        self.btn_empleados = QPushButton("Empleados")
        self.btn_materiales = QPushButton("Materiales")
        self.btn_equipos = QPushButton("Equipos")
        self.btn_proyectos = QPushButton("Proyectos")
        self.btn_dashboard_finanzas = QPushButton("Dashboard Finanzas")
        self.btn_novedades = QPushButton("Novedades")
        self.btn_salir = QPushButton("Salir")
        
        # Apply a specific object name for menu buttons
        for btn in [self.btn_calendario, self.btn_empleados, self.btn_materiales, self.btn_equipos, self.btn_proyectos, self.btn_dashboard_finanzas, self.btn_novedades, self.btn_salir]: # Removed btn_finanzas
            btn.setObjectName("menuButton")

        # Make buttons checkable and group them
        self.menu_button_group = QButtonGroup()
        self.menu_button_group.setExclusive(True)

        for btn in [self.btn_calendario, self.btn_empleados, self.btn_materiales, self.btn_equipos, self.btn_proyectos, self.btn_dashboard_finanzas]: # Removed btn_finanzas
            btn.setCheckable(True)
            self.menu_button_group.addButton(btn)

        # Set initial checked button
        self.btn_calendario.setChecked(True)

        menu_layout.addWidget(logo_label) # Add the logo_label instead of titulo
        menu_layout.addSpacing(20)
        menu_layout.addWidget(self.btn_calendario)
        menu_layout.addWidget(self.btn_empleados)
        menu_layout.addWidget(self.btn_materiales)
        menu_layout.addWidget(self.btn_equipos)
        menu_layout.addWidget(self.btn_proyectos)
        menu_layout.addWidget(self.btn_dashboard_finanzas) # Added to layout
        menu_layout.addStretch()
        menu_layout.addWidget(self.btn_novedades)
        menu_layout.addWidget(self.btn_salir)

        # Connect the new button's signal
        self.btn_novedades.clicked.connect(lambda: DisplayNovedadesDialog(module_name="Main", parent=self).exec())
        
        return menu_frame

    def _create_main_panel(self):
        """Creates the main content panel with the stacked widget."""
        self.stack = QStackedWidget()
        self.calendar_view = CalendarView()
        self.empleados_view = EmpleadosView()
        self.materiales_view = MaterialesView()
        self.equipos_view = EquiposView()
        self.proyectos_view = ProyectosView()
        # self.finanzas_view = FinanzasView() # Removed
        self.dashboard_finanzas_view = DashboardFinanzasView()

        self.stack.addWidget(self.calendar_view)
        self.stack.addWidget(self.empleados_view)
        self.stack.addWidget(self.materiales_view)
        self.stack.addWidget(self.equipos_view)
        self.stack.addWidget(self.proyectos_view)
        # self.stack.addWidget(self.finanzas_view) # Removed
        self.stack.addWidget(self.dashboard_finanzas_view)

        # Connect signals after buttons are created
        self.btn_calendario.clicked.connect(lambda: self.stack.setCurrentWidget(self.calendar_view))
        self.btn_empleados.clicked.connect(lambda: self.stack.setCurrentWidget(self.empleados_view))
        self.btn_materiales.clicked.connect(lambda: self.stack.setCurrentWidget(self.materiales_view))
        self.btn_equipos.clicked.connect(lambda: self.stack.setCurrentWidget(self.equipos_view))
        self.btn_proyectos.clicked.connect(lambda: self.stack.setCurrentWidget(self.proyectos_view))
        self.btn_dashboard_finanzas.clicked.connect(lambda: self.stack.setCurrentWidget(self.dashboard_finanzas_view))
        self.btn_salir.clicked.connect(self.close)

        # Connect data change signals to refresh dashboard
        self.proyectos_view.data_changed.connect(self.dashboard_finanzas_view.refresh_dashboard)

        return self.stack
