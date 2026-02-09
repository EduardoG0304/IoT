"""
Aplicación de Combinación de Correspondencia con GUI (PyQt6)

Esta aplicación permite gestionar una lista de personas (Altas, Bajas, Cambios)
y generar oficios en formatos TXT, PDF y DOCX.
"""
import sys
import os
from datetime import datetime

# --- Importaciones de PyQt6 ---
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QAbstractItemView,
    QProgressDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# --- Importaciones para PDF (ReportLab) ---
# Se necesita: pip install reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# --- Importaciones para Word (python-docx) ---
# Se necesita: pip install python-docx
from docx import Document
from docx.shared import Pt

# --- Constantes ---
PERSONAS_FILE = "personas.txt"
OFICIO_FILE = "oficio.txt"
OUTPUT_DIR = "oficios_generados"

# Nombres de los campos (el orden es importante)
FIELD_NAMES = [
    'nombre', 'apellido1', 'apellido2', 'cargo', 'empresa', 'calle',
    'numeroExt', 'numeroInt', 'colonia', 'municipio', 'estado',
    'codigoPostal', 'telefono', 'correoElectronico', 'fechaNacimiento'
]

# --- Texto para los archivos base ---

PERSONAS_EJEMPLO = """Juan|Pérez|García|Gerente|Tech Solutions|Av. Principal|123||Centro|Ciudad|Estado|12345|555-1234|juan@tech.com|15-05-1980
María|López|Hernández|Desarrolladora|Innovation Corp|Calle Secundaria|456|A|Norte|Municipio|Estado|54321|555-5678|maria@innovation.com|20-08-1990
Carlos|Gómez|Martínez|Analista|Data Dynamics|Boulevard Central|789|Of. 3|Sur|Metrópolis|Estado|67890|555-9012|carlos@data.com|10-11-1995
"""

OFICIO_PLANTILLA = """OFICIO: INVITACIÓN A REUNIÓN

A: [NOMBRE] [APELLIDO1] [APELLIDO2]
CARGO: [CARGO]
EMPRESA: [EMPRESA]
DIRECCIÓN: [CALLE] [NUMEROEXT] [NUMEROINT], [COLONIA], [MUNICIPIO], [ESTADO] [CODIGOPOSTAL]

Por medio del presente, me dirijo a usted para invitarlo cordialmente a la reunión de trabajo que se llevará a cabo el próximo viernes en nuestras instalaciones.

Agradecemos de antemano su valiosa participación.

Para cualquier aclaración, puede contactarnos al teléfono: [TELEFONO] o al correo: [CORREOELECTRONICO]

Atentamente,
El Comité Organizador

Fecha: [FECHA_ACTUAL]
"""

# --- Funciones de Configuración Inicial ---

def setup_files_and_dirs():
    """Crea los archivos y directorios base si no existen."""
    
    # Crear directorio de salida
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directorio '{OUTPUT_DIR}' creado.")

    # Crear archivo de personas
    if not os.path.exists(PERSONAS_FILE):
        with open(PERSONAS_FILE, "w", encoding="utf-8") as f:
            f.write(PERSONAS_EJEMPLO)
        print(f"Archivo '{PERSONAS_FILE}' creado con datos de ejemplo.")

    # Crear archivo de oficio
    if not os.path.exists(OFICIO_FILE):
        with open(OFICIO_FILE, "w", encoding="utf-8") as f:
            f.write(OFICIO_PLANTILLA)
        print(f"Archivo '{OFICIO_FILE}' creado con plantilla de ejemplo.")

# --- Clase de Diálogo para Alta/Cambio ---

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
                # Modo "Cambio" (Editar)
                line_edit.setText(persona_data[i])
            self.fields[field_name] = line_edit
            layout.addRow(f"{field_name.capitalize()}:", line_edit)

        # Botones de OK y Cancelar
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        """Devuelve los datos de los campos como una lista."""
        return [self.fields[field_name].text() for field_name in FIELD_NAMES]

# --- Hilo de Trabajo para Generación ---

