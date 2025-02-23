import streamlit as st
import geopandas as gpd
import pandas as pd 
import geopandas as gpd
import streamlit as st

from src.variables import CANDIDATOS
from src.plots import assign_quintiles


# Lectura de datos
def load_geo_data(file_path):
    return gpd.read_file(file_path)


def read_data():
    provincias_geojson = load_geo_data('data/provincias.geojson')
    cantones_geojson = load_geo_data('data/cantones.geojson')
    parroquias_geojson = load_geo_data('data/parroquias.geojson')
    
    resultados = pd.read_excel('data/resultados.xlsx')
    return provincias_geojson,cantones_geojson,parroquias_geojson,resultados

@st.cache_resource
def leer_resultados_juntas():
    data = pd.read_csv('data/RESULTADOS_JUNTA.csv')
    data['NOM_ZONA'] = data['NOM_ZONA'].fillna(' ')
    return data

def categorizacion_prop(n):
    n = float(n)
    if n >= 1.76:
        return 1
    elif n >= 1.26:
        return 2
    elif n >= 1.01:
        return 3
    elif n >= 0.80:
        return 4
    elif n >= 0.571:
        return 5
    else:
        return 6

# Transformaciones y obtencion de porcentajes
def generate_pivot(resultados,category):      
    if category == 'PROVINCIA':
        pivot = resultados.pivot_table(index=[f'COD_{category}',f'NOM_{category}'],values='RESULTADOS',columns='NOM_CANDIDATO',aggfunc='sum').reset_index()
    elif category == 'CANTON':
        pivot = resultados.pivot_table(index=[f'COD_{category}',f'NOM_{category}'],values='RESULTADOS',columns='NOM_CANDIDATO',aggfunc='sum').reset_index()
    elif category == 'PARROQUIA':
        pivot = resultados.pivot_table(index=['COD_PROVINCIA','NOM_CANTON','COD_CANTON',f'COD_{category}',f'NOM_{category}'],values='RESULTADOS',columns='NOM_CANDIDATO',aggfunc='sum').reset_index()
        cod_circun = resultados[['COD_CIRCUNSCRIPCION','COD_PARROQUIA']].drop_duplicates()
        cod_circun = cod_circun.drop_duplicates(subset='COD_PARROQUIA')
        pivot = pd.merge(pivot,cod_circun,on='COD_PARROQUIA',)
    elif category == 'PARROQUIA_CIRCUNSCRIPCION':
        pivot = resultados.pivot_table(index=['COD_PROVINCIA','COD_CIRCUNSCRIPCION',f'COD_PARROQUIA',f'NOM_PARROQUIA'],values='RESULTADOS',columns='NOM_CANDIDATO',aggfunc='sum').reset_index()
    else:
        print('ERROR: Category Not Found')
        return None
    pivot['AUSENTISMO'] = pivot['ELECTORES'] - pivot['SUFRAGANTES']
    pivot['VALIDOS'] = pivot['SUFRAGANTES'] - pivot['BLANCO'] - pivot['NULO']
    # Calculo porcentajes

    pivot['P_ANDREA GONZALEZ'] = ((pivot['ANDREA GONZALEZ']/pivot['VALIDOS'])*100).round(2)
    pivot['P_DANIEL NOBOA AZIN'] = ((pivot['DANIEL NOBOA AZIN']/pivot['VALIDOS'])*100).round(2)
    pivot['P_LEONIDAS IZA'] = ((pivot['LEONIDAS IZA']/pivot['VALIDOS'])*100).round(2)
    pivot['P_LUISA GONZALEZ'] = ((pivot['LUISA GONZALEZ']/pivot['VALIDOS'])*100).round(2)
    pivot['P_OTROS'] = ((pivot['OTROS']/pivot['VALIDOS'])*100).round(2)
    pivot['P_BLANCO'] = ((pivot['BLANCO']/pivot['SUFRAGANTES'])*100).round(2)
    pivot['P_NULO'] = ((pivot['NULO']/pivot['SUFRAGANTES'])*100).round(2)
    pivot['P_AUSENTISMO'] = ((pivot['AUSENTISMO']/pivot['ELECTORES'])*100).round(2)
    return pivot


