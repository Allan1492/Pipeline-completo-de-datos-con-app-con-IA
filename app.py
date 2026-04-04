import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from src.database import get_db_connection

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser el primer comando)
st.set_page_config(
    page_title="Panel de Control Tempe - Alerta Temprana", 
    layout="wide", 
    page_icon="🚓"
)

# 2. CARGA DE ESTILOS CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

# 3. CARGA DE DATOS
@st.cache_data(ttl=3600)
def load_data():
    try:
        db = get_db_connection()
        if db is not None:
            col = db["arrestos_tempe"]
            df = pd.DataFrame(list(col.find({}, {'_id': 0})))
            df.columns = [c.lower().strip() for c in df.columns]
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Mapeado de columnas
    c_delito, c_sev, c_zona, c_hora, c_dia = 'charge', 'severity_trans', 'area_name', 'arrest_hour_of_day', 'dia_nombre'

    # BARRA LATERAL
    st.sidebar.header("🎯 Filtros Históricos")
    opciones_cargos = sorted(df[c_delito].dropna().unique().tolist())
    seleccion = st.sidebar.multiselect("Filtrar por Cargo", opciones_cargos, default=opciones_cargos[:3])
    df_filtrado = df[df[c_delito].isin(seleccion)] if seleccion else df

    # CABECERA
    st.title("📊 Panel de Control de Arrestos y Alerta Temprana")
    st.markdown("Análisis descriptivo y predictivo de incidentes en Tempe, Arizona.")

    # MÉTRICAS
    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Arrestos", f"{len(df_filtrado):,}")
    m2.metric("Zona más Activa", df_filtrado[c_zona].mode()[0] if not df_filtrado.empty else "N/A")
    m3.metric("Hora Pico", f"{int(df_filtrado[c_hora].mode()[0]):02d}:00" if not df_filtrado.empty else "N/A")

    st.divider()

    # GRÁFICOS
    col_izq, col_der = st.columns([1.2, 0.8])
    with col_izq:
        st.subheader("Distribución por Cargo")
        conteo = df_filtrado[c_delito].value_counts().reset_index()
        conteo.columns = ['Cargo', 'Cantidad']
        fig_barras = px.bar(conteo, y='Cargo', x='Cantidad', orientation='h', color='Cantidad', 
                            template="plotly_white", color_continuous_scale="Reds")
        fig_barras.update_layout(yaxis={'categoryorder':'total ascending'}, font=dict(color="#262730"), 
                                 paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig_barras, use_container_width=True)

    with col_der:
        st.subheader("Análisis de Severidad")
        fig_pastel = px.pie(df_filtrado, names=c_sev, hole=0.4, template="plotly_white")
        fig_pastel.update_layout(font=dict(color="#262730"), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pastel, use_container_width=True)

    # SECCIÓN DE IA (ALERTA TEMPRANA)
    st.divider()
    st.header("🚨 Sistema de Alerta Temprana (ML)")
    
    path_model = 'models/alerta_tempe_model.pkl'
    path_cols = 'models/model_columns.pkl'

    if os.path.exists(path_model) and os.path.exists(path_cols):
        modelo = joblib.load(path_model)
        columnas_modelo = joblib.load(path_cols)

        with st.container():
            st.markdown("### Configuración de Escenario")
            p1, p2, p3 = st.columns(3)
            in_zona = p1.selectbox("Zona Geográfica", options=sorted(df[c_zona].unique()))
            in_dia = p2.selectbox("Día", options=sorted(df[c_dia].unique()))
            in_hora = p3.slider("Hora (0-23)", 0, 23, 12)

            if st.button("Generar Predicción de Riesgo"):
                input_data = pd.DataFrame(0, index=[0], columns=columnas_modelo)
                if c_hora in input_data.columns: input_data[c_hora] = in_hora
                col_z, col_d = f"{c_zona}_{in_zona}", f"{c_dia}_{in_dia}"
                if col_z in input_data.columns: input_data[col_z] = 1
                if col_d in input_data.columns: input_data[col_d] = 1

                res = modelo.predict(input_data)[0]
                prob = max(modelo.predict_proba(input_data)[0]) * 100

                # --- DISEÑO DE RESULTADO DE IMPACTO ---
                color_res = "#dc3545" if "Felony" in str(res) else "#28a745"
                label_res = "ALERTA: INCIDENTE GRAVE" if "Felony" in str(res) else "RIESGO BAJO / MODERADO"

                # Determinar color del porcentaje según el riesgo
                color_porcentaje = "#28a745" if "Misdemeanor" in str(res) else "#dc3545"

                st.markdown(
                    f"""
                    <div style="background-color: #ffffff; border-radius: 20px; padding: 30px; border: 1px solid #eee; text-align: center;">
                        <p style="color: {color_res}; font-size: 1.1em; font-weight: 700; letter-spacing: 1px;">{label_res}</p>
                        <h2 style="color: #1e293b; margin-top: 5px; font-size: 1.8em;">{res}</h2>
                        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #64748b; font-size: 0.9em; margin-bottom: 5px;">FIABILIDAD DEL DIAGNÓSTICO</p>
                        <h1 style="color: {color_porcentaje}; font-size: 4.5em; font-weight: 900; margin: 0;">
                            {prob:.1f}%
                        </h1>
                    </div>
                    """, unsafe_allow_html=True
                )
    else:
        st.warning("Archivos del modelo no encontrados.")
else:
    st.error("Error al conectar con la base de datos.")