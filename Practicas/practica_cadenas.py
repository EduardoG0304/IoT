# Práctica de la página 59 - Manejo de cadenas

def capturar_cadena():
    """Captura una cadena de texto del usuario"""
    print("\n--- Captura de Cadena ---")
    return input("Ingresa una cadena de texto: ")

def es_mayuscula_inicio(cadena):
    """Verifica si la primera letra es mayúscula"""
    return cadena and cadena[0].isupper()

def contar_palabras(cadena):
    """Cuenta las palabras en la cadena"""
    return len(cadena.split())

def obtener_palabras(cadena):
    """Devuelve una lista con las palabras de la cadena"""
    return cadena.split()

def invertir_cadena(cadena):
    """Devuelve la cadena invertida"""
    return cadena[::-1]

def ultima_letra_mayuscula(cadena):
    """Pone la última letra de cada palabra en mayúscula"""
    palabras = cadena.split()
    resultado = []
    for palabra in palabras:
        if len(palabra) > 0:
            palabra_mod = palabra[:-1] + palabra[-1].upper()
            resultado.append(palabra_mod)
        else:
            resultado.append(palabra)
    return ' '.join(resultado)

def ejecutar_practica_cadenas():
    print("\n" + "="*60)
    print("PRÁCTICA CON CADENAS - Página 59")
    print("="*60)
    
    cadena = capturar_cadena()
    
    if not cadena:
        print("No se capturó ninguna cadena.")
        return
    
    print(f"\nCadena original: '{cadena}'")
    
    # 1. Verificar si la primera letra es mayúscula
    resultado1 = es_mayuscula_inicio(cadena)
    print(f"1. ¿Primera letra es mayúscula? {resultado1}")
    
    # 2. Contar palabras
    resultado2 = contar_palabras(cadena)
    print(f"2. Número de palabras: {resultado2}")
    
    # 3. Lista de palabras
    resultado3 = obtener_palabras(cadena)
    print(f"3. Lista de palabras: {resultado3}")
    
    # 4. Cadena invertida
    resultado4 = invertir_cadena(cadena)
    print(f"4. Cadena invertida: '{resultado4}'")
    
    # 5. Última letra en mayúscula
    resultado5 = ultima_letra_mayuscula(cadena)
    print(f"5. Última letra mayúscula: '{resultado5}'")
    
    input("\nPresione Enter para continuar...")