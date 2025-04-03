import os
import hashlib
from dotenv import load_dotenv

# cargar variables de .env 
load_dotenv()
HASH_FILE_PATH = os.getenv("HASH_FILE_PATH")
NEW_CSVS_PATH = os.getenv("NEW_CSVS_PATH")

# Generar hash único para identificar si el archivo ya se procesó
def obtener_hash_archivo(file_path):
    hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

# Devuelve lista de archivos csv nuevos. Genera su hash y lo compara con los ya registrados
def obtener_archivos_nuevos(folder_path):
    archivos_nuevos = []
    hashes_registrados = {}

    # cargar hashes existentes si el registro ya existe
    if os.path.exists(HASH_FILE_PATH):
        with open(HASH_FILE_PATH, 'r') as f:
            for linea in f:
                file_name, hash = linea.strip().split(":")
                hashes_registrados[file_name] = hash
    
    # Buscar archivos csv
    for archivo in os.listdir(folder_path):
        if archivo.endswith(".csv"):
            file_path = os.path.join(folder_path, archivo)
            # Calcular hash actual del archivo
            file_hash = obtener_hash_archivo(file_path)
            # Si el archivo es nuevo o se ha modificado, se devuelve
            if archivo not in hashes_registrados or hashes_registrados[archivo] != file_hash:
                archivos_nuevos.append((file_path, archivo, file_hash))
    
    return archivos_nuevos

# Registrar hash de archivos nuevos
def registrar_hash(file_name, file_hash):
    registros = {}
    
    if os.path.exists(HASH_FILE_PATH):
        with open(HASH_FILE_PATH, 'r') as f:
            for linea in f:
                file_name, hash = linea.strip().split(":")
                registros[file_name] = hash
    
    # Actualizar o añadir el nuevo hash
    registros[file_name] = file_hash

    # Escribir registros actualizados
    with open(HASH_FILE_PATH, 'w') as f:
        for file_name, hash in registros.items():
            f.write(f"{file_name}:{hash}\n")


def procesar_archivo(carpeta):
    """
    Procesa los archivos CSV nuevos o modificados.
    Registra su hash tras el procesamiento.
    """
    archivos_nuevos = obtener_archivos_nuevos(carpeta)

    if not archivos_nuevos:
        print("No hay archivos nuevos o modificados para procesar.")
        return

    for file_path, file_name, file_hash in archivos_nuevos:
        print(f"Procesando archivo: {file_path}")
        registrar_hash(file_name, file_hash)
        print(f"Archivo procesado y registrado: {file_path}")

if __name__ == "__main__":
    procesar_archivo(NEW_CSVS_PATH)
