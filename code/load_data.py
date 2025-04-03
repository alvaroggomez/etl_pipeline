import pandas as pd
from create_tables import Encuestado, SaludMental, Social

# Leer datos limpios del CSV
def read_clean_data(file_path):
    return pd.read_csv(file_path)

# Cargar datos en la base de datos
def load_data_to_db(data, session):
    try:
        for _, row in data.iterrows():
            # Añadir info del encuestado
            encuestado = Encuestado(
                genero = row['genero'],
                pais = row['pais'],
                ocupacion = row['ocupacion'],
                autonomo = row['autonomo']
            )
            session.add(encuestado)
            session.commit()

            # Añadir info sobre salud
            salud = SaludMental(
                id_encuestado = encuestado.id_encuestado,
                antecedentes_familiares = row['antecedentes_familiares'],
                ha_buscado_tratamiento = row['ha_buscado_tratamiento'],
                historial_salud_mental = row['historial_salud_mental'], 
                cambios_humor = row['cambios_humor'],
                dificultades_lidiar_desafios = row['dificultades_lidiar_desafios'],
                estres_creciente = row['estres_creciente'],
                riesgo_salud = row['riesgo_salud']
            )
            session.add(salud)

            # Añadir info sobre habitos de encuestados
            social = Social(
                id_encuestado = encuestado.id_encuestado,
                dias_en_casa = row['dias_en_casa'],
                cambio_habitos = row['cambio_habitos'],
                interes_laboral = row['interes_laboral'],
                dificultades_sociales = row['dificultades_sociales'],
                salud_mental_entrevista = row['salud_mental_entrevista'],
                opciones_atencion = row['opciones_atencion']
            )
            session.add(social)
        
        # Confirmar cambios en la base de datos
        session.commit()
        print("Datos cargados exitosamente")

    except Exception as e:
        session.rollback()
        print(f"Error al cargar datos: {e}")