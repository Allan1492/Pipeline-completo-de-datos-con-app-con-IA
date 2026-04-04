import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
from src.database import get_db_connection

# Configuración inicial de la página
st.set_page_config(
    page_title="Panel de Control Tempe - Alerta Temprana", 
    layout="wide", 
    page_icon="🚓"
)

@st.cache_data(ttl=3600)
def load_data():
    try:
        db = get_db_connection()
        if db is not None:
            col = db["arrestos_tempe"]
            df = pd.DataFrame(list(col.find({}, {'_id': 0})))
            # Normalización de nombres de columnas
            df.columns = [c.lower().strip() for c in df.columns]
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al conectar con MongoDB Atlas: {e}")
        return pd.DataFrame()

st.title("📊 Panel de Control de Arrestos y Alerta Temprana")
st.markdown("Análisis descriptivo y predictivo de incidentes de arresto en Tempe, Arizona.")

df = load_data()

if not df.empty:
    # --- MAPEADO DE COLUMNAS ---
    c_delito = 'charge'
    c_sev = 'severity_trans'
    c_zona = 'area_name'
    c_hora = 'arrest_hour_of_day'
    c_dia = 'dia_nombre'

    # Barra lateral: Filtros
    st.sidebar.header("🎯 Filtros Históricos")
    st.sidebar.markdown("Ajusta los criterios para actualizar las métricas y gráficos.")
    
    opciones_cargos = sorted(df[c_delito].dropna().unique().tolist())
    seleccion = st.sidebar.multiselect(
        "Filtrar por Tipo de Cargo", 
        options=opciones_cargos, 
        default=opciones_cargos[:6]
    )
    
    # Aplicar filtro
    df_filtrado = df[df[c_delito].isin(seleccion)] if seleccion else df

    # --- MÉTRICAS PRINCIPALES ---
    st.subheader("Indicadores Clave (Datos Filtrados)")
    m1, m2, m3 = st.columns(3)
    
    m1.metric("Total de Arrestos", f"{len(df_filtrado):,}")
    
    zona_activa = df_filtrado[c_zona].mode()[0] if not df_filtrado.empty and c_zona in df_filtrado else "N/A"
    m2.metric("Zona más Activa", zona_activa)
    
    hora_pico = "N/A"
    if not df_filtrado.empty and c_hora in df_filtrado:
        valor_hora = int(df_filtrado[c_hora].mode()[0])
        hora_pico = f"{valor_hora:02d}:00"
    m3.metric("Hora Pico de Incidentes", hora_pico)

    # --- SECCIÓN DE GRÁFICOS ---
    st.divider()
    st.subheader("Análisis por Tipo de Cargo")

    if not df_filtrado.empty:
        # Preparación de datos para gráfico horizontal
        conteo = df_filtrado[c_delito].value_counts().reset_index()
        conteo.columns = ['Cargo', 'Cantidad']
        
        # Gráfico de barras HORIZONTAL
        fig_barras = px.bar(
            conteo, 
            y='Cargo', 
            x='Cantidad', 
            orientation='h', 
            color='Cantidad', 
            title="Distribución de Arrestos por Cargo Seleccionado",
            labels={'Cantidad': 'Número de Arrestos', 'Cargo': 'Descripción del Delito'},
            template="plotly_dark",
            height=500  # Altura suficiente para etiquetas largas
        )
        
        fig_barras.update_layout(
            yaxis={'categoryorder':'total ascending'}, # El más alto arriba
            margin=dict(l=250, r=20, t=50, b=50)      # Margen izquierdo amplio para los nombres
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    else:
        st.warning("⚠️ Selecciona al menos un cargo en el panel lateral para generar los gráficos.")

    st.divider() 

    # 2. Gráfico de pastel
    col_izq, col_der = st.columns([1, 1]) 
    
    with col_izq:
        st.subheader("Distribución por Severidad")
        if not df_filtrado.empty and c_sev in df_filtrado:
            fig_pastel = px.pie(
                df_filtrado, 
                names=c_sev, 
                hole=0.4, 
                title="Proporción de Delitos por Nivel de Gravedad",
                template="plotly_dark"
            )
            st.plotly_chart(fig_pastel, use_container_width=True)
        else:
            st.info("Información de severidad no disponible para este filtro.")
        
    with col_der:
        st.write(" ") 

    # --- SECCIÓN DE ALERTA TEMPRANA (IA) ---
    st.divider()
    st.header("🚨 Sistema de Alerta Temprana")
    
    RUTA_MODELO = 'models/alerta_tempe_model.pkl'
    RUTA_COLUMNAS = 'models/model_columns.pkl'

    if os.path.exists(RUTA_MODELO) and os.path.exists(RUTA_COLUMNAS):
        modelo = joblib.load(RUTA_MODELO)
        columnas_modelo = joblib.load(RUTA_COLUMNAS)

        with st.container():
            st.markdown("### Configuración de la Predicción")
            p1, p2, p3 = st.columns(3)
            with p1:
                input_zona = st.selectbox("Seleccione Zona Geográfica", options=sorted(df[c_zona].unique()))
            with p2:
                input_dia = st.selectbox("Día de la Semana", options=sorted(df[c_dia].unique()))
            with p3:
                input_hora = st.slider("Ventana Horaria (Formato 24h)", 0, 23, 12)

            if st.button("Consultar Nivel de Riesgo"):
                df_entrada = pd.DataFrame(0, index=[0], columns=columnas_modelo)
                if c_hora in df_entrada.columns: 
                    df_entrada[c_hora] = input_hora
                
                col_z = f"{c_zona}_{input_zona}"
                col_d = f"{c_dia}_{input_dia}"
                
                if col_z in df_entrada.columns: df_entrada[col_z] = 1
                if col_d in df_entrada.columns: df_entrada[col_d] = 1

                prediccion = modelo.predict(df_entrada)[0]
                probabilidades = modelo.predict_proba(df_entrada)[0]
                confianza = max(probabilidades) * 100

                st.markdown(f"#### Resultado de la Inferencia: **{prediccion}**")
                if "Felony" in prediccion:
                    st.error(f"Alerta: Riesgo de incidente grave detectado. Confianza: {confianza:.1f}%")
                else:
                    st.success(f"Estado: Riesgo moderado o bajo. Confianza: {confianza:.1f}%")
    else:
        st.warning("⚠️ Los archivos del modelo (.pkl) no fueron encontrados en la carpeta `/models`.")

else:
    st.error("❌ No se pudo establecer conexión con la base de datos de MongoDB.")