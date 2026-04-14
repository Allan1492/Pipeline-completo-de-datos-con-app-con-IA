import json
from database import get_db_connection  # Se importa la conexión

def subir_json_a_mongo(ruta_json):
    # 1. Se conecta el JSON a MongoDB
    db = get_db_connection()
    if db is None:
        return
        
    coleccion = db["arrestos_tempe"] # Nombre de la tabla en Atlas

    # 2. Se lee el JSON procesado
    with open("arrestos_procesados.json", 'r') as f:
        datos = json.load(f)

    # 3. Subida masiva (Insert Many)
    print(f"Subiendo {len(datos)} registros a MongoDB Atlas.")
    try:
        coleccion.insert_many(datos)
        print("Carga exitosa.")
    except Exception as e:
        print(f"Falló la subida: {e}")

if __name__ == "__main__":
    subir_json_a_mongo("arrestos_procesados.json")