import pandas as pd
import os
from src.database import get_db_connection  # Conexión centralizada

def extraer_datos_desde_mongo():
    """Extrae los datos crudos directamente desde el clúster de Atlas."""
    try:
        db = get_db_connection()
        if db is not None:
            coleccion = db["arrestos_tempe"] 
            
            # Proyección: Solo traemos lo que la IA necesita (ahorra ancho de banda)
            proyeccion = {
                'arrest_dt': 1, 'arrest_hour_of_day': 1, 'zipcode': 1, 
                'area_name': 1, 'severity_trans': 1, 'charge': 1, 
                'x_coordinate': 1, 'y_coordinate': 1, '_id': 0
            }
            
            cursor = coleccion.find({}, proyeccion)
            df = pd.DataFrame(list(cursor))
            
            if df.empty:
                print("⚠️ La colección está vacía. Revisa MongoDB Atlas.")
                return None
                
            print(f"☁️ Datos extraídos desde MongoDB: {len(df)} filas.")
            return df
        return None
    except Exception as e:
        print(f"❌ Error al conectar con Atlas: {e}")
        return None

def transformar_datos(df):
    """Lógica de limpieza y Feature Engineering."""
    print("🛠️ Iniciando transformación...")
    
    # 1. Conversión de tipos y variables temporales
    df['arrest_dt'] = pd.to_datetime(df['arrest_dt'])
    df['dia_nombre'] = df['arrest_dt'].dt.day_name()
    df['mes'] = df['arrest_dt'].dt.month
    
    # 2. Limpieza de registros incompletos
    df = df.dropna(subset=['area_name', 'severity_trans', 'zipcode'])
    
    # 3. Mapeo para análisis numérico
    mapeo_severidad = {'Misdemeanor': 0, 'Felony': 1}
    df['severidad_num'] = df['severity_trans'].map(mapeo_severidad).fillna(0)
    
    print(f"✅ Transformación completa. {len(df)} registros listos.")
    return df

def ejecutar_pipeline_completo():
    """Coordina el flujo: Extracción (Cloud) -> Transformación -> Retorno."""
    # CAMBIO CLAVE: Llamamos a la función de MONGO, no a la de CSV
    df_crudo = extraer_datos_desde_mongo() 
    
    if df_crudo is not None:
        df_limpio = transformar_datos(df_crudo)
        return df_limpio
    return None

if __name__ == "__main__":
    print("🚀 Iniciando el Pipeline de Datos (Cloud Mode)...")
    resultado = ejecutar_pipeline_completo()
    
    if resultado is not None:
        # Aquí podrías añadir una función para subir el resultado a una nueva colección
        print(f"✅ Proceso finalizado con éxito. Se procesaron {len(resultado)} registros.")
    else:
        print("❌ El proceso terminó con errores. Verifica logs superiores.")