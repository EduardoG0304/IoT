
import os
import sys
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

# --- Importaciones para PDF (ReportLab) ---
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
except ImportError:
    print("Error: 'reportlab' no está instalado. Ejecute: pip install reportlab")
    sys.exit(1)

# --- Importaciones para Word (python-docx) ---
try:
    from docx import Document
    from docx.shared import Pt
except ImportError:
    print("Error: 'python-docx' no está instalado. Ejecute: pip install python-docx")
    sys.exit(1)

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
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"Directorio '{OUTPUT_DIR}' creado.")

        if not os.path.exists(PERSONAS_FILE):
            with open(PERSONAS_FILE, "w", encoding="utf-8") as f:
                f.write(PERSONAS_EJEMPLO)
            print(f"Archivo '{PERSONAS_FILE}' creado con datos de ejemplo.")

        if not os.path.exists(OFICIO_FILE):
            with open(OFICIO_FILE, "w", encoding="utf-8") as f:
                f.write(OFICIO_PLANTILLA)
            print(f"Archivo '{OFICIO_FILE}' creado con plantilla de ejemplo.")
    except Exception as e:
        print(f"Error durante la configuración inicial: {e}")

# --- Funciones de Lectura/Escritura de Datos ---

def load_template_content():
    """Carga la plantilla del oficio y la devuelve como string."""
    try:
        with open(OFICIO_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{OFICIO_FILE}'")
        return "ERROR: PLANTILLA NO ENCONTRADA"
    except Exception as e:
        print(f"Error al leer la plantilla: {e}")
        return f"ERROR: {e}"

def load_personas_data():
    """Lee 'personas.txt' y devuelve una lista de listas."""
    data = []
    try:
        with open(PERSONAS_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split('|')
                if len(datos) == len(FIELD_NAMES):
                    data.append(datos)
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo '{PERSONAS_FILE}'.")
    except Exception as e:
        print(f"Error al cargar personas: {e}")
    return data

def save_personas_data(data: list[list[str]]):
    """Guarda la lista de listas en 'personas.txt'."""
    try:
        with open(PERSONAS_FILE, "w", encoding="utf-8") as f:
            for fila in data:
                f.write("|".join(fila) + "\n")
    except Exception as e:
        print(f"No se pudo guardar el archivo de personas: {e}")
        # Opcional: relanzar la excepción si es crítico
        raise

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
        self.is_running = True

    def run(self):
        total = len(self.rows_data)
        for i, persona_dict in enumerate(self.rows_data):
            if not self.is_running:
                break # Salir si el usuario canceló
            
            try:
                self.generate_file(persona_dict)
            except Exception as e:
                print(f"Error generando para {persona_dict.get('nombre')}: {e}")
            
            self.progress.emit(int((i + 1) * 100 / total))

        if self.is_running:
            self.finished.emit(f"Generación de {total} archivos {self.gen_type.upper()} completada.")
        else:
            self.finished.emit("Generación cancelada.")

    def stop(self):
        self.is_running = False

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
            
            lines = oficio_str.split('\n')
            for line in lines:
                doc.add_paragraph(line)
            
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Arial'
                    run.font.size = Pt(11)
            
            doc.save(filepath)
