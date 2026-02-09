# Práctica de la página 58 - Manejo de números y listas

def capturar_numeros():
    """Captura números del usuario y los almacena en una lista"""
    numeros = []
    print("\n--- Captura de Números ---")
    print("Ingresa números (escribe 'fin' para terminar):")
    
    while True:
        entrada = input("Número: ")
        if entrada.lower() == 'fin':
            break
        try:
            numeros.append(int(entrada))
        except ValueError:
            print("Por favor ingresa un número válido")
    
    return numeros

def calcular_cubo(lista_numeros):
    """Calcula el cubo de cada elemento de la lista"""
    return [x ** 3 for x in lista_numeros]

def ejecutar_practica_numeros():
    print("\n" + "="*60)
    print("PRÁCTICA CON NÚMEROS - Página 58")
    print("="*60)
    
    # Capturar números
    numeros = capturar_numeros()
    
    if not numeros:
        print("No se capturaron números.")
        return
    
    print(f"\nLista original: {numeros}")
    
    # 1. Sublista de 2 elementos de la mitad
    if len(numeros) >= 2:
        mitad = len(numeros) // 2
        sublista = numeros[mitad-1:mitad+1]
        print(f"1. Sublista de la mitad: {sublista}")
    else:
        print("1. La lista debe tener al menos 2 elementos")
    
    # 2. Primer y último elemento
    print(f"2. Primer y último elemento: {numeros[0]}, {numeros[-1]}")
    
    # 3. Duplicar lista
    numeros.extend(numeros)
    print(f"3. Lista duplicada: {numeros}")
    
    # 4. Ordenar ascendente
    numeros_asc = sorted(numeros)
    print(f"4. Orden ascendente: {numeros_asc}")
    
    # 5. Ordenar descendente
    numeros_desc = sorted(numeros, reverse=True)
    print(f"5. Orden descendente: {numeros_desc}")
    
    # 6. Calcular cubos
    cubos = calcular_cubo(numeros)
    print(f"6. Cubos de los elementos: {cubos}")
    
    input("\nPresione Enter para continuar...")