import csv
import os
from pylocres import LocresFile, LocalizedString

def locres_to_csv(locres_path, csv_path):
    """
    Convierte un archivo .locres de Unreal Engine a un archivo .csv.
    """
    try:
        print(f"    Cargando archivo: {locres_path}")
        locres_file = LocresFile.load(locres_path)

        print(f"    Creando archivo CSV: {csv_path}")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Escribir la cabecera
            writer.writerow(['Namespace', 'Key', 'SourceHash', 'OriginalText', 'TranslatedText'])

            # Escribir las entradas de texto
            for entry in locres_file.entries:
                writer.writerow([entry.namespace, entry.key, entry.source_hash, entry.text, ''])

        print(f"    Conversión a CSV completada.")

    except Exception as e:
        print(f"Error durante la conversión de .locres a .csv: {e}")
        # Crear un archivo CSV vacío en caso de error para no interrumpir el flujo
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Namespace', 'Key', 'SourceHash', 'OriginalText', 'TranslatedText', 'Error'])
            writer.writerow(['ERROR', str(e), '', '', '', ''])


def csv_to_locres(csv_path, locres_path):
    """
    Convierte un archivo .csv traducido de vuelta a un archivo .locres de Unreal Engine.
    """
    if not os.path.exists(csv_path):
        print(f"    AVISO: No se encontró el archivo {csv_path}, se omitirá la conversión.")
        return

    try:
        print(f"    Cargando archivo CSV: {csv_path}")

        new_entries = []
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Omitir la cabecera

            for row in reader:
                # Extraer datos de la fila
                namespace, key, source_hash, original_text, translated_text = row

                # Usar el texto traducido si existe, si no, usar el original
                final_text = translated_text if translated_text else original_text

                # Crear una nueva entrada de localización
                new_entries.append(LocalizedString(
                    namespace=namespace,
                    key=key,
                    source_hash=source_hash,
                    text=final_text
                ))

        # Crear un nuevo archivo .locres y añadir las entradas
        new_locres_file = LocresFile()
        new_locres_file.entries = new_entries

        # Guardar el nuevo archivo .locres
        print(f"    Guardando nuevo archivo .locres: {locres_path}")
        new_locres_file.save(locres_path)
        print(f"    Conversión a .locres completada.")

    except Exception as e:
        print(f"Error durante la conversión de .csv a .locres: {e}")
