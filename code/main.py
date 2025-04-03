import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from prefect import flow, task
from sqlalchemy.orm import sessionmaker
from archivo_hash import obtener_archivos_nuevos, registrar_hash
from data_processing import read_csv, clean_data, transform_data, save_data
from load_data import read_clean_data, load_data_to_db

# cargar variables de .env 
load_dotenv()
DB_URL = os.getenv("DB_URL")
NEW_CSVS_PATH = os.getenv("NEW_CSVS_PATH")
TRANSFORMED_CSVS_PATH = os.getenv("TRANSFORMED_CSVS_PATH")

# Conectar a la base de datos
engine = create_engine(DB_URL)

@task
def procesar_archivos(carpeta):
    nuevos_archivos = obtener_archivos_nuevos(carpeta)
    return nuevos_archivos

@task
def transformar_datos(file_path, output_path):
    original_data = read_csv(file_path)
    cleaned_data = clean_data(original_data)
    transformed_data = transform_data(cleaned_data)
    save_data(transformed_data, output_path)

@task
def cargar_datos(output_data):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        data = read_clean_data(output_data)
        load_data_to_db(data, session)
    finally:
        session.close()

@flow
def etl_flow(carpeta):
    print("Buscando archivos nuevos...")
    archivos_nuevos = procesar_archivos(carpeta)

    if not archivos_nuevos:
        print("No hay archivos nuevos para procesar.")
        return
    
    for file_path, file_name, file_hash in archivos_nuevos:
        print(f"Procesando archivo: {file_path}")

        # hacer copia del archivo que tendrá los datos ya procesados
        nombre_base, extension = os.path.splitext(file_name)
        output_filename = f"{nombre_base}_procesado{extension}"
        output_path =  os.path.join(TRANSFORMED_CSVS_PATH, output_filename)

        transformar_datos(file_path, output_path)
        cargar_datos(output_path)
        
        registrar_hash(file_name, file_hash)
        print(f"Archivo procesado y registrado: {file_name}")

if __name__ == "__main__":
    etl_flow(NEW_CSVS_PATH)