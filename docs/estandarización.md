Excelente pregunta. Me alegra que el análisis esté progresando. Crear un sistema de plantillas es exactamente el enfoque correcto para escalar el desarrollo de los 20 análisis de manera rápida y robusta.

Así es como podemos lograrlo, dividiendo la estrategia en dos partes: Backend (Orquestador) y Frontend.

Estrategia de Plantillas para el Backend (Orquestador)
El objetivo es que para crear un nuevo análisis (ej. Q2), solo necesitemos escribir la lógica específica de ese análisis, reutilizando toda la infraestructura.

Crear una Clase Base Abstracta:

Crearemos un nuevo archivo llamado analysis_modules/base_analyzer.py.
Dentro, definiremos una clase BaseAnalyzer que servirá como un "contrato" para todos los módulos de análisis.
Esta clase base contendrá la lógica que se repite siempre:
Cargar el archivo ingested_data.json.
Inicializar el cliente de OpenAI.
También definirá un método analyze() abstracto, forzando a que cada nuevo módulo de análisis (Q1, Q2, etc.) tenga este método.
Refactorizar el Orquestador Principal (analyze.py):

Modificaremos analyze.py para que funcione como un "enrutador" dinámico. En lugar de tener un if/elif para cada módulo (Q1, Q2...), usará un diccionario para mapear el nombre del módulo a su clase correspondiente.
Ejemplo en analyze.py:
ANALYSIS_MODULES = {
    "Q1": Q1Emociones,
    "Q2": Q2Personalidad, # Futuro
    # ... y así sucesivamente
}
Cuando se ejecute con --module Q2, el script sabrá automáticamente que debe instanciar y ejecutar la clase Q2Personalidad.
Flujo de Trabajo para un Nuevo Análisis (ej. Q2):

Paso 1: Copiar q1_emociones.py y renombrarlo a q2_personalidad.py.
Paso 2: Cambiar el nombre de la clase a Q2Personalidad y asegurarse de que herede de BaseAnalyzer.
Paso 3: Modificar el método analyze(). Esta es la única parte que cambia: se ajusta el prompt de la IA y la estructura del JSON de salida según las especificaciones del documento docs/q2_personalidad.md.
Paso 4: Registrar el nuevo módulo en el diccionario ANALYSIS_MODULES de analyze.py.
Resultado: Añadir un nuevo análisis se reduce a (1) crear un nuevo archivo de módulo, (2) escribir el prompt específico, y (3) añadir una línea en el enrutador. El resto es automático.

Estrategia de Plantillas para el Frontend
El enfoque es muy similar: reutilizar la estructura y solo cambiar el contenido específico de la visualización.

Establecer un "Contrato de Datos":

Cada pipeline del orquestador debe generar un archivo de salida con un nombre predecible (ej. q1_emociones.json, q2_personalidad.json). Esto ya lo estamos haciendo.
Flujo de Trabajo para una Nueva Vista (ej. Q2):

Paso 1: Copiar el archivo pipelines/social_media/view_components/qual/q1_view.py y renombrarlo a q2_view.py.
Paso 2: Dentro del nuevo archivo, hacer un "buscar y reemplazar":
Cambiar la carga de q1_emociones.json por q2_personalidad.json.
Renombrar la función principal de display_q1_emotions a display_q2_personality.
Paso 3: Modificar el cuerpo de la función para crear los gráficos y tablas de Streamlit que correspondan a los datos de Q2, basándose en docs/q2_personalidad.md.
Paso 4: En app.py, en la sección de "Análisis Cualitativo", añadir una nueva pestaña que llame a la función display_q2_personality.
Resultado: Crear una nueva vista es un proceso de copiar, renombrar y ajustar los gráficos, lo cual es mucho más rápido que empezar desde cero.

Una vez que confirmemos que el pipeline Q1 se ejecuta correctamente de principio a fin, mi primer paso será crear la clase BaseAnalyzer para solidificar esta arquitectura.