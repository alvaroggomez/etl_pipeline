import pandas as pd

# Leer csv original
def read_csv(file_path):
    return pd.read_csv(file_path)

# Limpiar datos
def clean_data(df):
    # Eliminar la primera columna
    df = df.drop(columns=['Timestamp'])

    # Eliminar filas con valores nulos en alguna de las priemras columnas (genero - autonomo)
    df = df.dropna(subset=df.columns[0:4])

    return df

# Crear y editar columnas o valores de atributos
def transform_data(df):
    ## Cambiar nombres de columnas
    df.columns = ['genero', 'pais', 'ocupacion', 'autonomo', 'antecedentes_familiares', 'ha_buscado_tratamiento', 'dias_en_casa',
                'estres_creciente', 'cambio_habitos', 'historial_salud_mental', 'cambios_humor', 'dificultades_lidiar_desafios', 
                    'interes_laboral', 'dificultades_sociales', 'salud_mental_entrevista', 'opciones_atencion']

    ## Cambiar nombres de valores
    df = df.replace({'Yes': 'Si', 'Maybe': 'Quizas'})

    df['genero'] = df['genero'].replace({'Female': 'Mujer', 'Male': 'Hombre'})

        # Se puede usar bibliotecas como deep_translator pero tardaría mucho más. 
    df['pais'] = df['pais'].replace({
        'United States': 'Estados Unidos', 'Poland': 'Polonia', 'United Kingdom': 'Reino Unido', 'South Africa': 'Sudáfrica',
        'Sweden': 'Suecia', 'New Zealand': 'Nueva Zelanda', 'Netherlands': 'Países Bajos', 'Belgium': 'Bélgica', 'Ireland': 'Irlanda',
        'France': 'Francia', 'Brazil': 'Brasil', 'Russia': 'Rusia', 'Germany': 'Alemania', 'Switzerland': 'Suiza', 'Finland': 'Finlandia',
        'Italy': 'Italia', 'Bosnia and Herzegovina': 'Bosnia y Herzegovina', 'Singapore': 'Singapur', 'Croatia': 'Croacia', 'Thailand': 'Tailandia',
        'Denmark': 'Dinamarca', 'Greece': 'Grecia', 'Moldova': 'Moldavia', 'Czech Republic': 'República Checa', 'Philippines': 'Filipinas' 
    })


    df['ocupacion'] = df['ocupacion'].replace({'Corporate': 'Corporativo', 'Student': 'Estudiante', 'Business': 'Negocios', 'Housewife': 'Hogar', 'Others': 'Otros'})

    df['dias_en_casa'] = df['dias_en_casa'].replace({'1-14 days': '1-14', 'Go out Every day': '0', 'More than 2 months': '+60', '15-30 days': '15-30', '31-60 days': '31-60'})

    df['cambios_humor'] = df['cambios_humor'].replace({'Medium': 'Medio', 'Low': 'Bajo', 'High': 'Alto'})

    df['opciones_atencion'] = df['opciones_atencion'].replace({'Not sure': 'No sabe'})

    # Convertir las columnas con solo valores de Si y No a booleanas
    columns_to_convert = ['autonomo', 'antecedentes_familiares', 'ha_buscado_tratamiento', 'dificultades_lidiar_desafios']

    for column in columns_to_convert:
        df[column] = df[column].apply(lambda x: True if x == 'Si' else (False if x == 'No' else x))
    
    # Creamos un nuevo atributo que indica el nivel de riesgo de tener un problema de salud mental basado en atributos ya definidos
    def calcular_riesgo(row):
        # Definir columnas clave que afectan al riesgo
        columnas_riesgo = ['estres_creciente', 'cambio_habitos', 'antecedentes_familiares', 'ha_buscado_tratamiento',
                            'historial_salud_mental', 'cambios_humor', 'dificultades_lidiar_desafios']
        
        # Por cada 'si' en una columna de riesgo suma 2 y por cada 'quizas' suma 1
        count_columnas = sum([2 if row[col] == 'Si' else 1 if row[col] == 'Quizas' else 0 for col in columnas_riesgo])
        # Pondera 1 si no pasa ningun dia en casa, y 2 si pasa mas de 60 
        count_dias = 1 if row['dias_en_casa'] == '0' else 2 if row['dias_en_casa'] == '+60' else 0
        # Calculo de riesgo
        count = count_columnas + count_dias
        # Definir nivel de riesgo
        if count >= 7:
            return 'Alto'
        elif count >= 4:
            return 'Medio'
        else:
            return 'Bajo'
        
    df['riesgo_salud'] = df.apply(calcular_riesgo, axis = 1)

    return df

# Guardar los datos limpios
def save_data(df, output_path):
    df.to_csv(output_path, index=False)
