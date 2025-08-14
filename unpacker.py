import subprocess
import os
import sys

# --- Configuración ---
UNREALPAK_EXE_PATH = ""

# --- Funciones Auxiliares ---

def find_unreal_pak():
    """Busca o pregunta por la ubicación de UnrealPak.exe."""
    if UNREALPAK_EXE_PATH and os.path.exists(UNREALPAK_EXE_PATH):
        return UNREALPAK_EXE_PATH

    print("--- Buscando UnrealPak.exe ---")
    path = input("Por favor, introduce la ruta completa a 'UnrealPak.exe':\n> ")

    if os.path.exists(path) and path.endswith("UnrealPak.exe"):
        print(f"UnrealPak.exe encontrado en: {path}")
        return path
    else:
        print("Error: La ruta proporcionada no es válida o no apunta a UnrealPak.exe.")
        sys.exit(1)

def get_pak_file():
    """Pregunta por la ubicación del archivo .pak del mod."""
    print("\n--- Selección del archivo .pak ---")
    path = input("Arrastra el archivo .pak del mod a esta ventana y presiona Enter, o pega la ruta:\n> ").strip('"')

    if os.path.exists(path) and path.endswith(".pak"):
        return path
    else:
        print("Error: El archivo no existe o no es un archivo .pak.")
        sys.exit(1)

def unpack_pak_file(unreal_pak_path, pak_file_path):
    """Desempaqueta el archivo .pak usando UnrealPak.exe."""
    print("\n--- Desempaquetando el mod ---")

    output_dir = os.path.join(os.path.dirname(pak_file_path), "unpacked_mod")
    os.makedirs(output_dir, exist_ok=True)

    command = [unreal_pak_path, pak_file_path, "-Extract", output_dir]

    print(f"Ejecutando comando: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"¡Éxito! Archivos extraídos en: {output_dir}")
        return output_dir
    except subprocess.CalledProcessError as e:
        print("Error al desempaquetar el archivo .pak.")
        print(f"Salida del comando:\n{e.stderr}")
        sys.exit(1)

def main():
    """Función principal que orquesta el desempaquetado."""
    unreal_pak = find_unreal_pak()
    pak_file = get_pak_file()

    unpacked_folder = unpack_pak_file(unreal_pak, pak_file)

    print(f"\n¡Desempaquetado completado! Los archivos se encuentran en la carpeta '{unpacked_folder}'.")
    print("Ahora puedes usar uno de los archivos .locres de esa carpeta con el script 'inspector.py'.")

if __name__ == "__main__":
    main()
