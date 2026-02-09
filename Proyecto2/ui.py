"""
Módulo de Interfaz de Usuario (UI)

Contiene:
- La clase PersonDialog (para añadir/editar).
- La clase MainWindow (la ventana principal de la app).
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QAbstractItemView,
    QProgressDialog, QGroupBox, QGridLayout, QToolBar, QStyle
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

# Importar la lógica y constantes de functions.py
import functions 
from functions import FIELD_NAMES, GenerationWorker

class PersonDialog(QDialog):
    """Diálogo para agregar o editar una persona."""
    
    def __init__(self, persona_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administrar Persona")
        self.setMinimumWidth(400)

        self.fields = {}
        layout = QFormLayout(self)

        for i, field_name in enumerate(FIELD_NAMES):
            line_edit = QLineEdit()
            if persona_data:
                line_edit.setText(persona_data[i])
            self.fields[field_name] = line_edit
            layout.addRow(f"{field_name.capitalize()}:", line_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        """Devuelve los datos de los campos como una lista."""
        return [self.fields[field_name].text() for field_name in FIELD_NAMES]

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Combinación de Correspondencia")
        self.setGeometry(100, 100, 1000, 600)

        self.template_oficio = ""
        self.progress_dialog = None
        self.worker = None

        # Cargar datos lógicos primero
        self.load_template()

        # Configurar la UI
        self._create_actions()
        self._create_tool_bar()
        self._create_central_widget()
        self._connect_signals()
        
        # Cargar datos en la tabla
        self.load_personas()

    def _create_actions(self):
        """Crea las QActions para la barra de herramientas."""
        # Usar iconos estándar de QStyle
        style = self.style()
        icon_add = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon) # Re-usado, SP_NewFolderIcon es otra opción
        icon_edit = style.standardIcon(QStyle.StandardPixmap.SP_DialogYesButton) # Re-usado
        icon_delete = style.standardIcon(QStyle.StandardPixmap.SP_DialogNoButton) # Re-usado

        self.action_add = QAction(icon_add, "Añadir (Altas)", self)
        self.action_edit = QAction(icon_edit, "Editar (Cambios)", self)
        self.action_delete = QAction(icon_delete, "Eliminar (Bajas)", self)

    def _create_tool_bar(self):
        """Crea y añade la barra de herramientas principal."""
        tool_bar = QToolBar("Acciones Principales")
        tool_bar.addAction(self.action_add)
        tool_bar.addAction(self.action_edit)
        tool_bar.addAction(self.action_delete)
        self.addToolBar(tool_bar)

    def _create_central_widget(self):
        """Crea y configura el widget central (tabla y botones)."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # --- Tabla de Personas ---
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(len(FIELD_NAMES))
        self.tableWidget.setHorizontalHeaderLabels([name.capitalize() for name in FIELD_NAMES])
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.tableWidget, 1) # Ocupa más espacio

        # --- Grupo de Generación (UI Mejorada) ---
        gen_group = QGroupBox("Generación de Documentos")
        gen_layout = QGridLayout(gen_group)

        # Botones de TXT
        self.btn_gen_txt_sel = QPushButton("Generar TXT (Seleccionado)")
        self.btn_gen_txt_all = QPushButton("Generar TXT (Todos)")
        gen_layout.addWidget(self.btn_gen_txt_sel, 0, 0)
        gen_layout.addWidget(self.btn_gen_txt_all, 1, 0)

        # Botones de PDF
        self.btn_gen_pdf_sel = QPushButton("Generar PDF (Seleccionado)")
        self.btn_gen_pdf_all = QPushButton("Generar PDF (Todos)")
        gen_layout.addWidget(self.btn_gen_pdf_sel, 0, 1)
        gen_layout.addWidget(self.btn_gen_pdf_all, 1, 1)

        # Botones de DOCX
        self.btn_gen_docx_sel = QPushButton("Generar DOCX (Seleccionado)")
        self.btn_gen_docx_all = QPushButton("Generar DOCX (Todos)")
        gen_layout.addWidget(self.btn_gen_docx_sel, 0, 2)
        gen_layout.addWidget(self.btn_gen_docx_all, 1, 2)

        main_layout.addWidget(gen_group)

    def _connect_signals(self):
        """Conecta todas las señales de botones y actions."""
        # Acciones de la barra de herramientas
        self.action_add.triggered.connect(self.on_add)
        self.action_edit.triggered.connect(self.on_edit)
        self.action_delete.triggered.connect(self.on_delete)
        
        # Botones de generación
        self.btn_gen_txt_sel.clicked.connect(lambda: self.on_generate(selected_only=True, gen_type='txt'))
        self.btn_gen_txt_all.clicked.connect(lambda: self.on_generate(selected_only=False, gen_type='txt'))
        
        self.btn_gen_pdf_sel.clicked.connect(lambda: self.on_generate(selected_only=True, gen_type='pdf'))
        self.btn_gen_pdf_all.clicked.connect(lambda: self.on_generate(selected_only=False, gen_type='pdf'))
        
        self.btn_gen_docx_sel.clicked.connect(lambda: self.on_generate(selected_only=True, gen_type='docx'))
        self.btn_gen_docx_all.clicked.connect(lambda: self.on_generate(selected_only=False, gen_type='docx'))

    # --- Métodos de Carga/Guardado (Puente UI <-> Lógica) ---

    def show_message(self, title, message):
        """Muestra un diálogo de mensaje."""
        QMessageBox.information(self, title, message)

    def load_template(self):
        """Carga la plantilla usando la función de 'functions.py'."""
        self.template_oficio = functions.load_template_content()
        if "ERROR" in self.template_oficio:
            self.show_message("Error de Plantilla", self.template_oficio)

    def load_personas(self):
        """Carga los datos de 'functions.py' en la QTableWidget."""
        self.tableWidget.setRowCount(0) # Limpiar tabla
        data = functions.load_personas_data()
        
        if not data:
            self.show_message("Información", f"No se encontraron datos en '{functions.PERSONAS_FILE}'.")
            
        for row_idx, fila in enumerate(data):
            self.tableWidget.insertRow(row_idx)
            for col_idx, item in enumerate(fila):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(item))
        self.tableWidget.resizeColumnsToContents()

    def save_personas(self):
        """Extrae los datos de la QTableWidget y los guarda usando 'functions.py'."""
        data = []
        for row in range(self.tableWidget.rowCount()):
            fila = []
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, col)
                fila.append(item.text() if item else "")
            data.append(fila)
        
        try:
            functions.save_personas_data(data)
        except Exception as e:
            self.show_message("Error al Guardar", f"No se pudo guardar el archivo de personas: {e}")

    def get_persona_dict(self, row):
        """Convierte una fila de la tabla en un diccionario."""
        persona = {}
        for col, field_name in enumerate(FIELD_NAMES):
            item = self.tableWidget.item(row, col)
            persona[field_name] = item.text() if item else ""
        return persona
        
    def _get_rows_to_process(self, selected_only):
        """Helper para obtener las filas a procesar (seleccionadas o todas)."""
        if selected_only:
            selected_rows = self.tableWidget.selectionModel().selectedRows()
            if not selected_rows:
                self.show_message("Sin selección", "Por favor, seleccione al menos una fila.")
                return []
            return sorted(list(set(index.row() for index in selected_rows)))
        else:
            return list(range(self.tableWidget.rowCount()))

    # --- Handlers de Eventos (Slots) ---

    def on_add(self):
        """(Altas) Abre el diálogo para añadir una nueva persona."""
        dialog = PersonDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            row_count = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_count)
            for col, item in enumerate(data):
                self.tableWidget.setItem(row_count, col, QTableWidgetItem(item))
            self.save_personas()
            self.show_message("Éxito", "Persona añadida correctamente.")

    def on_edit(self):
        """(Cambios) Abre el diálogo para editar la persona seleccionada."""
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        if not selected_rows:
            self.show_message("Error", "Seleccione una fila para editar.")
            return
        
        row = selected_rows[0].row()
        persona_data = [self.tableWidget.item(row, col).text() for col in range(self.tableWidget.columnCount())]
        
        dialog = PersonDialog(persona_data=persona_data, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            for col, item in enumerate(data):
                self.tableWidget.setItem(row, col, QTableWidgetItem(item))
            self.save_personas()
            self.show_message("Éxito", "Persona actualizada correctamente.")

    def on_delete(self):
        """(Bajas) Elimina las filas seleccionadas."""
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        if not selected_rows:
            self.show_message("Error", "Seleccione una o más filas para eliminar.")
            return
        
        reply = QMessageBox.warning(self, "Confirmar Eliminación",
                                    f"¿Está seguro de que desea eliminar {len(selected_rows)} registro(s)?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            rows_to_delete = sorted(list(set(index.row() for index in selected_rows)), reverse=True)
            for row in rows_to_delete:
                self.tableWidget.removeRow(row)
            self.save_personas()
            self.show_message("Éxito", "Persona(s) eliminada(s).")

    def on_generate(self, selected_only, gen_type):
        """Inicia la generación de archivos en un hilo separado."""
        row_indices = self._get_rows_to_process(selected_only)
        if not row_indices:
            return

        rows_data = [self.get_persona_dict(row) for row in row_indices]
        
        self.progress_dialog = QProgressDialog(f"Generando {len(rows_data)} archivos {gen_type.upper()}...", 
                                               "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setWindowTitle("Procesando...")
        
        self.worker = GenerationWorker(rows_data, self.template_oficio, gen_type)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.finished.connect(self.on_generation_finished)
        self.progress_dialog.canceled.connect(self.worker.stop) # Conectar cancelar
        self.progress_dialog.show()
        self.worker.start()

    def on_generation_finished(self, message):
        """Se ejecuta cuando el hilo de generación termina."""
        self.progress_dialog.setValue(100)
        self.progress_dialog.close()
        self.show_message("Proceso Terminado", 
                          f"{message}\nLos archivos se guardaron en la carpeta '{functions.OUTPUT_DIR}'.")
        self.worker = None

    def closeEvent(self, event):
        """Asegura que el hilo de trabajo se detenga al cerrar la app."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait() # Esperar a que el hilo termine
        event.accept()
