import json
from database import get_db_connection  # Importamos la conexión de tu otro compa

def subir_json_a_mongo(ruta_json):
    # 1. Conectamos
    db = get_db_connection()
    if db is None:
        return
        
    coleccion = db["arrestos_tempe"] # Nombre de la tabla en Atlas

    # 2. Leemos el JSON que tú mismo creaste
    with open(ruta_json, 'r') as f:
        datos = json.load(f)

    # 3. Subida masiva (Insert Many)
    print(f"⬆️ Subiendo {len(datos)} registros a MongoDB Atlas...")
    try:
        coleccion.insert_many(datos)
        print("✅ ¡Carga exitosa! Los datos ya están en la nube.")
    except Exception as e:
        print(f"❌ Falló la subida: {e}")

if __name__ == "__main__":
    subir_json_a_mongo("data/arrestos_procesados.json")