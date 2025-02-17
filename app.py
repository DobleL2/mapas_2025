import streamlit as st
import geopandas as gpd
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth 

from src.read_data import calcular_completas
from src.plots import generate_chroma_palette, plot_map
from src.variables import CANDIDATOS, COLORES, COLORES_ADN_RC


st.set_page_config(layout='wide',page_icon='🔍',page_title='Mapas - Resultados')
st.title('Análisis de resultados elecciones 2025 primera vuelta')

# --- HIDE #MAIN-MENU/FOOTER/HEADER -------
hide_st_style = """
    <style>
    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}
    </style>
"""
st.markdown(hide_st_style,unsafe_allow_html=True)
# -----------------------------------------

with open('./data_users.yaml') as file:
    config = yaml.load(file,Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
    )

name, authentication_status,username = authenticator.login()
if authentication_status is False:
    st.error('Incorrect username or password')
elif authentication_status is None:
    st.info('Please enter your username and password')
elif authentication_status:
    st.sidebar.title(f"Bienvenido")
    authenticator.logout("Cerrar Sesión","sidebar")
    completa_provincias,completa_cantones,completa_parroquias,completa_parroquias_circunscripcion,completa_parroquias_canton = calcular_completas()

    tab1,tab2 = st.tabs(["Comparativa",'Mapas de Calor'])
    with tab1:
        st.subheader('Comparativa')
        col1, col2 = st.columns([3,1])
        colores = COLORES_ADN_RC
        col2.subheader('Desglose')
        mostrar_nombres_1 = col2.toggle('Mostrar Nombres',key='1')
        fig_2 = None
        provincia = col2.selectbox('PROVINCIA',['SELECCIONAR PROVINCIA']+completa_provincias['NOM_PROVINCIA'].unique().tolist(),key='3') 
        if provincia == 'SELECCIONAR PROVINCIA':
            data = completa_provincias
            data_sg = data[data['COD_PROVINCIA']==20]
            fig_2, ax_2 = plot_map(data_sg, "COD_PROVINCIA", "NOM_PROVINCIA", f"Cat_Prop", colores,mostrar_nombres=mostrar_nombres_1)
            data_ng = data[data['COD_PROVINCIA']!=20]
            fig_1, ax_1 = plot_map(data_ng, "COD_PROVINCIA", "NOM_PROVINCIA", f"Cat_Prop", colores,mostrar_nombres=mostrar_nombres_1)
            col1.pyplot(fig_1, transparent=True)
            st.subheader('Votos')
            mostrar_data = data[['NOM_PROVINCIA']+CANDIDATOS+ ['ELECTORES','COD_PROVINCIA']]
            mostrar_data.set_index('COD_PROVINCIA',inplace=True) 
            st.write(mostrar_data)

            st.subheader('Porcentajes')
            mostrar_data_p = data[['NOM_PROVINCIA']+['P_'+i for i in CANDIDATOS]+['COD_PROVINCIA']+['Diff ADN-RC']]
            mostrar_data_p.set_index('COD_PROVINCIA',inplace=True) 
            st.write(mostrar_data_p)
        else:               
            cod_provincia = completa_provincias[completa_provincias['NOM_PROVINCIA']==provincia]['COD_PROVINCIA']
            data = completa_cantones[completa_cantones['COD_PROVINCIA']==int(cod_provincia)]
            data_report = completa_parroquias_canton[completa_parroquias_canton['COD_PROVINCIA']==int(cod_provincia)]
            data_report_circ = completa_parroquias_circunscripcion[completa_parroquias_circunscripcion['COD_PROVINCIA']==int(cod_provincia)]
            canton = col2.selectbox('CANTON',['SELECCIONAR CANTON']+data['NOM_CANTON'].unique().tolist(),key='5') 
            if canton == 'SELECCIONAR CANTON':
                fig_1, ax_1 = plot_map(data, "COD_CANTON", "NOM_CANTON", f"Cat_Prop", colores,mostrar_nombres=mostrar_nombres_1)
                col1.pyplot(fig_1, transparent=True)
                st.title('Desglose Canton')
                st.subheader('Votos')
                mostrar_data = data[['NOM_CANTON']+CANDIDATOS+ ['ELECTORES','COD_CANTON']]
                mostrar_data.set_index('COD_CANTON',inplace=True) 
                st.write(mostrar_data)

                st.subheader('Porcentajes')
                mostrar_data_p = data[['NOM_CANTON']+['P_'+i for i in CANDIDATOS]+['COD_CANTON']+['Diff ADN-RC']]
                mostrar_data_p.set_index('COD_CANTON',inplace=True) 
                st.write(mostrar_data_p)
            else:
                cod_canton = completa_cantones[completa_cantones['NOM_CANTON']==canton]['COD_CANTON']
                data = completa_parroquias[completa_parroquias['COD_CANTON']==int(cod_canton)]
                fig_1, ax_1 = plot_map(data, "COD_PARROQUIA", "NOM_PARROQUIA", f"Cat_Prop", colores,mostrar_nombres=mostrar_nombres_1)
                col1.pyplot(fig_1, transparent=True)
                data_lateral = data_report[['NOM_PARROQUIA',f"Prop",'COD_PARROQUIA']]
                data_lateral.set_index('COD_PARROQUIA',inplace=True) 
                col2.write(data_lateral)
            if provincia in ['GUAYAS','PICHINCHA','MANABI']:
                st.title('Parroquias por:')
                tab1_s,tab2_s = st.tabs(['CANTON','CIRCUNSCRIPCION'])
                with tab1_s:
                    
                    mostrar_data = data_report[['NOM_CANTON','NOM_PARROQUIA']+CANDIDATOS+ ['ELECTORES','COD_PARROQUIA']]
                    mostrar_data.set_index('COD_PARROQUIA',inplace=True) 
                    cantones = mostrar_data['NOM_CANTON'].unique().tolist() 
                    canton = st.selectbox('Seleccionar Circunscripción',cantones)
                    data_canton = mostrar_data[mostrar_data['NOM_CANTON']==canton]

                    st.subheader('Votos')
                    st.write(data_canton)

                    st.subheader('Porcentajes')
                    mostrar_data_p = data_report[['NOM_CANTON','NOM_PARROQUIA']+['P_'+i for i in CANDIDATOS]+['COD_PARROQUIA']+ ['Diff ADN-RC']]
                    mostrar_data_p.set_index('COD_PARROQUIA',inplace=True) 
                    data_canton_p = mostrar_data_p[mostrar_data_p['NOM_CANTON']==canton]
                    st.write(data_canton_p)   
                with tab2_s:
                    mostrar_data = data_report_circ[['NOM_PARROQUIA']+CANDIDATOS+ ['ELECTORES','COD_PARROQUIA','COD_CIRCUNSCRIPCION']]
                    mostrar_data.set_index('COD_PARROQUIA',inplace=True) 
                    circuns = mostrar_data['COD_CIRCUNSCRIPCION'].unique().tolist() 
                    circ = st.selectbox('Seleccionar Circunscripción',circuns)
                    data_circ = mostrar_data[mostrar_data['COD_CIRCUNSCRIPCION']==circ]
                    
                    st.subheader('Votos')
                    st.write(data_circ)

                    st.subheader('Porcentajes')
                    mostrar_data_p = data_report_circ[['NOM_PARROQUIA']+['P_'+i for i in CANDIDATOS]+['COD_PARROQUIA','COD_CIRCUNSCRIPCION']+ ['Diff ADN-RC']]
                    mostrar_data_p.set_index('COD_PARROQUIA',inplace=True) 
                    data_circ_p = mostrar_data_p[mostrar_data_p['COD_CIRCUNSCRIPCION']==circ]
                    st.write(data_circ_p)   
            else:
                st.subheader('Votos')
                mostrar_data = data_report[['NOM_PARROQUIA']+CANDIDATOS+ ['ELECTORES','COD_PARROQUIA']]
                mostrar_data.set_index('COD_PARROQUIA',inplace=True) 
                st.write(mostrar_data)

                st.subheader('Porcentajes')
                mostrar_data_p = data_report[['NOM_PARROQUIA']+['P_'+i for i in CANDIDATOS]+['COD_PARROQUIA']+ ['Diff ADN-RC']]
                mostrar_data_p.set_index('COD_PARROQUIA',inplace=True) 
                st.write(mostrar_data_p)

    with tab2:
        st.subheader('Mapas de Calor')
        col1, col2 = st.columns([3,1])
        col2.subheader('Candidato')
        candidato = col2.selectbox('CANDIDATO',CANDIDATOS) # Create
        colores = generate_chroma_palette(COLORES[candidato]) 
        col2.subheader('Desglose')
        mostrar_nombres = col2.toggle('Mostrar Nombres',key='2')
        fig_2 = None
        provincia = col2.selectbox('PROVINCIA',['SELECCIONAR PROVINCIA']+completa_provincias['NOM_PROVINCIA'].unique().tolist(),key='4') 
        if provincia == 'SELECCIONAR PROVINCIA':
            data = completa_provincias
            data_sg = data[data['COD_PROVINCIA']==20]
            fig_2, ax_2 = plot_map(data_sg, "COD_PROVINCIA", "NOM_PROVINCIA", f"Q_{candidato}", colores,mostrar_nombres=mostrar_nombres)
            data_ng = data[data['COD_PROVINCIA']!=20]
            fig_1, ax_1 = plot_map(data_ng, "COD_PROVINCIA", "NOM_PROVINCIA", f"Q_{candidato}", colores,mostrar_nombres=mostrar_nombres)
            col1.pyplot(fig_1, transparent=True)
            st.subheader('Votos')
            mostrar_data = data[['NOM_PROVINCIA']+CANDIDATOS+ ['ELECTORES','COD_PROVINCIA']]
            mostrar_data.set_index('COD_PROVINCIA',inplace=True) 
            st.write(mostrar_data)

            st.subheader('Porcentajes')
            mostrar_data_p = data[['NOM_PROVINCIA']+['P_'+i for i in CANDIDATOS]+['COD_PROVINCIA']+['Diff ADN-RC']]
            mostrar_data_p.set_index('COD_PROVINCIA',inplace=True) 
            st.write(mostrar_data_p)
        else:
            cod_provincia = completa_provincias[completa_provincias['NOM_PROVINCIA']==provincia]['COD_PROVINCIA']
            data = completa_cantones[completa_cantones['COD_PROVINCIA']==int(cod_provincia)]
            data_report = completa_parroquias_canton[completa_parroquias_canton['COD_PROVINCIA']==int(cod_provincia)]
            data_report_circ = completa_parroquias_circunscripcion[completa_parroquias_circunscripcion['COD_PROVINCIA']==int(cod_provincia)]
            canton = col2.selectbox('CANTON',['SELECCIONAR CANTON']+data['NOM_CANTON'].unique().tolist(),key='6') 
            if canton == 'SELECCIONAR CANTON':
                fig_1, ax_1 = plot_map(data, "COD_CANTON", "NOM_CANTON", f"Q_{candidato}", colores,mostrar_nombres=mostrar_nombres)
                col1.pyplot(fig_1, transparent=True)
                st.subheader('Votos')
                mostrar_data = data[['NOM_CANTON']+CANDIDATOS+ ['ELECTORES','COD_CANTON']]
                mostrar_data.set_index('COD_CANTON',inplace=True) 
                st.write(mostrar_data)

                st.subheader('Porcentajes')
                mostrar_data_p = data[['NOM_CANTON']+['P_'+i for i in CANDIDATOS]+['COD_CANTON'] +['Diff ADN-RC']]
                mostrar_data_p.set_index('COD_CANTON',inplace=True) 
                st.write(mostrar_data_p)
            else:
                cod_canton = completa_cantones[completa_cantones['NOM_CANTON']==canton]['COD_CANTON']
                data = completa_parroquias[completa_parroquias['COD_CANTON']==int(cod_canton)]
                fig_1, ax_1 = plot_map(data, "COD_PARROQUIA", "NOM_PARROQUIA", f"Q_{candidato}", colores,mostrar_nombres=mostrar_nombres)
                col1.pyplot(fig_1, transparent=True)
                data_lateral = data_report[['NOM_PARROQUIA',f"P_{candidato}",'COD_PARROQUIA']]
                data_lateral.set_index('COD_PARROQUIA',inplace=True) 
                col2.write(data_lateral)
            if provincia in ['GUAYAS','PICHINCHA','MANABI']:
                st.title('Parroquias por:')
                tab1_l,tab2_l = st.tabs(['CANTON','CIRCUNSCRIPCION'])
                with tab1_l:
                    
                    mostrar_data = data_report[['NOM_CANTON','NOM_PARROQUIA']+CANDIDATOS+ ['ELECTORES','COD_PARROQUIA']]
                    mostrar_data.set_index('COD_PARROQUIA',inplace=True) 
                    cantones = mostrar_data['NOM_CANTON'].unique().tolist() 
                    canton = st.selectbox('Seleccionar Circunscripción',cantones)
                    data_canton = mostrar_data[mostrar_data['NOM_CANTON']==canton]
                    
                    st.subheader('Votos')
                    st.write(data_canton)

                    st.subheader('Porcentajes')
                    mostrar_data_p = data_report[['NOM_CANTON','NOM_PARROQUIA']+['P_'+i for i in CANDIDATOS]+['COD_PARROQUIA']+ ['Diff ADN-RC']]
                    mostrar_data_p.set_index('COD_PARROQUIA',inplace=True) 
                    data_canton_p = mostrar_data_p[mostrar_data_p['NOM_CANTON']==canton]
                    st.write(data_canton_p)   
                with tab2_l:
                    mostrar_data = data_report_circ[['NOM_PARROQUIA']+CANDIDATOS+ ['ELECTORES','COD_PARROQUIA','COD_CIRCUNSCRIPCION']]
                    mostrar_data.set_index('COD_PARROQUIA',inplace=True) 
                    circuns = mostrar_data['COD_CIRCUNSCRIPCION'].unique().tolist() 
                    circ = st.selectbox('Seleccionar Circunscripción',circuns)
                    data_circ = mostrar_data[mostrar_data['COD_CIRCUNSCRIPCION']==circ]
                    
                    st.subheader('Votos')
                    st.write(data_circ)

                    st.subheader('Porcentajes')
                    mostrar_data_p = data_report_circ[['NOM_PARROQUIA']+['P_'+i for i in CANDIDATOS]+['COD_PARROQUIA','COD_CIRCUNSCRIPCION']+ ['Diff ADN-RC']]
                    mostrar_data_p.set_index('COD_PARROQUIA',inplace=True) 
                    data_circ_p = mostrar_data_p[mostrar_data_p['COD_CIRCUNSCRIPCION']==circ]
                    st.write(data_circ_p)   
            else:
                st.subheader('Votos')
                mostrar_data = data_report[['NOM_PARROQUIA']+CANDIDATOS+ ['ELECTORES','COD_PARROQUIA']]
                mostrar_data.set_index('COD_PARROQUIA',inplace=True) 
                st.write(mostrar_data)

                st.subheader('Porcentajes')
                mostrar_data_p = data_report[['NOM_PARROQUIA']+['P_'+i for i in CANDIDATOS]+['COD_PARROQUIA']+ ['Diff ADN-RC']]
                mostrar_data_p.set_index('COD_PARROQUIA',inplace=True) 
                st.write(mostrar_data_p)
