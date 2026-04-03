import pandas as pd
import os
import json

# --- CONFIGURACIÓN DE RUTAS ---
# Usamos rutas relativas para que funcione en las compus de tus 2 compañeros
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW = os.path.join(BASE_DIR, "..", "data", "Temp_Agol_Arrests_Con_TypeA_OpenData.csv")
DATA_PROCESSED = os.path.join(BASE_DIR, "..", "data", "arrestos_procesados.json")

def extraer_datos(ruta_archivo):
    """Lee el CSV original filtrando solo las columnas necesarias."""
    columnas_vitales = [
        'arrest_dt', 'arrest_hour_of_day', 'zipcode', 'area_name', 
        'severity_trans', 'charge', 'x_coordinate', 'y_coordinate'
    ]
    try:
        df = pd.read_csv(ruta_archivo, usecols=columnas_vitales)
        print(f"📖 Datos extraídos: {len(df)} filas.")
        return df
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo en {ruta_archivo}")
        return None

def transformar_datos(df):
    """Aplica la lógica de negocio y limpieza para la IA."""
    print("🛠️ Iniciando transformación...")
    
    # 1. Limpieza de fechas y creación de variables temporales
    df['arrest_dt'] = pd.to_datetime(df['arrest_dt'])
    df['dia_nombre'] = df['arrest_dt'].dt.day_name()
    df['mes'] = df['arrest_dt'].dt.month
    df['es_fin_de_semana'] = df['arrest_dt'].dt.dayofweek >= 4 # Viernes a Domingo
    
    # 2. Manejo de Nulos (Si no hay zona o severidad, no sirve para predecir riesgo)
    df = df.dropna(subset=['area_name', 'severity_trans', 'zipcode'])
    
    # 3. Categorización de severidad para la IA (0=Menor, 1=Grave)
    # Esto le ahorra trabajo al compañero de la IA
    mapeo_severidad = {'Misdemeanor': 0, 'Felony': 1}
    df['severidad_num'] = df['severity_trans'].map(mapeo_severidad).fillna(0)
    
    print(f"✅ Transformación completa. Quedaron {len(df)} registros limpios.")
    return df

def guardar_localmente(df, ruta_salida):
    """Guarda el resultado en JSON para que el compañero de Mongo lo suba."""
    try:
        # Creamos la carpeta data si no existe
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        df.to_json(ruta_salida, orient='records', indent=4)
        print(f"💾 Archivo guardado con éxito en: {ruta_salida}")
    except Exception as e:
        print(f"❌ Error al guardar: {e}")

def ejecutar_pipeline_completo():
    """Función principal que coordina todo el proceso."""
    df_crudo = extraer_datos(DATA_RAW)
    if df_crudo is not None:
        df_limpio = transformar_datos(df_crudo)
        guardar_localmente(df_limpio, DATA_PROCESSED)
        return df_limpio

if __name__ == "__main__":
    ejecutar_pipeline_completo()