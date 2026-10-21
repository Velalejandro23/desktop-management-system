from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCalendarWidget,
    QListWidget, QPushButton, QHBoxLayout, QListWidgetItem
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor

from datetime import datetime, time
from app.database.db import get_session
from app.models.visita import Visita
from app.views.add_visit_dialog import AddVisitDialog
from app.views.add_novedad_dialog import AddNovedadDialog
from app.views.display_novedades_dialog import DisplayNovedadesDialog # New import
from app.services import novedad_service # New import
from app.views.visita_detalle import VisitaDetalle # New import


class CalendarView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cargar_fechas_con_eventos()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        titulo = QLabel("Calendario de Visitas")
        titulo.setObjectName("calendarTitle")
        titulo.setAlignment(Qt.AlignCenter)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setObjectName("mainCalendar")
        # Ensure a small spacing between month and year controls by adjusting
        # the navigation bar's layout spacing and margins directly. Stylesheets
        # can't always influence layout spacing, so set it programmatically.
        nav = self.calendar.findChild(QWidget, "qt_calendar_navigationbar")
        if nav and nav.layout():
            try:
                nav.layout().setSpacing(8)
                nav.layout().setContentsMargins(6, 2, 6, 2)
            except Exception:
                pass

        btn_row_layout = QHBoxLayout() # New layout for buttons
        self.btn_agregar = QPushButton("Nueva visita")
        self.btn_agregar.setObjectName("newVisitButton")
        self.btn_agregar.clicked.connect(self.agregar_visita)
        btn_row_layout.addWidget(self.btn_agregar)

        self.btn_novedades = QPushButton("📢 Novedades") # New Novedades button
        self.btn_novedades.clicked.connect(lambda: self._show_novedades_dialog("Calendario")) # Connect to dialog
        btn_row_layout.addWidget(self.btn_novedades)
        btn_row_layout.addStretch() # Push buttons to the left

        self.lista = QListWidget()
        self.lista.setObjectName("visitList")

        day_list_label = QLabel("Visitas del día:")
        day_list_label.setObjectName("dayListLabel")


        layout.addWidget(titulo)
        layout.addWidget(self.calendar)
        layout.addLayout(btn_row_layout) # Add the new button layout
        layout.addWidget(day_list_label)
        layout.addWidget(self.lista)


        self.calendar.clicked.connect(self.mostrar_visitas_dia)
        self.lista.itemClicked.connect(self.mostrar_detalle_visita)

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


    # 🟢 Abrir formulario para agregar visita
    def agregar_visita(self):
        fecha = self.calendar.selectedDate()
        dialog = AddVisitDialog(fecha)

        if dialog.exec():
            session = get_session()

            nueva = Visita(
                titulo=dialog.titulo.text(),
                descripcion=dialog.descripcion.toPlainText(),
                fecha_inicio=dialog.fecha_inicio.toPython(), # QDateTime to Python datetime
                fecha_fin=dialog.fecha_fin.toPython(),       # QDateTime to Python datetime
                recibe_persona=dialog.recibe_persona_text,
                direccion=dialog.direccion_text,
                tipo_visita=dialog.tipo_visita_text,
                objetivo=dialog.objetivo_text,
                persona_hace_visita=dialog.persona_hace_visita_text,
                estado="Pendiente"
            )

            session.add(nueva)
            session.commit()
            session.close()

            # refrescar vista
            self.cargar_fechas_con_eventos()
            self.mostrar_visitas_dia(fecha)

    # 🟢 Marca los días con visitas
    def cargar_fechas_con_eventos(self):
        # Reset all formats
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        session = get_session()
        visitas = session.query(Visita).all()
        session.close()

        # Highlight dates with events by setting their background color.
        # Styling this via QSS is not straightforward for QCalendarWidget,
        # so we do it programmatically.
        formato = QTextCharFormat()
        formato.setBackground(QColor("#d4edda")) # Light green

        for v in visitas:
            fecha = QDate(
                v.fecha_inicio.year,
                v.fecha_inicio.month,
                v.fecha_inicio.day
            )
            # Apply the format to the specific date
            self.calendar.setDateTextFormat(fecha, formato)

    # 🟢 Mostrar visitas del día seleccionado
    def mostrar_visitas_dia(self, fecha):
        self.lista.clear()
        session = get_session()

        inicio = datetime.combine(fecha.toPython(), time.min)
        fin = datetime.combine(fecha.toPython(), time.max)

        visitas = session.query(Visita).filter(
            Visita.fecha_inicio.between(inicio, fin)
        ).order_by(Visita.fecha_inicio).all()

        if not visitas:
            self.lista.addItem("No hay visitas este día.")
        else:
            for v in visitas:
                hora_inicio = v.fecha_inicio.strftime("%H:%M")
                hora_fin = v.fecha_fin.strftime("%H:%M")
                item_text = f"{hora_inicio} - {hora_fin} - {v.titulo} (Recibe: {v.recibe_persona}, Dirección: {v.direccion})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, v.id) # Store the visit ID
                self.lista.addItem(item)

        session.close()

    def mostrar_detalle_visita(self, item):
        visita_id = item.data(Qt.UserRole)
        if visita_id:
            dialog = VisitaDetalle(visita_id, self)
            dialog.visita_deleted.connect(self._refresh_calendar_data) # Connect the signal
            dialog.exec()

    def _refresh_calendar_data(self):
        # Refresh both calendar highlights and the current day's visit list
        self.cargar_fechas_con_eventos()
        self.mostrar_visitas_dia(self.calendar.selectedDate())