# Hacemos merge del geojson con las transformaciones
@st.cache_resource
def calcular_completas():
    # 1. Leemos los geojson y los resultados
    provincias_geojson,cantones_geojson,parroquias_geojson,resultados = read_data()
    # 2. Definimos el degloce y generamos las tablas pivot

    pivot_provincia = generate_pivot(resultados,'PROVINCIA')
    pivot_canton = generate_pivot(resultados,'CANTON')
    pivot_parroquia = generate_pivot(resultados,'PARROQUIA')
    pivot_parroquia_circunscripcion = generate_pivot(resultados,'PARROQUIA_CIRCUNSCRIPCION')
    # Provincia
    completa_provincias = pd.merge(pivot_provincia,provincias_geojson,on='COD_PROVINCIA')
    completa_provincias['Diff ADN-RC'] = completa_provincias['P_DANIEL NOBOA AZIN'] - completa_provincias['P_LUISA GONZALEZ']
    completa_provincias['Prop'] = completa_provincias['DANIEL NOBOA AZIN']/completa_provincias['LUISA GONZALEZ']
    completa_provincias['Cat_Prop'] = completa_provincias['Prop'].apply(categorizacion_prop)
    completa_provincias = gpd.GeoDataFrame(completa_provincias, geometry='geometry')

    # Canton
    completa_cantones = pd.merge(pivot_canton,cantones_geojson,on='COD_CANTON')
    completa_cantones['Diff ADN-RC'] = completa_cantones['P_DANIEL NOBOA AZIN'] - completa_cantones['P_LUISA GONZALEZ']
    completa_cantones['Prop'] = completa_cantones['DANIEL NOBOA AZIN']/completa_cantones['LUISA GONZALEZ']
    completa_cantones['Cat_Prop'] = completa_cantones['Prop'].apply(categorizacion_prop)
    completa_cantones = gpd.GeoDataFrame(completa_cantones, geometry='geometry')
    
    # Parroquia
    completa_parroquias = pd.merge(pivot_parroquia,parroquias_geojson,on='COD_PARROQUIA')
    completa_parroquias['Diff ADN-RC'] = completa_parroquias['P_DANIEL NOBOA AZIN'] - completa_parroquias['P_LUISA GONZALEZ']
    completa_parroquias['Prop'] = completa_parroquias['DANIEL NOBOA AZIN']/completa_parroquias['LUISA GONZALEZ']
    completa_parroquias['Cat_Prop'] = completa_parroquias['Prop'].apply(categorizacion_prop)
    completa_parroquias = gpd.GeoDataFrame(completa_parroquias, geometry='geometry')
    
    # Parroquia Canton
    completa_parroquias_canton = pd.merge(pivot_parroquia,parroquias_geojson,on='COD_PARROQUIA',how='left')
    completa_parroquias_canton['Diff ADN-RC'] = completa_parroquias_canton['P_DANIEL NOBOA AZIN'] - completa_parroquias_canton['P_LUISA GONZALEZ']
    completa_parroquias_canton['Prop'] = completa_parroquias_canton['DANIEL NOBOA AZIN']/completa_parroquias_canton['LUISA GONZALEZ']
    completa_parroquias_canton['Cat_Prop'] = completa_parroquias_canton['Prop'].apply(categorizacion_prop)
    completa_parroquias_canton = gpd.GeoDataFrame(completa_parroquias_canton, geometry='geometry')
    
    # Circunscripción Parroquia
    completa_parroquias_circunscripcion = pd.merge(pivot_parroquia_circunscripcion,parroquias_geojson,on='COD_PARROQUIA',how='left')
    completa_parroquias_circunscripcion['Diff ADN-RC'] = completa_parroquias_circunscripcion['P_DANIEL NOBOA AZIN'] - completa_parroquias_circunscripcion['P_LUISA GONZALEZ']
    completa_parroquias_circunscripcion['Prop'] = completa_parroquias_circunscripcion['DANIEL NOBOA AZIN']/completa_parroquias_circunscripcion['LUISA GONZALEZ']
    completa_parroquias_circunscripcion['Cat_Prop'] = completa_parroquias_circunscripcion['Prop'].apply(categorizacion_prop)
    completa_parroquias_circunscripcion = gpd.GeoDataFrame(completa_parroquias_circunscripcion, geometry='geometry')    
    
    for cand in CANDIDATOS:
        completa_provincias[f'Q_{cand}'] = assign_quintiles(completa_provincias[f'P_{cand}'])
        completa_cantones[f'Q_{cand}'] = assign_quintiles(completa_cantones[f'P_{cand}'])
        completa_parroquias[f'Q_{cand}'] = assign_quintiles(completa_parroquias[f'P_{cand}'])
        completa_parroquias_canton[f'Q_{cand}'] = assign_quintiles(completa_parroquias_canton[f'P_{cand}'].fillna(0))
        completa_parroquias_circunscripcion[f'Q_{cand}'] = assign_quintiles(completa_parroquias_circunscripcion[f'P_{cand}'].fillna(0))
    return completa_provincias,completa_cantones,completa_parroquias,completa_parroquias_circunscripcion,completa_parroquias_canton
