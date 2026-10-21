from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,QToolButton,
    QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QHeaderView, QLineEdit
)
from PySide6.QtGui import QPixmap, QPainter, QColor,QIcon
from PySide6.QtCore import Qt,QSize
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtSvg import QSvgRenderer

from app.utils.paths import resource_path
from app.database.db import get_session
from app.models.empleado import Empleado
from app.models.proyecto_empleado import ProyectoEmpleado
from app.views.empleado_form import EmpleadoForm
from app.views.add_novedad_dialog import AddNovedadDialog
from app.views.display_novedades_dialog import DisplayNovedadesDialog # New import
from app.services import novedad_service # New import


class EmpleadosView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cargar_empleados()

    # ---------------- UI ----------------
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
        self.btn_novedades.clicked.connect(lambda: self._show_novedades_dialog("Empleados")) # Connect to dialog
        btn_layout.addWidget(self.btn_novedades)
        
        btn_layout.addStretch()

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Buscar empleado...")
        self.buscador.setFixedWidth(250)
        self.buscador.textChanged.connect(self.filtrar)
        btn_layout.addWidget(self.buscador)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Nombre", "Apellidos", "Teléfono", "Estado", "Acciones"
        ])

        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setDefaultSectionSize(45)
        self.tabla.verticalHeader().setVisible(False)

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
    def cargar_empleados(self):
        self.tabla.setRowCount(0)
        session = get_session()
        empleados = session.query(Empleado).all()

        for fila, emp in enumerate(empleados):
            self.tabla.insertRow(fila)

            self.tabla.setItem(fila, 0, QTableWidgetItem(emp.nombre.title()))
            self.tabla.setItem(fila, 1, QTableWidgetItem(emp.apellidos.title()))
            self.tabla.setItem(fila, 2, QTableWidgetItem(emp.telefono or ""))
            self.tabla.setItem(
                fila, 3,
                QTableWidgetItem("Activo" if emp.estado else "Inactivo")
            )

            # Guardar ID oculto
            self.tabla.item(fila, 0).setData(Qt.UserRole, emp.id)

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


            btn_ver.clicked.connect(lambda _, e=emp.id: self.ver_detalle(e))
            btn_editar.clicked.connect(lambda _, e=emp.id: self.editar_desde_tabla(e))
            btn_eliminar.clicked.connect(lambda _, e=emp.id: self.eliminar_desde_tabla(e))

            contenedor = QHBoxLayout()
            contenedor.setContentsMargins(0, 0, 0, 0)
            contenedor.setSpacing(6)
            contenedor.setAlignment(Qt.AlignCenter)
            contenedor.addWidget(btn_ver)
            contenedor.addWidget(btn_editar)
            contenedor.addWidget(btn_eliminar)

            widget = QWidget()
            widget.setLayout(contenedor)

            self.tabla.setCellWidget(fila, 4, widget)

        session.close()
        self.filtrar(self.buscador.text())

    # ---------------- ACCIONES ----------------
    def nuevo(self):
        form = EmpleadoForm()
        if form.exec():
            self.cargar_empleados()

    def ver_detalle(self, emp_id):
        from app.views.empleado_detalle import EmpleadoDetalle
        dlg = EmpleadoDetalle(emp_id)
        dlg.exec()

    def editar_desde_tabla(self, emp_id):
        form = EmpleadoForm(emp_id)
        if form.exec():
            self.cargar_empleados()

    def eliminar_desde_tabla(self, emp_id):
        confirm = QMessageBox.question(
            self, "Confirmar",
            "¿Seguro que deseas eliminar este empleado?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            session = get_session()
            
            # Validar si el empleado está asociado a algún proyecto
            proyecto_asociado = session.query(ProyectoEmpleado).filter(
                ProyectoEmpleado.empleado_id == emp_id
            ).first()
            
            if proyecto_asociado:
                session.close()
                QMessageBox.warning(
                    self, "No se puede eliminar",
                    f"El empleado está asociado a uno o más proyectos.\n"
                    f"Debe desasociarlo de los proyectos antes de eliminarlo."
                )
                return
            
            emp = session.get(Empleado, emp_id)
            if emp:
                session.delete(emp)
                session.commit()
                session.close()
                self.cargar_empleados()
            else:
                session.close()
                QMessageBox.warning(self, "Error", "Empleado no encontrado.")
