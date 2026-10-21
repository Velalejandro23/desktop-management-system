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
from app.models.equipo import Equipo
from app.models.proyecto_equipo import ProyectoEquipo
from app.views.equipo_form import EquipoForm
from app.views.equipo_detalle import EquipoDetalle # New import
from app.views.add_novedad_dialog import AddNovedadDialog
from app.views.display_novedades_dialog import DisplayNovedadesDialog # New import
from app.services import novedad_service # New import


class EquiposView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cargar_equipos()

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
        self.btn_novedades.clicked.connect(lambda: self._show_novedades_dialog("Equipos")) # Connect to dialog
        btn_layout.addWidget(self.btn_novedades)

        btn_layout.addStretch()

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Buscar equipo...")
        self.buscador.setFixedWidth(250)
        self.buscador.textChanged.connect(self.filtrar)
        btn_layout.addWidget(self.buscador)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels([
            "Nombre", "Tipo", "Cantidad", "Acciones"
        ])
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True) # Habilitar colores alternos
        self.tabla.verticalHeader().setDefaultSectionSize(45) # Filas más altas
        self.tabla.verticalHeader().setVisible(False) # Ocultar números de fila para limpiar la vista


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

    def cargar_equipos(self):
        self.tabla.setRowCount(0)
        session = get_session()
        equipos = session.query(Equipo).all()

        for fila, eq in enumerate(equipos):
            self.tabla.insertRow(fila)

            self.tabla.setItem(fila, 0, QTableWidgetItem(eq.nombre.title()))
            self.tabla.setItem(fila, 1, QTableWidgetItem((eq.tipo or "").title()))
            self.tabla.setItem(fila, 2, QTableWidgetItem(str(eq.cantidad)))
            
            # Guardar ID oculto
            self.tabla.item(fila, 0).setData(Qt.UserRole, eq.id)

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

            btn_ver.clicked.connect(lambda _, e=eq.id: self.ver_detalle(e))
            btn_editar.clicked.connect(lambda _, e=eq.id: self.editar_desde_tabla(e))
            btn_eliminar.clicked.connect(lambda _, e=eq.id: self.eliminar_desde_tabla(e))

            contenedor = QHBoxLayout()
            contenedor.setContentsMargins(0, 0, 0, 0)
            contenedor.setSpacing(6)
            contenedor.setAlignment(Qt.AlignCenter)
            contenedor.addWidget(btn_ver)
            contenedor.addWidget(btn_editar)
            contenedor.addWidget(btn_eliminar)

            widget = QWidget()
            widget.setLayout(contenedor)

            self.tabla.setCellWidget(fila, 3, widget) # Adjusted from 5 to 3

        session.close()
        self.filtrar(self.buscador.text())

    # ---------------- ACCIONES ----------------
    def nuevo(self):
        form = EquipoForm()
        if form.exec():
            self.cargar_equipos()

    def ver_detalle(self, eq_id):
        dlg = EquipoDetalle(eq_id)
        dlg.exec()

    def editar_desde_tabla(self, eq_id):
        form = EquipoForm(eq_id)
        if form.exec():
            self.cargar_equipos()

    def eliminar_desde_tabla(self, eq_id):
        confirm = QMessageBox.question(
            self, "Confirmar",
            "¿Seguro que deseas eliminar este equipo?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            session = get_session()
            
            # Validar si el equipo está asociado a algún proyecto
            proyecto_asociado = session.query(ProyectoEquipo).filter(
                ProyectoEquipo.equipo_id == eq_id
            ).first()
            
            if proyecto_asociado:
                session.close()
                QMessageBox.warning(
                    self, "No se puede eliminar",
                    f"El equipo está asociado a uno o más proyectos.\n"
                    f"Debe desasociarlo de los proyectos antes de eliminarlo."
                )
                return
            
            eq = session.get(Equipo, eq_id)
            if eq:
                session.delete(eq)
                session.commit()
                session.close()
                self.cargar_equipos()
            else:
                session.close()
                QMessageBox.warning(self, "Error", "Equipo no encontrado.")
