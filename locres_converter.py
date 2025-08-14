import csv
import struct
import os

# Esta es una implementación desde cero del parser de .locres.
# Se basa en la especificación inferida de varias fuentes.
# Puede necesitar ajustes para versiones específicas de Unreal Engine.

def read_string(f):
    """Lee una cadena de texto con prefijo de longitud del archivo."""
    length = struct.unpack('<i', f.read(4))[0]
    if length == 0:
        return ""
    # Unreal Engine usa longitudes negativas para cadenas UTF-16
    is_utf16 = length < 0
    if is_utf16:
        length = -length
        # Multiplicamos por 2 porque cada carácter UTF-16 ocupa 2 bytes
        utf16_bytes = f.read(length * 2)
        # Se decodifica y se elimina el terminador nulo
        return utf16_bytes.decode('utf-16-le').rstrip('\x00')
    else:
        # Se leen los bytes y se elimina el terminador nulo
        string_bytes = f.read(length)
        # Cambiamos a latin-1, que es más permisivo y no fallará en bytes desconocidos.
        return string_bytes.decode('latin-1').rstrip('\x00')

def write_string(f, text):
    """Escribe una cadena de texto con prefijo de longitud en el archivo."""
    # Usaremos UTF-8 por simplicidad al escribir.
    # NOTA: Para una compatibilidad perfecta, deberíamos respetar el formato original.
    if not text:
        f.write(struct.pack('<i', 0))
        return

    # Añadir terminador nulo y codificar
    encoded_text = (text + '\x00').encode('utf-8')
    length = len(encoded_text)

    # Escribir longitud y luego el texto
    f.write(struct.pack('<i', length))
    f.write(encoded_text)


def locres_to_csv(locres_path, csv_path):
    """
    Convierte un archivo .locres de Unreal Engine a un archivo .csv.
    """
    print(f"    Iniciando conversión (desde cero) de: {locres_path}")
    try:
        with open(locres_path, 'rb') as f, open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Namespace', 'Key', 'SourceHash', 'OriginalText', 'TranslatedText'])

            # --- Cabecera (Header) ---
            # Magic number (GUID) y versión. La investigación sugiere que la cabecera
            # a menudo consiste en un GUID de 16 bytes.
            header_bytes = f.read(16) # Saltar el GUID de 16 bytes

            # Leer el número de entradas de texto
            strings_count = struct.unpack('<i', f.read(4))[0]
            print(f"    Se encontraron {strings_count} cadenas de texto.")

            # --- Entradas de Texto ---
            for _ in range(strings_count):
                # Cada entrada tiene un namespace, una clave y el texto fuente
                namespace = read_string(f)
                key = read_string(f)
                source_hash = read_string(f) # El "hash" a menudo se almacena como una cadena

                # Escribimos la fila en el CSV
                writer.writerow([namespace, key, source_hash, key, '']) # Usamos la 'key' como texto original por ahora

        print(f"    Conversión a CSV completada: {csv_path}")

    except Exception as e:
        print(f"Error durante la conversión de .locres a .csv: {e}")
        # Crear un archivo CSV de error
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Error'])
            writer.writerow([str(e)])

def csv_to_locres(csv_path, locres_path):
    """
    Convierte un archivo .csv traducido de vuelta a un archivo .locres.
    NOTA: Esta función es un marcador de posición por ahora.
    Reconstruir el binario es complejo y requiere que la lectura sea 100% correcta primero.
    """
    print(f"    [AVISO] La función 'csv_to_locres' aún no está implementada en la versión desde cero.")
    if not os.path.exists(csv_path):
        print(f"    AVISO: No se encontró el archivo {csv_path}, se omitirá la conversión.")
        return

    # Aquí iría la lógica para leer el CSV y escribir el archivo binario .locres.
    # Esto es muy complejo y se hará una vez que la lectura (locres_to_csv) se valide.
    # Por ahora, crearemos un archivo vacío para no romper el flujo.
    with open(locres_path, 'w') as f:
        f.write("PENDIENTE DE IMPLEMENTACIÓN")

    print(f"    [SIMULACIÓN] Se crearía el archivo: {locres_path}")
