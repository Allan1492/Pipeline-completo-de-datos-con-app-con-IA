import os
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Cargamos las variables del archivo .env
load_dotenv()

def get_db_connection():
    """
    Establece la conexión con MongoDB Atlas usando la URI del .env.
    Retorna el objeto de la base de datos o None si falla.
    """
    # Buscamos la variable 'MONGO_URI' en el archivo .env
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "TempeArrestsDB") # Valor por defecto si no existe

    if not mongo_uri:
        print("❌ Error: No se encontró 'MONGO_URI' en el archivo .env")
        return None

    try:
        # Creamos el cliente con un timeout de 5 segundos para no dejar el programa colgado
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Forzamos una llamada para verificar que la conexión sea real
        client.server_info() 
        
        print(f"🔌 Conexión exitosa a la base de datos: {db_name}")
        return client[db_name]
        
    except Exception as e:
        print(f"❌ Error de conexión a MongoDB: {e}")
        return None

if __name__ == "__main__":
    # Prueba rápida de conexión
    db = get_db_connection()
    if db is not None:
        print("✅ La base de datos está lista para recibir datos.")