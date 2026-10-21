from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,QToolButton,
    QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QHeaderView, QLineEdit
)
from PySide6.QtGui import QPixmap, QPainter, QColor,QIcon
from PySide6.QtCore import Qt,QSize, Signal # Import Signal
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtSvg import QSvgRenderer

from app.database.db import get_session
from app.models.proyecto import Proyecto
from app.views.proyecto_form import ProyectoForm
from app.views.add_novedad_dialog import AddNovedadDialog
from app.views.display_novedades_dialog import DisplayNovedadesDialog # New import
from app.services import novedad_service # New import
from app.utils.formatting import format_cop
from app.utils.paths import resource_path


class ProyectosView(QWidget):
    data_changed = Signal() # Define the custom signal

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cargar_proyectos()


    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Botones de acción
        btn_layout = QHBoxLayout()
        self.btn_nuevo = QPushButton("➕ Nuevo")
        self.btn_nuevo.clicked.connect(self.nuevo)
        btn_layout.addWidget(self.btn_nuevo)
        
        self.btn_novedades = QPushButton("📢 Novedades") # New Novedades button
        self.btn_novedades.clicked.connect(lambda: self._show_novedades_dialog("Proyectos")) # Connect to dialog
        btn_layout.addWidget(self.btn_novedades)
        
        btn_layout.addStretch()

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Buscar proyecto...")
        self.buscador.setFixedWidth(250)
        self.buscador.textChanged.connect(self.filtrar)
        btn_layout.addWidget(self.buscador)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Nombre", "Cliente", "Fecha Inicio", "Fecha Fin", "Estado", "Presupuesto", "Anticipo", "Acciones"
        ])
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setDefaultSectionSize(45)
        self.tabla.verticalHeader().setVisible(False)
        # Ocultar la columna de ID si se prefiere (ya no es necesario ocultar ID)
        # self.tabla.setColumnHidden(0, True)

        layout.addLayout(btn_layout)
        layout.addWidget(self.tabla)
        self.setLayout(layout)

    # ---------------- FILTRO ----------------
    def filtrar(self, texto):
        texto = texto.lower()
        for fila in range(self.tabla.rowCount()):
            coincide = False
            for columna in range(self.tabla.columnCount() - 1): # Excluir columna de acciones
                item = self.tabla.item(fila, columna)
                if item and texto in item.text().lower():
                    coincide = True
                    break
            self.tabla.setRowHidden(fila, not coincide)

    # ---------------- UTILIDADES ----------------
    def crear_boton(self, icono, tooltip):
        btn = QToolButton()
        btn.setIcon(icono)
        btn.setIconSize(QSize(18, 18))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setAutoRaise(True)
        btn.setFixedSize(32, 32)

        btn.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
            }
            QToolButton:hover {
                background-color: #eaeaea;
                border-radius: 6px;
            }
        """)

        return btn
    
    def _show_novedades_dialog(self, module_name: str):
        dialog = AddNovedadDialog(module_name=module_name, parent=self)
        dialog.exec()
        
    def _cleanup_and_display_novedades(self, module_name: str):
        db = get_session()
        try:
            # First, clean up expired novelties
            novedad_service.delete_expired_novedades(db)
            
            # Then, get active novelties for the current module
            active_novedades = novedad_service.get_active_novedades_by_module(db, module_name)
            if active_novedades:
                # dialog will fetch novedades itself based on module_name
                dialog = DisplayNovedadesDialog(module_name=module_name, parent=self)
                dialog.exec()
        except Exception as e:
            print(f"Error handling novelties: {e}") # Log error, don't block UI
        finally:
            db.close()


    
    def icono_coloreado(self, ruta_svg, color, size=18):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        renderer = QSvgRenderer(ruta_svg)
        painter = QPainter(pixmap)

        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor(color))
        painter.end()

        return QIcon(pixmap)
    # ---------------- DATOS ----------------

    def cargar_proyectos(self):
        self.tabla.setRowCount(0)
        session = get_session()
        proyectos = session.query(Proyecto).all()

        for fila, p in enumerate(proyectos):
            self.tabla.insertRow(fila)

            self.tabla.setItem(fila, 0, QTableWidgetItem(p.nombre.title()))
            self.tabla.setItem(fila, 1, QTableWidgetItem((p.cliente or "").title()))
            self.tabla.setItem(fila, 2, QTableWidgetItem(p.fecha_inicio.strftime('%Y-%m-%d') if p.fecha_inicio else ''))
            self.tabla.setItem(fila, 3, QTableWidgetItem(p.fecha_fin.strftime('%Y-%m-%d') if p.fecha_fin else ''))
            self.tabla.setItem(fila, 4, QTableWidgetItem((p.estado or "").title()))
            self.tabla.setItem(fila, 5, QTableWidgetItem(f"$ {format_cop(p.presupuesto)}"))
            self.tabla.setItem(fila, 6, QTableWidgetItem(f"$ {format_cop(p.anticipo)}"))
            
            # Guardar ID oculto
            self.tabla.item(fila, 0).setData(Qt.UserRole, p.id)

            # Botones
            btn_ver = self.crear_boton(
                self.icono_coloreado(resource_path("assets/icons/view.svg"), "#61615E"),
                "Ver detalles"
            )

            btn_editar = self.crear_boton(
                self.icono_coloreado(resource_path("assets/icons/edit.svg"), "#0fc4f1"),
                "Editar"
            )

            btn_eliminar = self.crear_boton(
                self.icono_coloreado(resource_path("assets/icons/delete.svg"), "#e74c3c"),
                "Eliminar"
            )

            btn_ver.clicked.connect(lambda _, pr_id=p.id: self.ver_detalle(pr_id))
            btn_editar.clicked.connect(lambda _, pr_id=p.id: self.editar_desde_tabla(pr_id))
            btn_eliminar.clicked.connect(lambda _, pr_id=p.id: self.eliminar_desde_tabla(pr_id))

            contenedor = QHBoxLayout()
            contenedor.setContentsMargins(0, 0, 0, 0)
            contenedor.setSpacing(6)
            contenedor.setAlignment(Qt.AlignCenter)
            contenedor.addWidget(btn_ver)
            contenedor.addWidget(btn_editar)
            contenedor.addWidget(btn_eliminar)

            widget = QWidget()
            widget.setLayout(contenedor)

            self.tabla.setCellWidget(fila, 7, widget)

        session.close()
        self.filtrar(self.buscador.text())

    # ---------------- ACCIONES ----------------
    def nuevo(self):
        form = ProyectoForm()
        if form.exec():
            form.financial_data_changed.connect(self.data_changed) # Connect the signal
            self.cargar_proyectos()
            self.data_changed.emit() # Also emit for project list changes
            # Refresh MaterialesView and EquiposView after project save
            from app.views.main_view import MainView # Local import to avoid circular dependency
            if isinstance(self.parent().parent(), MainView):
                main_view = self.parent().parent()
                main_view.materiales_view.cargar_materiales()
                main_view.equipos_view.cargar_equipos()

    def ver_detalle(self, pr_id):
        from app.views.proyecto_detalle import ProyectoDetalleView
        dlg = ProyectoDetalleView(pr_id)
        dlg.exec()

    def editar_desde_tabla(self, pr_id):
        form = ProyectoForm(pr_id)
        if form.exec():
            form.financial_data_changed.connect(self.data_changed) # Connect the signal
            self.cargar_proyectos()
            self.data_changed.emit() # Also emit for project list changes
            # Refresh MaterialesView and EquiposView after project save
            from app.views.main_view import MainView # Local import to avoid circular dependency
            if isinstance(self.parent().parent(), MainView):
                main_view = self.parent().parent()
                main_view.materiales_view.cargar_materiales()
                main_view.equipos_view.cargar_equipos()

    def eliminar_desde_tabla(self, pr_id):
        confirm = QMessageBox.question(
            self, "Confirmar",
            "¿Seguro que deseas eliminar este proyecto? Esto podría eliminar registros financieros asociados.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            session = get_session()
            p = session.get(Proyecto, pr_id)
            if p:
                session.delete(p)
                session.commit()
                session.close()
                self.cargar_proyectos()
                self.data_changed.emit() # Emit signal after data is loaded
            else:
                session.close()
                QMessageBox.warning(self, "Error", "Proyecto no encontrado.")
