from menu import mostrar_menu
from practica_numeros import ejecutar_practica_numeros
from practica_cadenas import ejecutar_practica_cadenas
from practica_correo import ejecutar_practica_correo
from practica_archivos import ejecutar_practica_archivos

def main():
    while True:
        opcion = mostrar_menu()
        
        if opcion == '1':
            ejecutar_practica_numeros()
        elif opcion == '2':
            ejecutar_practica_cadenas()
        elif opcion == '3':
            ejecutar_practica_correo()
        elif opcion == '4':
            ejecutar_practica_archivos()
        elif opcion == '5':
            print("¡Bye!")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()