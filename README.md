🚓 Tempe Arrest Analytics & Predictive Early Warning System

1. Visión General
Este proyecto implementa un Pipeline de Datos End-to-End para el análisis descriptivo y predictivo de los registros de arrestos en la ciudad de Tempe, Arizona. La solución integra una arquitectura híbrida que abarca desde la ingesta en MongoDB Atlas hasta el despliegue de inferencias estadísticas mediante un modelo de Machine Learning integrado en una interfaz de Streamlit.

2. Arquitectura de la Solución
El ecosistema técnico se divide en tres capas principales:

Capa de Persistencia: Base de datos NoSQL (MongoDB Atlas) para el almacenamiento escalable de documentos JSON.

Capa de Lógica (Business Intelligence): Procesamiento de datos con pandas y visualización dinámica mediante la librería Plotly.

Capa de Inferencia (ML): Modelo predictivo serializado capaz de clasificar la severidad del delito basado en variables temporales y geográficas.

3. Especificaciones Técnicas de los Modelos (/models)
Para garantizar la reproducibilidad del entorno de producción, es imperativo contar con los siguientes artefactos binarios:

alerta_tempe_model.pkl: Instancia serializada del estimador entrenado. Contiene los pesos y parámetros optimizados para la clasificación binaria/multiclase de incidentes.

model_columns.pkl: Vector de características (feature vector) necesario para el alineamiento de datos. Garantiza que el One-Hot Encoding generado en el frontend coincida con la estructura dimensional esperada por el modelo, evitando discrepancias de shape en el tensor de entrada.


4. Protocolo de Instalación y Despliegue
Entorno Virtual
Se recomienda el aislamiento de dependencias para evitar conflictos de versiones:

Bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
Configuración de Variables de Entorno


Ejecución del Servidor
Bash
streamlit run app.py

5. Pipeline de Machine Learning
El modelo realiza una tarea de Inferencia en Tiempo Real. Al recibir parámetros de entrada (Zona, Día, Hora), el backend:

Reconstruye el vector de características usando model_columns.pkl.

Ejecuta predict_proba() para calcular la confianza estadística del diagnóstico.

Clasifica la severidad entre Felony (Riesgo Crítico) y Misdemeanor (Riesgo Moderado).