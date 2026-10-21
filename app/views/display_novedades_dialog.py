from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from app.models.novedad import Novedad # For type hinting
from app.services import novedad_service
from app.database.db import get_session
from sqlalchemy.orm import Session # Import Session for type hinting

class DisplayNovedadesDialog(QDialog):
    def __init__(self, module_name: str, parent=None): # Removed 'novedades' from constructor
        super().__init__(parent)
        self.setWindowTitle(f"Gestión de Novedades para {module_name}")
        self.module_name = module_name
        self.db_session = get_session() # Get session here
        self.novedades = [] # Will be loaded dynamically
        self.init_ui()
        self._load_novedades_table() # Load data on initialization

    def _cleanup_session(self):
        if self.db_session:
            self.db_session.close()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        self.table_novedades = QTableWidget()
        self.table_novedades.setColumnCount(4) # ID, Fecha, Mensaje, Expira
        self.table_novedades.setHorizontalHeaderLabels(["ID", "Fecha", "Mensaje", "Expira"])
        self.table_novedades.setColumnHidden(0, True) # Hide ID column
        self.table_novedades.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_novedades.setEditTriggers(QTableWidget.NoEditTriggers) # Make table read-only
        main_layout.addWidget(self.table_novedades)

        button_layout = QHBoxLayout()
        self.btn_delete_novedad = QPushButton("🗑️ Eliminar Novedad Seleccionada")
        self.btn_delete_novedad.clicked.connect(self._delete_selected_novedad)
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_delete_novedad)
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
    
    def _load_novedades_table(self):
        self.novedades = novedad_service.get_active_novedades_by_module(self.db_session, None)
        print(f"[DEBUG] DisplayNovedadesDialog._load_novedades_table module={self.module_name} count={len(self.novedades)}")
        self.table_novedades.setRowCount(len(self.novedades))
        for row, novedad in enumerate(self.novedades):
            self.table_novedades.setItem(row, 0, QTableWidgetItem(str(novedad.id)))
            self.table_novedades.setItem(row, 1, QTableWidgetItem(novedad.created_at.strftime('%Y-%m-%d %H:%M')))
            self.table_novedades.setItem(row, 2, QTableWidgetItem(novedad.message))
            self.table_novedades.setItem(row, 3, QTableWidgetItem(novedad.expires_at.strftime('%Y-%m-%d')))

    def _delete_selected_novedad(self):
        selected_rows = self.table_novedades.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Eliminar Novedad", "Por favor, seleccione una novedad para eliminar.")
            return

        reply = QMessageBox.question(self, "Confirmar Eliminación", 
                                     "¿Está seguro de que desea eliminar la novedad seleccionada?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Get the ID from the hidden first column of the selected row
            novedad_id_item = self.table_novedades.item(selected_rows[0].row(), 0)
            if novedad_id_item:
                novedad_id = int(novedad_id_item.text())
                novedad_service.delete_novedad(self.db_session, novedad_id)
                QMessageBox.information(self, "Eliminar Novedad", "Novedad eliminada exitosamente.")
                self._load_novedades_table() # Refresh table
            else:
                QMessageBox.critical(self, "Error", "No se pudo obtener el ID de la novedad seleccionada.")

    def closeEvent(self, event):
        self._cleanup_session()
        super().closeEvent(event)
