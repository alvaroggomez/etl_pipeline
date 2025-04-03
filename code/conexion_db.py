import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# cargar variables de .env 
load_dotenv()
DB_URL = os.getenv("DB_URL")

# Conectar a la base de datos
engine = create_engine(DB_URL)

# Prueba de conexion a la base de datos
if __name__ == "__main__":
    try:
        with engine.connect() as conexion:
            print("Conexión exitosa a la base de datos")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")