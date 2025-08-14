import sys
from pylocres import LocresFile

def inspect_locres(file_path):
    """
    Carga un archivo .locres e imprime información sobre su estructura interna.
    """
    print(f"--- Inspeccionando el archivo: {file_path} ---")

    try:
        # Cargar el archivo .locres
        locres_file = LocresFile.load(file_path)
        print("Archivo .locres cargado con éxito.")

        # Comprobar si tiene entradas
        if not locres_file.entries:
            print("El archivo no contiene ninguna entrada de texto.")
            return

        print(f"El archivo contiene {len(locres_file.entries)} entradas.")

        # Obtener la primera entrada para inspeccionarla
        first_entry = locres_file.entries[0]

        # Imprimir el tipo/clase de la entrada. ¡Esto es lo que necesito!
        print("\n--- ¡INFORMACIÓN CLAVE! ---")
        print(f"El tipo de objeto de las entradas es: {type(first_entry)}")

        # Imprimir los atributos y métodos del objeto de entrada
        print("\n--- Atributos y métodos del objeto de entrada ---")
        print(dir(first_entry))
        print("\n--- Fin de la inspección ---")

    except Exception as e:
        print(f"\nSe produjo un error durante la inspección: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Por favor, proporciona la ruta a un archivo .locres.")
        print("Uso: python inspector.py <ruta_al_archivo.locres>")
    else:
        file_to_inspect = sys.argv[1]
        inspect_locres(file_to_inspect)