class GenerationWorker(QThread):
    """
    Hilo de trabajo para generar documentos sin congelar la GUI.
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    
    def __init__(self, rows_data, template, gen_type):
        super().__init__()
        self.rows_data = rows_data
        self.template = template
        self.gen_type = gen_type # 'txt', 'pdf', 'docx'

    def run(self):
        total = len(self.rows_data)
        for i, persona_dict in enumerate(self.rows_data):
            try:
                self.generate_file(persona_dict)
            except Exception as e:
                print(f"Error generando para {persona_dict.get('nombre')}: {e}")
            
            # Actualizar progreso
            self.progress.emit(int((i + 1) * 100 / total))

        self.finished.emit(f"Generación de {total} archivos {self.gen_type.upper()} completada.")

    def _generate_oficio_string(self, persona_dict):
        """Genera el texto del oficio reemplazando placeholders."""
        oficio = self.template
        
        # Agregar edad calculada
        try:
            fecha_nac = datetime.strptime(persona_dict.get('fechaNacimiento', ''), '%d-%m-%Y')
            hoy = datetime.now()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            persona_dict['edad'] = str(edad)
        except:
            persona_dict['edad'] = "N/A"
            
        # Reemplazar placeholders
        for key, value in persona_dict.items():
            oficio = oficio.replace(f'[{key.upper()}]', value)
        
        oficio = oficio.replace('[FECHA_ACTUAL]', datetime.now().strftime('%d-%m-%Y'))
        return oficio

    def generate_file(self, persona_dict):
        """Función central que genera el archivo del tipo correcto."""
        nombre_base = f"{persona_dict.get('nombre', 'N')}_{persona_dict.get('apellido1', 'A')}"
        oficio_str = self._generate_oficio_string(persona_dict)
        
        if self.gen_type == 'txt':
            filepath = os.path.join(OUTPUT_DIR, f"oficio_{nombre_base}.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(oficio_str)
        
        elif self.gen_type == 'pdf':
            filepath = os.path.join(OUTPUT_DIR, f"oficio_{nombre_base}.pdf")
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            style_body = styles['BodyText']
            story = []
            
            # Convertir saltos de línea en párrafos de ReportLab
            lines = oficio_str.split('\n')
            for line in lines:
                if line == "":
                    story.append(Spacer(1, 0.1 * inch))
                else:
                    story.append(Paragraph(line, style_body))
            
            doc.build(story)

        elif self.gen_type == 'docx':
            filepath = os.path.join(OUTPUT_DIR, f"oficio_{nombre_base}.docx")
            doc = Document()
            
            # Convertir saltos de línea en párrafos de Word
            lines = oficio_str.split('\n')
            for line in lines:
                doc.add_paragraph(line)
            
            # Opcional: Estilizar fuente
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Arial'
                    run.font.size = Pt(11)
            
            doc.save(filepath)

# --- Ventana Principal de la Aplicación ---

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Combinación de Correspondencia")
        self.setGeometry(100, 100, 1000, 600)

        self.template_oficio = ""
        self.progress_dialog = None

        # --- Layout Principal ---
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

        # --- Botones de CRUD ---
        crud_layout = QHBoxLayout()
        self.btn_add = QPushButton("Añadir (Altas)")
        self.btn_edit = QPushButton("Editar (Cambios)")
        self.btn_delete = QPushButton("Eliminar (Bajas)")
        
        crud_layout.addWidget(self.btn_add)
        crud_layout.addWidget(self.btn_edit)
        crud_layout.addWidget(self.btn_delete)
        crud_layout.addStretch()
        main_layout.addLayout(crud_layout)

        # --- Botones de Generación TXT ---
        gen_txt_layout = QHBoxLayout()
        self.btn_gen_txt_sel = QPushButton("Generar TXT (Seleccionado)")
        self.btn_gen_txt_all = QPushButton("Generar TXT (Todos)")
        gen_txt_layout.addWidget(self.btn_gen_txt_sel)
        gen_txt_layout.addWidget(self.btn_gen_txt_all)
        gen_txt_layout.addStretch()
        main_layout.addLayout(gen_txt_layout)

        # --- Botones de Generación PDF (Extra) ---
        gen_pdf_layout = QHBoxLayout()
        self.btn_gen_pdf_sel = QPushButton("Generar PDF (Seleccionado)")
        self.btn_gen_pdf_all = QPushButton("Generar PDF (Todos)")
        gen_pdf_layout.addWidget(self.btn_gen_pdf_sel)
        gen_pdf_layout.addWidget(self.btn_gen_pdf_all)
        gen_pdf_layout.addStretch()
        main_layout.addLayout(gen_pdf_layout)

        # --- Botones de Generación DOCX (Extra) ---
        gen_docx_layout = QHBoxLayout()
        self.btn_gen_docx_sel = QPushButton("Generar DOCX (Seleccionado)")
        self.btn_gen_docx_all = QPushButton("Generar DOCX (Todos)")
        gen_docx_layout.addWidget(self.btn_gen_docx_sel)
        gen_docx_layout.addWidget(self.btn_gen_docx_all)
        gen_docx_layout.addStretch()
        main_layout.addLayout(gen_docx_layout)

        # --- Conectar Señales ---
        self.btn_add.clicked.connect(self.on_add)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_delete.clicked.connect(self.on_delete)
        
        # Conexiones con lambda para pasar parámetros
        self.btn_gen_txt_sel.clicked.connect(lambda: self.on_generate(selected_only=True, gen_type='txt'))
        self.btn_gen_txt_all.clicked.connect(lambda: self.on_generate(selected_only=False, gen_type='txt'))
        
        self.btn_gen_pdf_sel.clicked.connect(lambda: self.on_generate(selected_only=True, gen_type='pdf'))
        self.btn_gen_pdf_all.clicked.connect(lambda: self.on_generate(selected_only=False, gen_type='pdf'))
        
        self.btn_gen_docx_sel.clicked.connect(lambda: self.on_generate(selected_only=True, gen_type='docx'))
        self.btn_gen_docx_all.clicked.connect(lambda: self.on_generate(selected_only=False, gen_type='docx'))

        # --- Carga Inicial ---
        self.load_template()
        self.load_personas()

    def show_message(self, title, message):
        """Muestra un diálogo de mensaje."""
        QMessageBox.information(self, title, message)

    def load_template(self):
        """Carga la plantilla del oficio en memoria."""
        try:
            with open(OFICIO_FILE, "r", encoding="utf-8") as f:
                self.template_oficio = f.read()
        except FileNotFoundError:
            self.show_message("Error", f"No se encontró el archivo '{OFICIO_FILE}'")
            self.template_oficio = "ERROR: PLANTILLA NO ENCONTRADA"
        except Exception as e:
            self.show_message("Error", f"Error al leer la plantilla: {e}")

    def load_personas(self):
        """Lee 'personas.txt' y puebla la tabla."""
        self.tableWidget.setRowCount(0) # Limpiar tabla
        try:
            with open(PERSONAS_FILE, "r", encoding="utf-8") as f:
                for row_idx, linea in enumerate(f):
                    datos = linea.strip().split('|')
                    if len(datos) == len(FIELD_NAMES):
                        self.tableWidget.insertRow(row_idx)
                        for col_idx, item in enumerate(datos):
                            self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(item))
            self.tableWidget.resizeColumnsToContents()
        except FileNotFoundError:
            self.show_message("Advertencia", f"No se encontró el archivo '{PERSONAS_FILE}'. Se creará uno nuevo al guardar.")
        except Exception as e:
            self.show_message("Error", f"Error al cargar personas: {e}")

    def save_personas(self):
        """Guarda el contenido de la tabla en 'personas.txt'."""
        try:
            with open(PERSONAS_FILE, "w", encoding="utf-8") as f:
                for row in range(self.tableWidget.rowCount()):
                    datos = []
                    for col in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, col)
                        datos.append(item.text() if item else "")
                    f.write("|".join(datos) + "\n")
        except Exception as e:
            self.show_message("Error", f"No se pudo guardar el archivo de personas: {e}")

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
            # Obtener índices de fila únicos
            return sorted(list(set(index.row() for index in selected_rows)))
        else:
            return list(range(self.tableWidget.rowCount()))

    # --- Funciones de Botones (CRUD) ---

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
        
        # Solo editar la primera fila seleccionada
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
            # Obtener índices de fila únicos y ordenarlos en reversa para evitar problemas
            rows_to_delete = sorted(list(set(index.row() for index in selected_rows)), reverse=True)
            
            for row in rows_to_delete:
                self.tableWidget.removeRow(row)
            
            self.save_personas()
            self.show_message("Éxito", "Persona(s) eliminada(s).")

    # --- Funciones de Botones (Generación) ---

    def on_generate(self, selected_only, gen_type):
        """Método principal para iniciar la generación de archivos."""
        row_indices = self._get_rows_to_process(selected_only)
        if not row_indices:
            return

        rows_data = [self.get_persona_dict(row) for row in row_indices]
        
        # Configurar diálogo de progreso
        self.progress_dialog = QProgressDialog(f"Generando {len(rows_data)} archivos {gen_type.upper()}...", 
                                               "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setWindowTitle("Procesando...")
        self.progress_dialog.show()

        # Iniciar hilo de trabajo
        self.worker = GenerationWorker(rows_data, self.template_oficio, gen_type)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.finished.connect(self.on_generation_finished)
        self.progress_dialog.canceled.connect(self.worker.terminate)
        self.worker.start()

    def on_generation_finished(self, message):
        """Se ejecuta cuando el hilo de generación termina."""
        self.progress_dialog.setValue(100)
        self.progress_dialog.close()
        self.show_message("Generación Completa", 
                          f"{message}\nLos archivos se guardaron en la carpeta '{OUTPUT_DIR}'.")
        self.worker = None

# --- Punto de Entrada ---
if __name__ == "__main__":
    # 1. Asegurarse de que los archivos base existen
    setup_files_and_dirs()
    
    # 2. Iniciar la aplicación Qt
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
