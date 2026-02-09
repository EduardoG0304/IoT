# Práctica de la página 86 - Combinar correspondencia

import os
from datetime import datetime

def crear_archivo_personas():
    """Crea el archivo de personas si no existe"""
    if not os.path.exists("personas.txt"):
        with open("personas.txt", "w", encoding="utf-8") as f:
            f.write("Juan|Pérez|García|Gerente|Tech Solutions|Av. Principal|123||Centro|Ciudad|Estado|12345|555-1234|juan@tech.com|15-05-1980\n")
            f.write("María|López|Hernández|Desarrolladora|Innovation Corp|Calle Secundaria|456|A|Norte|Municipio|Estado|54321|555-5678|maria@innovation.com|20-08-1990\n")
        print("Archivo 'personas.txt' creado con datos de ejemplo.")

def crear_archivo_oficio():
    """Crea el archivo de oficio si no existe"""
    if not os.path.exists("oficio.txt"):
        with open("oficio.txt", "w", encoding="utf-8") as f:
            f.write("""OFICIO: INVITACIÓN A REUNIÓN

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
""")
        print("Archivo 'oficio.txt' creado con formato base.")

def leer_personas():
    """Lee el archivo de personas y devuelve una lista de diccionarios"""
    personas = []
    try:
        with open("personas.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split('|')
                if len(datos) >= 15:
                    persona = {
                        'nombre': datos[0],
                        'apellido1': datos[1],
                        'apellido2': datos[2],
                        'cargo': datos[3],
                        'empresa': datos[4],
                        'calle': datos[5],
                        'numeroExt': datos[6],
                        'numeroInt': datos[7],
                        'colonia': datos[8],
                        'municipio': datos[9],
                        'estado': datos[10],
                        'codigoPostal': datos[11],
                        'telefono': datos[12],
                        'correoElectronico': datos[13],
                        'fechaNacimiento': datos[14]
                    }
                    # Calcular edad
                    try:
                        fecha_nac = datetime.strptime(persona['fechaNacimiento'], '%d-%m-%Y')
                        hoy = datetime.now()
                        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                        persona['edad'] = str(edad)
                    except:
                        persona['edad'] = "N/A"
                    
                    personas.append(persona)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'personas.txt'")
    return personas

def generar_oficio(persona):
    """Genera un oficio personalizado para una persona"""
    try:
        with open("oficio.txt", "r", encoding="utf-8") as f:
            plantilla = f.read()
        
        # Reemplazar placeholders
        oficio = plantilla
        for key, value in persona.items():
            oficio = oficio.replace(f'[{key.upper()}]', value)
        
        oficio = oficio.replace('[FECHA_ACTUAL]', datetime.now().strftime('%d-%m-%Y'))
        
        return oficio
    except FileNotFoundError:
        return "Error: No se encontró el archivo 'oficio.txt'"

def ejecutar_practica_archivos():
    print("\n" + "="*60)
    print("COMBINAR CORRESPONDENCIA - Página 86")
    print("="*60)
    
    # Crear archivos si no existen
    crear_archivo_personas()
    crear_archivo_oficio()
    
    # Leer personas
    personas = leer_personas()
    
    if not personas:
        print("No se encontraron personas en el archivo.")
        return
    
    print(f"\nSe encontraron {len(personas)} personas en el archivo.")
    
    # Generar oficios
    print("\nGenerando oficios...")
    for i, persona in enumerate(personas, 1):
        oficio = generar_oficio(persona)
        
        # Guardar oficio individual
        nombre_archivo = f"oficio_{persona['nombre']}_{persona['apellido1']}.txt"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(oficio)
        
        print(f"✓ Oficio {i} generado: {nombre_archivo}")
    
    # Generar oficio combinado
    with open("oficios_combinados.txt", "w", encoding="utf-8") as f:
        for persona in personas:
            oficio = generar_oficio(persona)
            f.write(oficio)
            f.write("\n" + "="*50 + "\n\n")
    
    print("✓ Archivo combinado generado: oficios_combinados.txt")
    print("\n--- Archivos generados ---")
    print("• personas.txt - Datos de las personas")
    print("• oficio.txt - Plantilla del oficio")
    print("• oficio_[Nombre]_[Apellido].txt - Oficios individuales")
    print("• oficios_combinados.txt - Todos los oficios en un archivo")
    
    input("\nPresione Enter para continuar...")