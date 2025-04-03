import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import func, desc, case
from create_tables import Encuestado, SaludMental, Social
import plotly.graph_objects as go

# cargar variables de .env 
load_dotenv()
DB_URL = os.getenv("DB_URL")

# Conectar a la base de datos
engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)
session = Session()

num_encuestados = session.query(Encuestado).count()
print(f"Numero total de encuestados: {num_encuestados}")

riesgo_alto = session.query(SaludMental).filter(getattr(SaludMental, "riesgo_salud") == "Alto").count()
print(f"Nº de personas con riesgo de salud elevado: {riesgo_alto}")

autonomos_riesgo = session.query(Encuestado).join(SaludMental, Encuestado.id_encuestado == SaludMental.id_encuestado)\
    .filter(Encuestado.autonomo == True, SaludMental.riesgo_salud == "Alto").count()
print(f"Personas autonomas con riesgo salud alto: {autonomos_riesgo}")

numero_autonomos = session.query(Encuestado).filter(Encuestado.autonomo == True).count()
autonomos_porcentage = (numero_autonomos/num_encuestados) * 100
print(f"Porcentaje de autonomos: {autonomos_porcentage}")

autonomos_riesgo_porcentage = (autonomos_riesgo/riesgo_alto) * 100
print(f"Porcentaje de autonomos con riesgo alto: {autonomos_riesgo_porcentage}")

# Consultar el número de personas por categoría
categorias = session.query(Encuestado.ocupacion, func.count(Encuestado.id_encuestado)).group_by(Encuestado.ocupacion).all()

for categoria, count in categorias:
    porcentaje = (count / num_encuestados) * 100
    print(f"{categoria}: {porcentaje:.2f}%. ", end="")
print()

# Consultar el número de personas por categoría con riesto de salud alto
encuestados_por_ocupacion = session.query(Encuestado.ocupacion, func.count(Encuestado.id_encuestado))\
    .join(SaludMental, Encuestado.id_encuestado == SaludMental.id_encuestado)\
        .filter(SaludMental.riesgo_salud == "Alto").group_by(Encuestado.ocupacion).all()

for categoria, count in encuestados_por_ocupacion:
    porcentaje = (count / riesgo_alto) * 100
    print(f"{categoria}: {porcentaje:.2f}%. ", end="")
print()


# Datos obtenidos de la consulta
ocupaciones = [categoria for categoria, _ in encuestados_por_ocupacion]
counts = [count for _, count in encuestados_por_ocupacion]
# Suponemos que `riesgo_alto` es el total de los encuestados con riesgo alto
porcentajes = [(count / riesgo_alto) * 100 for count in counts]

'''
# Crear el gráfico de barras
fig = go.Figure(
    data=[go.Bar(
        x=ocupaciones, 
        y=porcentajes, 
        marker_color='skyblue'
    )]
)

# Actualizar layout con títulos
fig.update_layout(
    title='Porcentaje de Encuestados con Riesgo Alto por Ocupación',
    xaxis_title='Ocupación',
    yaxis_title='Porcentaje (%)',
    xaxis_tickangle=-45  # Girar etiquetas si es necesario
)

# Mostrar gráfico interactivo
fig.show()
'''

# Personas con riesgo alto por genero
total_por_genero = session.query(Encuestado.genero,func.count(Encuestado.id_encuestado)).group_by(Encuestado.genero).all()

riesgo_alto_por_genero = session.query(Encuestado.genero,func.count(Encuestado.id_encuestado)).join(SaludMental, Encuestado.id_encuestado == SaludMental.id_encuestado)\
 .filter(SaludMental.riesgo_salud == 'Alto').group_by(Encuestado.genero).all()

total_dict = dict(total_por_genero)
riesgo_dict = dict(riesgo_alto_por_genero)

print("Porcentaje de personas con riesgo de salud alto por genero: ")
for genero, riesgo_count in riesgo_dict.items():
    total_count = total_dict.get(genero, 0)
    porcentaje = (riesgo_count / total_count) * 100 if total_count else 0
    print(f"    {genero} : {porcentaje:.2f}%")

# Consultar porcentaje de estudiantes con estres creciente
estudiantes_num = session.query(Encuestado).filter(Encuestado.ocupacion == "Otros").count()

estudiantes_estres = session.query(Encuestado).filter(Encuestado.ocupacion == "Otros")\
    .join(SaludMental, Encuestado.id_encuestado == SaludMental.id_encuestado).filter(SaludMental.estres_creciente == "Si").count()

porcentaje_estudiantes_estres = (estudiantes_estres / estudiantes_num) * 100
print(f"Porcentaje de estudiantes con estres creciente: {porcentaje_estudiantes_estres: .2f}%")

