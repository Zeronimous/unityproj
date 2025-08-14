import subprocess
import os
import sys
import locres_converter

# --- Configuración ---
# Deja esta variable vacía para que el script te pregunte la ubicación.
# O escribe la ruta completa a UnrealPak.exe si quieres que sea fija.
# Ejemplo: "C:/Program Files/Epic Games/UE_4.27/Engine/Binaries/Win64/UnrealPak.exe"
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

def convert_locres_to_csv(unpacked_dir):
    """Encuentra y convierte todos los archivos .locres a .csv."""
    print("\n--- Convirtiendo archivos de localización a CSV ---")
    locres_files = []
    for root, _, files in os.walk(unpacked_dir):
        for file in files:
            if file.endswith(".locres"):
                locres_files.append(os.path.join(root, file))

    if not locres_files:
        print("No se encontraron archivos .locres en el mod.")
        return [], ""

    print(f"Se encontraron {len(locres_files)} archivo(s) .locres.")
    for locres_path in locres_files:
        csv_path = locres_path.replace(".locres", ".csv")
        print(f"Convirtiendo {os.path.basename(locres_path)} -> {os.path.basename(csv_path)}")
        locres_converter.locres_to_csv(locres_path, csv_path)

    print("\n¡Archivos listos para traducir!")
    print("Por favor, abre los archivos .csv generados y traduce el texto.")
    print("Los encontrarás en la misma carpeta que los archivos originales.")

    return locres_files

def main():
    """Función principal que orquesta todo el proceso."""
    unreal_pak = find_unreal_pak()
    pak_file = get_pak_file()

    # 1. Desempaquetar
    unpacked_folder = unpack_pak_file(unreal_pak, pak_file)

    # 2. Convertir a CSV para traducción
    locres_files_to_process = convert_locres_to_csv(unpacked_folder)

    if not locres_files_to_process:
        print("\nProceso finalizado ya que no había archivos de localización que procesar.")
        sys.exit(0)

    # 3. Pausa para la traducción manual
    input("\n--- PAUSA --- \nPresiona Enter cuando hayas terminado de traducir los archivos .csv...\n")

    # 4. Convertir de vuelta a .locres
    print("\n--- Convirtiendo archivos CSV traducidos de vuelta a .locres ---")
    for locres_path in locres_files_to_process:
        csv_path = locres_path.replace(".locres", ".csv")
        print(f"Procesando {os.path.basename(csv_path)} -> {os.path.basename(locres_path)}")
        locres_converter.csv_to_locres(csv_path, locres_path)

    # 5. Re-empaquetar el mod
    print("\n--- Re-empaquetando el nuevo mod ---")
    response_file = create_response_file(unpacked_folder, pak_file)
    repack_pak_file(unreal_pak, pak_file, response_file)

    print("\n¡Proceso completado!")
    print("Se ha creado un nuevo archivo .pak con la traducción.")
    print("El archivo original no ha sido modificado.")


def create_response_file(unpacked_dir, original_pak_path):
    """Crea el archivo response.txt para el re-empaquetado."""
    response_file_path = os.path.join(os.path.dirname(unpacked_dir), "response.txt")

    # La ruta base para las rutas relativas dentro del pak.
    # Usualmente es tres niveles arriba del archivo de contenido.
    # Ejemplo: ../../../GameName/Content/....
    mount_point = "../../../"

    with open(response_file_path, "w") as f:
        for root, _, files in os.walk(unpacked_dir):
            for file in files:
                full_path = os.path.join(root, file)
                # La ruta relativa debe empezar desde la carpeta que contiene "Content"
                # Extraemos la parte de la ruta que viene después de "unpacked_mod"
                relative_path = os.path.relpath(full_path, unpacked_dir)

                # Construimos la ruta como la espera UnrealPak
                # Ejemplo: "../../../MyGame/Content/Blueprints/BP_Test.uasset"
                pak_path = os.path.join(mount_point, relative_path).replace("\\", "/")

                f.write(f'"{full_path}" "{pak_path}"\n')

    print(f"Archivo de respuesta creado en: {response_file_path}")
    return response_file_path

def repack_pak_file(unreal_pak_path, original_pak_path, response_file_path):
    """Crea un nuevo archivo .pak con los archivos modificados."""

    base_name = os.path.basename(original_pak_path)
    new_pak_name = base_name.replace(".pak", "_es.pak")
    new_pak_path = os.path.join(os.path.dirname(original_pak_path), new_pak_name)

    print(f"Creando nuevo archivo de mod: {new_pak_path}")

    command = [unreal_pak_path, new_pak_path, f"-Create={response_file_path}"]

    print(f"Ejecutando comando: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("¡Éxito! Nuevo archivo .pak creado.")
    except subprocess.CalledProcessError as e:
        print("Error al re-empaquetar el archivo .pak.")
        print(f"Salida del comando:\n{e.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    main()
