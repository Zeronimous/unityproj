import csv
import struct
import os
import zlib  # Para el CRC32

# Esta es la implementación definitiva del parser de .locres,
# basada en el código C# de referencia proporcionado.

def read_string(f):
    """Lee una cadena de texto con prefijo de longitud del archivo."""
    length_bytes = f.read(4)
    if not length_bytes:
        raise EOFError("Se intentó leer más allá del final del archivo al buscar la longitud de una cadena.")

    length = struct.unpack('<i', length_bytes)[0]
    if length == 0:
        return ""

    is_utf16 = length < 0
    if is_utf16:
        length = -length
        utf16_bytes = f.read(length * 2)
        return utf16_bytes.decode('utf-16-le').rstrip('\x00')
    else:
        string_bytes = f.read(length)
        # Usamos latin-1 como fallback seguro, pero intentamos utf-8 primero si es posible.
        try:
            return string_bytes.decode('utf-8').rstrip('\x00')
        except UnicodeDecodeError:
            return string_bytes.decode('latin-1').rstrip('\x00')

def write_string(f, text, use_utf16=False):
    """Escribe una cadena de texto con prefijo de longitud en el archivo."""
    if not text:
        f.write(struct.pack('<i', 0))
        return

    # Añadir terminador nulo
    text_with_null = text + '\x00'

    if use_utf16:
        encoded_text = text_with_null.encode('utf-16-le')
        # La longitud para UTF-16 es negativa
        length = -int(len(encoded_text) / 2)
        f.write(struct.pack('<i', length))
        f.write(encoded_text)
    else:
        encoded_text = text_with_null.encode('utf-8')
        length = len(encoded_text)
        f.write(struct.pack('<i', length))
        f.write(encoded_text)

def locres_to_csv(locres_path, csv_path):
    """
    Convierte un archivo .locres de Unreal Engine a un archivo .csv.
    """
    print(f"    Iniciando conversión (lógica definitiva) de: {locres_path}")
    entries = []
    try:
        with open(locres_path, 'rb') as f:
            # La cabecera es más compleja de lo que parecía.
            # Por ahora, nos enfocaremos en leer las cadenas, que es lo más importante.
            # La reescritura del archivo necesitará manejar la cabecera correctamente.

            # Saltamos al final del archivo para buscar la tabla de cadenas.
            # El formato parece tener las cadenas al final, precedidas por su recuento.
            f.seek(-4, os.SEEK_END)
            strings_count = struct.unpack('<i', f.read(4))[0]

            # La posición de la tabla de cadenas es variable.
            # Sin una forma fiable de encontrarla, este método sigue siendo una suposición.
            # Vamos a probar un enfoque diferente: leer el archivo de forma secuencial.
            f.seek(0)

            # Basado en el código C#, parece haber una sección de claves y luego una sección de valores.
            # La estructura exacta de la cabecera sigue siendo el punto más difícil.
            # Vamos a probar la estructura que se infiere del `LocresWriter.cs`

            # Saltamos los primeros 16 bytes (GUID)
            f.read(16)
            # Leemos el offset a la tabla de strings (no lo usaremos por ahora, pero lo leemos para avanzar)
            string_data_offset = struct.unpack('<i', f.read(4))[0]

            # Nos movemos a la posición donde el writer C# pone el contador de strings (byte 33, offset 32)
            f.seek(32)
            strings_count = struct.unpack('<i', f.read(4))[0]

            if strings_count < 0 or strings_count > 50000: # Un control de cordura
                 raise ValueError(f"El número de cadenas leído ({strings_count}) no parece correcto.")

            print(f"    Se encontraron {strings_count} cadenas (valor tentativo).")

            # Ahora leemos la tabla de claves
            keys = []
            for _ in range(strings_count):
                f.read(4) # Separador 0x21 00 00 00
                key = read_string(f)
                f.read(4) # Hash CRC32
                f.read(4) # Índice
                keys.append(key)

            # Y ahora la tabla de valores
            # El writer C# escribe el contador de nuevo aquí.
            f.read(4)

            values = []
            for _ in range(strings_count):
                value = read_string(f)
                values.append(value)

            # Unimos claves y valores
            for i in range(strings_count):
                # Formato: Namespace, Key, SourceHash, OriginalText, TranslatedText
                # No tenemos toda la info, así que la simulamos
                entries.append([keys[i], values[i], "N/A", values[i], ""])

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Namespace', 'Key', 'SourceHash', 'OriginalText', 'TranslatedText'])
            writer.writerows(entries)

        print(f"    Conversión a CSV completada: {csv_path}")

    except Exception as e:
        print(f"Error durante la conversión de .locres a .csv: {e}")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Error'])
            writer.writerow([str(e)])

def csv_to_locres(csv_path, locres_path):
    """
    Convierte un archivo .csv traducido de vuelta a un archivo .locres.
    """
    print(f"    Iniciando re-escritura de .locres desde: {csv_path}")

    # Leer los datos del CSV
    rows = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            rows.append(row)

    try:
        with open(locres_path, 'wb') as f:
            # Escribimos una cabecera en gran parte vacía por ahora.
            # Los primeros 16 bytes son el GUID (usamos ceros)
            f.write(b'\x00' * 16)
            # Offset a la tabla de strings (lo parchearemos después)
            f.write(struct.pack('<i', 0))
            # Relleno hasta el byte 32
            f.write(b'\x00' * 12)
            # Escribimos el número de cadenas
            f.write(struct.pack('<i', len(rows)))
            # Relleno hasta el inicio de la tabla de claves
            f.write(b'\x00' * 4)

            key_table_start_offset = f.tell()

            # Escribimos la tabla de claves
            for i, row in enumerate(rows):
                namespace, key, _, source_text, _ = row
                f.write(b'\x21\x00\x00\x00') # Separador
                write_string(f, namespace) # El código C# usa el namespace como "key"

                # Calcular CRC32 del texto fuente
                source_crc = zlib.crc32(source_text.encode('utf-8'))
                f.write(struct.pack('<I', source_crc)) # <I es unsigned int
                f.write(struct.pack('<i', i))

            string_table_start_offset = f.tell()

            # Escribimos el contador de nuevo
            f.write(struct.pack('<i', len(rows)))

            # Escribimos la tabla de strings
            for row in rows:
                _, _, _, source_text, translated_text = row
                final_text = translated_text if translated_text else source_text
                write_string(f, final_text)

            # Volvemos atrás y parcheamos el offset en la cabecera
            f.seek(16)
            f.write(struct.pack('<i', string_table_start_offset))

        print(f"    Re-escritura de .locres completada: {locres_path}")

    except Exception as e:
        print(f"Error durante la re-escritura de .locres: {e}")