# Relacion entre dias en casa y dificultades sociales
dificultades_por_dias = session.query(Social.dias_en_casa, Social.dificultades_sociales, func.count(Social.id_social))\
    .group_by(Social.dias_en_casa, Social.dificultades_sociales).all()

resultados = {}

for dias, dificultad, count in dificultades_por_dias:
    if dias not in resultados:
        resultados[dias] = {}
    resultados[dias][dificultad] = count

for dias, dificultades in resultados.items():
    total = sum(dificultades.values())
    print(f"{dias} dias en casa: ", end="")
    for dificultad, count in dificultades.items():
        porcentaje = (count / total) * 100
        print(f"{dificultad} -> {porcentaje:.2f}%", end=" ")
    print()

# Personas que reportan cambio de habitos y que tambien presentan estres creciente
totaL_cambio_habitos = session.query(func.count(Social.id_encuestado)).filter(Social.cambio_habitos == "Si").scalar()

total_cambio_habitos_y_estres = session.query(func.count(Social.id_encuestado)).join(SaludMental, Social.id_encuestado == SaludMental.id_encuestado)\
    .filter(Social.cambio_habitos == "Si", SaludMental.estres_creciente == "Si").scalar()

porcentaje = (total_cambio_habitos_y_estres / totaL_cambio_habitos) * 100

print(f"Porcentaje personas con cambio habitos que presentan estres creciente: {porcentaje:.2f}%")

# Impacto del tiempo en casa sobre el nivel de estres
estres_por_dias = session.query(Social.dias_en_casa, SaludMental.estres_creciente, func.count(Social.id_social).label('total_grupo'))\
    .join(SaludMental, Social.id_encuestado == SaludMental.id_encuestado).group_by(Social.dias_en_casa, SaludMental.estres_creciente).all()

resultados_dias_estres = {}

for dias, estres, count in estres_por_dias:
    if dias not in resultados_dias_estres:
        resultados_dias_estres[dias] = {}
    resultados_dias_estres[dias][estres] = count

for dias, estres in resultados_dias_estres.items():
    total = sum(estres.values())
    print(f"{dias} dias en casa: ", end="")
    for estres_nivel, count in estres.items():
        porcentaje = (count / total) * 100
        print(f"{estres_nivel} -> {porcentaje:.2f}%", end=" ")
    print()

# Top 5 paises con mayor porcentaje de personas con riesgo medio o alto de salud
total_personas_por_pais = session.query(Encuestado.pais, func.count(Encuestado.id_encuestado).label('total_personas')).group_by(Encuestado.pais).all()

riesgo_por_pais = session.query(Encuestado.pais, func.count(Encuestado.id_encuestado).label('total_riesgo_alto_medio'))\
    .join(SaludMental, Encuestado.id_encuestado == SaludMental.id_encuestado).filter(SaludMental.riesgo_salud.in_(["Medio", "Alto"]))\
        .group_by(Encuestado.pais).all()

total_personas_dict = {pais: total for pais, total in total_personas_por_pais}
riesgo_dict = {pais: total_riesgo_alto_medio for pais, total_riesgo_alto_medio in riesgo_por_pais}
resultados_paises = []

for pais in total_personas_dict:
    total = total_personas_dict[pais]
    riesgo_alto = riesgo_dict.get(pais, 0)
    porcentaje = riesgo_alto / total * 100
    resultados_paises.append((pais, porcentaje))

top_5 = sorted(resultados_paises, key=lambda x: x[1], reverse=True)[:5] # Ordenar por el segundo elemento (porcentaje)

for pais, porcentaje in top_5:
    print(f"{pais}: {porcentaje:.4f}%")

# Personas con posibilidades de atencion y que han buscado tratamiento
result = session.query(func.count(case((Social.opciones_atencion == 'Si', 1), else_ = None)).label('total_opciones_atencion'),\
    func.count(case(((Social.opciones_atencion == 'Si') & (SaludMental.ha_buscado_tratamiento == True), 1), else_ = None)).label('han_buscado_tratamiento')).\
        join(SaludMental, Social.id_encuestado == SaludMental.id_encuestado).all()

total_opciones_atencion = result[0].total_opciones_atencion
han_buscado_tratamiento = result[0].han_buscado_tratamiento

porcentaje = (han_buscado_tratamiento / total_opciones_atencion * 100) if total_opciones_atencion else 0

print(f"Encuestados con opciones de atencion: {total_opciones_atencion}. Han buscado tratamiento {han_buscado_tratamiento} ({porcentaje:.2f}%)")
