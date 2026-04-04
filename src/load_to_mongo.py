import json
import os 
from database import get_db_connection

def subir_json_a_mongo(ruta_json):
    # 1. Conectamos
    db = get_db_connection()
    if db is None:
        return
        
    coleccion = db["arrestos_tempe"]

    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            
        # 3. Subida masiva
        print(f"⬆️ Subiendo {len(datos)} registros a MongoDB Atlas...")
        
     
        
        coleccion.insert_many(datos)
        print("✅ ¡Carga exitosa! Los datos ya están en la nube.")
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo en la ruta: {ruta_json}")
    except Exception as e:
        print(f"❌ Falló la subida: {e}")

if __name__ == "__main__":
    
    subir_json_a_mongo("data/arrestos_procesados.json")