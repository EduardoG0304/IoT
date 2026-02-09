# Práctica de la página 59 - Validación de correo electrónico

import re

def validar_correo(correo):
    """
    Valida si una cadena es una dirección de correo electrónico válida
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, correo) is not None

def ejecutar_practica_correo():
    print("\n" + "="*60)
    print("VALIDACIÓN DE CORREO ELECTRÓNICO - Página 59")
    print("="*60)
    
    print("\n--- Validación de Correo Electrónico ---")
    correo = input("Ingresa una dirección de correo electrónico: ")
    
    if validar_correo(correo):
        print(f"✓ '{correo}' es una dirección de correo válida.")
    else:
        print(f"✗ '{correo}' NO es una dirección de correo válida.")
    
    # Ejemplos de prueba
    print("\n--- Ejemplos de Prueba ---")
    ejemplos = [
        "usuario@example.com",
        "nombre.apellido@company.co.uk",
        "usuario@localhost",
        "correo@invalido",
        "test@sub.dominio.com"
    ]
    
    for ejemplo in ejemplos:
        es_valido = validar_correo(ejemplo)
        estado = "✓ VÁLIDO" if es_valido else "✗ INVÁLIDO"
        print(f"{estado}: {ejemplo}")
    
    input("\nPresione Enter para continuar...")