import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# cargar variables de .env 
load_dotenv()
DB_URL = os.getenv("DB_URL")

# Conectar a la base de datos
engine = create_engine(DB_URL)

# Definir clase base para las tablas
Base = declarative_base()

# Tabla informacion de los encuestados
class Encuestado(Base):
    __tablename__ = 'encuestado'

    id_encuestado = Column(Integer, primary_key = True, autoincrement = True)
    genero = Column(String)
    pais = Column(String)
    ocupacion = Column(String)
    autonomo = Column(Boolean, nullable=True)

# Tabla sobre historial clinico, antecendentes ... 
class SaludMental(Base):
    __tablename__ = 'salud_mental'

    id_salud_mental = Column(Integer, primary_key = True, autoincrement = True)
    id_encuestado = Column(Integer, ForeignKey('encuestado.id_encuestado'), nullable = False)
    antecedentes_familiares = Column(Boolean, nullable=True)
    ha_buscado_tratamiento = Column(Boolean, nullable=True)
    historial_salud_mental = Column(Enum('Si', 'No', 'Quizas', name='enum_historial_salud_mental'))
    cambios_humor = Column(Enum('Bajo', 'Medio', 'Alto', name='enum_cambios_humor'))
    dificultades_lidiar_desafios = Column(Boolean, nullable=True)
    estres_creciente = Column(Enum('Si', 'No', 'Quizas', name='enum_estres_creciente'))
    riesgo_salud = Column(Enum('Bajo', 'Medio', 'Alto', name='enum_riesgo_salud'))

# Tabla sobre los habitos de los encuestados
class Social(Base):
    __tablename__ = 'social'

    id_social = Column(Integer, primary_key = True, autoincrement = True)
    id_encuestado = Column(Integer, ForeignKey('encuestado.id_encuestado'), nullable = False)
    dias_en_casa = Column(String)
    cambio_habitos = Column(Enum('Si', 'No', 'Quizas', name='enum_cambio_habitos'))
    interes_laboral = Column(Enum('Si', 'No', 'Quizas', name='enum_interes_laboral'))
    dificultades_sociales = Column(Enum('Si', 'No', 'Quizas', name='enum_dificultades_sociales'))
    salud_mental_entrevista = Column(Enum('Si', 'No', 'Quizas', name='enum_salud_mental_entrevista'))
    opciones_atencion = Column(Enum('Si', 'No', 'No sabe', name='enum_opciones_atencion'))

if __name__ == "__main__":
    try:
        with engine.connect() as conexion:
            print("Conexion exitosa a la base de datos")
            # Crear las tablas en la base de datos
            Base.metadata.create_all(engine)
            print("Tablas creadas exitosamente.")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")