import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from pathlib import Path

# Intentar importar la conexión a DB
try:
    from src.database import get_db_connection
except ModuleNotFoundError:
    from database import get_db_connection

def train_alert_model():
    print("⏳ Iniciando entrenamiento...")
    
    # 1. Cargar datos desde Atlas
    db = get_db_connection()
    if db is None:
        print("❌ Error: No se pudo conectar a la base de datos.")
        return

    df = pd.DataFrame(list(db["arrestos_tempe"].find({}, {'_id': 0})))
    
    if df.empty:
        print("⚠️ La colección está vacía. Verifica tus datos en Atlas.")
        return

  
    features = ['area_name', 'arrest_hour_of_day', 'dia_nombre']
    
    # Creamos variables dummy (numéricas) para el modelo
    X = pd.get_dummies(df[features], drop_first=True) 
    y = df['severity_trans'] 
    
    # 3. Entrenar el modelo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # --- LÓGICA DE RUTAS SEGURA ---
  
    base_path = Path(__file__).resolve().parent.parent
    models_dir = base_path / "models"

    if not models_dir.exists():
        models_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Carpeta creada en: {models_dir}")

    # Definir rutas de archivos
    model_path = models_dir / "alerta_tempe_model.pkl"
    columns_path = models_dir / "model_columns.pkl"

    # 4. Guardar
    joblib.dump(model, model_path)
    joblib.dump(X.columns.tolist(), columns_path)
    
    print(f"✅ Modelo guardado con éxito en: {model_path}")

if __name__ == "__main__":
    train_alert_model()