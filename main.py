from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import create_engine, text
import os
import re
import unidecode # Para remover acentos
from rapidfuzz import process # Para fuzzy matching

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# --- Configuración ---
# Asegúrate de que OPENAI_API_KEY esté configurada en tus variables de entorno o la pones directamente
# Para DeepSeek, la clave de API es tu clave de DeepSeek, no la de OpenAI, aunque use la interfaz OpenAI.
# OPENAI_API_KEY = "sk-..." # Si la tienes directamente aquí

# Usar variables de entorno para las credenciales, es más seguro
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-cd23ed33b5e34e45a6ca9c2438bfe1ee") # ¡Asegúrate de cambiar esto!
DB_URI = os.getenv("DATABASE_URI", "postgresql://postgres:HUOMtnXMvadivsKSrzQCmpxOqfTxaZJz@maglev.proxy.rlwy.net:30559/railway")

# --- Inicializar App y Conexiones ---
app = FastAPI()
engine = create_engine(DB_URI)
db = SQLDatabase(engine=engine)

# Configurar el LLM para DeepSeek
llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0, # Baja temperatura para mayor consistencia en SQL
    openai_api_key=OPENAI_API_KEY,
    base_url="https://api.deepseek.com"
)

# --- Funciones de Utilidad para Pre-procesamiento y Post-procesamiento ---

def _normalize_string(s: str) -> str:
    """Convierte un string a minúsculas y remueve acentos."""
    return unidecode.unidecode(s).lower()

def get_db_values(engine, table: str, column: str) -> list[str]:
    """Obtiene valores únicos de una columna en una tabla de la DB."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT DISTINCT {column} FROM {table};"))
            # Normalizar los valores al obtenerlos de la DB para la comparación
            return [_normalize_string(row[0]) for row in result.fetchall() if row[0]]
    except Exception as e:
        print(f"Error al obtener valores de la DB ({table}.{column}): {e}")
        return []

# Cargar los nombres y países al iniciar la aplicación (o una vez al día, etc.)
# Para evitar consultar la DB en cada petición si los datos no cambian mucho.
# Puedes hacer esto fuera de la función, en el scope global, o como un @app.on_event("startup")
all_person_akas = []
all_countries = []
all_event_names = []

@app.on_event("startup")
async def load_initial_data():
    global all_person_akas, all_countries, all_event_names
    print("Cargando datos de referencia de la DB...")
    all_person_akas = get_db_values(engine, "persons", "aka")
    all_countries = get_db_values(engine, "events", "country") # O 'persons.country' si es más completo
    all_event_names = get_db_values(engine, "events", "name")
    print(f"Cargados {len(all_person_akas)} AKAs, {len(all_countries)} países, {len(all_event_names)} nombres de eventos.")


def fuzzy_match_and_normalize(input_text: str, valid_list: list[str], umbral: int = 80) -> str:
    """
    Intenta hacer fuzzy matching y normalizar un texto de entrada contra una lista de valores válidos.
    Devuelve la versión corregida si hay una buena coincidencia, de lo contrario, el texto original normalizado.
    """
    normalized_input = _normalize_string(input_text)
    
    if not valid_list: # Si la lista de referencia está vacía
        return normalized_input

    # Intenta encontrar una coincidencia exacta primero (después de normalizar)
    if normalized_input in valid_list:
        return normalized_input

    # Si no hay coincidencia exacta, intenta fuzzy matching
    best_match, score, _ = process.extractOne(normalized_input, valid_list, scorer=fuzz.ratio)
    
    if score >= umbral:
        return best_match
    return normalized_input # Si no hay buena coincidencia, devuelve el input normalizado


def preprocess_user_query(query: str) -> dict:
    """
    Normaliza y corrige entidades en la consulta del usuario.
    Devuelve un diccionario con la consulta original y las entidades corregidas.
    """
    corrected_entities = {}
    normalized_query = _normalize_string(query)

    # Buscar y corregir nombres de personas (AKAs)
    # Una forma simple es buscar palabras que podrían ser AKAs
    # Para un sistema más robusto, se usaría NER (Named Entity Recognition)
    
    # Intenta identificar AKAs en la consulta
    for aka_db in all_person_akas:
        if re.search(r'\b' + re.escape(aka_db) + r'\b', normalized_query):
            # Si hay una coincidencia exacta (normalizada), ya está bien
            corrected_entities['person_aka'] = aka_db
            break
    if 'person_aka' not in corrected_entities:
        # Si no hay coincidencia exacta, busca palabras que podrían ser AKAs y haz fuzzy matching
        potential_akas = re.findall(r'\b[a-z0-9]+\b', normalized_query) # Extrae palabras simples
        for p_aka in potential_akas:
            corrected_aka = fuzzy_match_and_normalize(p_aka, all_person_akas, umbral=80)
            if corrected_aka != _normalize_string(p_aka): # Si hubo una corrección
                corrected_entities['person_aka'] = corrected_aka
                break # Solo la primera coincidencia por simplicidad

    # Buscar y corregir países
    for country_db in all_countries:
        if re.search(r'\b' + re.escape(country_db) + r'\b', normalized_query):
            corrected_entities['country'] = country_db
            break
    if 'country' not in corrected_entities:
        potential_countries = re.findall(r'\b(mexico|méxico|argentina|chile|españa|colombia|peru|venezuela|cuba|bolivia|ecuador|uruguay|paraguay)\b', normalized_query, re.IGNORECASE)
        for p_country in potential_countries:
            corrected_country = fuzzy_match_and_normalize(p_country, all_countries, umbral=85)
            if corrected_country != _normalize_string(p_country):
                corrected_entities['country'] = corrected_country
                break
    
    # Puedes añadir lógica similar para nombres de eventos si es necesario
    # for event_name_db in all_event_names:
    #     if re.search(r'\b' + re.escape(event_name_db) + r'\b', normalized_query):
    #         corrected_entities['event_name'] = event_name_db
    #         break
    # if 'event_name' not in corrected_entities:
    #     # Lógica de fuzzy matching para eventos
    #     pass

    # Devuelve el estado de las correcciones junto con la consulta original.
    # El LLM usará esto para generar la SQL.
    return {
        "original_query": query,
        "normalized_query": normalized_query, # Puede ser útil para el LLM
        "corrected_entities": corrected_entities
    }


def validate_sql_query(sql_query: str) -> str:
    """
    Valida una consulta SQL para seguridad y previene comandos no deseados.
    """
    sql_query_lower = sql_query.strip().lower()

    # 1. Solo permitir SELECT statements
    if not sql_query_lower.startswith("select"):
        raise ValueError("Solo se permiten consultas SELECT.")
    
    # 2. Prevenir comandos peligrosos (ej. DROP, DELETE, UPDATE, INSERT)
    forbidden_keywords = ["drop", "delete", "update", "insert", "alter", "truncate", "create", "grant", "revoke"]
    if any(keyword in sql_query_lower for keyword in forbidden_keywords):
        raise ValueError(f"La consulta contiene comandos SQL prohibidos: {sql_query_lower}")

    # 3. Prevenir múltiples comandos SQL encadenados
    if ';' in sql_query_lower[:-1]: # Si hay ; y no es el final de la consulta
        raise ValueError("Múltiples comandos SQL no permitidos en una sola consulta.")

    # 4. (Opcional) Validar contra un esquema conocido o permitir solo tablas/columnas específicas
    # Esto es más avanzado y requeriría parseo SQL completo o regex más complejos
    # Por ahora, nos basamos en las instrucciones al LLM y la verificación de comandos peligrosos.

    return sql_query

# --- Configuración del Agente SQL de LangChain con Prompt Personalizado ---

# Instrucciones detalladas para el LLM
system_message_content = """
You are an expert SQL assistant for the Red Bull Batalla database.
Your task is to convert natural language questions into accurate, safe, and efficient SQL queries.

**Database Schema:**
You have access to the following tables. Pay close attention to column names and types.
- `events`: `evento_id` (PK, INTEGER), `name` (TEXT, event name), `type` (TEXT, e.g., 'nacional', 'internacional'), `country` (TEXT), `city` (TEXT), `place` (TEXT), `date` (TEXT, 'YYYY-MM-DD').
- `battles`: `battle_id` (PK, INTEGER), `evento_id` (FK to events.evento_id), `name` (TEXT, battle name), `person_1_id` (FK to persons.person_id), `person_2_id` (FK to persons.person_id), `winner_id` (FK to persons.person_id), `phase` (TEXT, e.g., 'cuartos', 'semifinal', 'final').
- `persons`: `person_id` (PK, INTEGER), `aka` (TEXT, rapper's stage name, e.g., 'aczino', 'chuty'), `full_name` (TEXT), `country` (TEXT), `active` (BOOLEAN).

**CRITICAL GUIDELINES FOR ACCURACY AND ROBUSTNESS:**
1.  **Value Normalization:** All string values in the database (like country names, person AKAs) are stored in **lowercase and without accents**. When converting user input to a WHERE clause value, **always ensure the value matches this format**.
    *   **IMPORTANT:** If the `preprocessed_data` context (provided below) contains `corrected_entities` for `person_aka` or `country`, **YOU MUST USE THOSE CORRECTED VALUES EXACTLY** in your SQL query. Do not re-interpret them.
    *   Example: If `preprocessed_data.corrected_entities.country` is 'mexico', use `'mexico'`.
2.  **Fuzzy/Partial Matching:** When the user is looking for a name or event name, use the `LIKE` operator with wildcard `%` if the match might be partial or contain variations.
    *   Example: "batallas de Acsino" -> `WHERE p.aka LIKE '%aczino%'`.
    *   Example: "eventos de 2023" -> `WHERE name LIKE '%2023%'` or `WHERE date LIKE '2023%'`.
3.  **Exact Matching:** Use `=` for IDs, types, or values that are expected to be precise.
4.  **Relationships (JOINs):** Use JOINs when queries involve information from multiple tables (e.g., participants from a country, battles of a specific person).
    *   `persons.person_id` to `battles.person_1_id`, `battles.person_2_id`, `battles.winner_id`.
    *   `events.evento_id` to `battles.evento_id`.
    *   `events.country` or `persons.country` as needed.
5.  **Only SQL:** Return ONLY the SQL query, no extra text, explanations, or markdown formatting (```sql ... ```).
6.  **Avoid SELECT *:** Always specify the columns you need.
7.  **No Hallucinations:** Do NOT invent table names, column names, or values. If you are unsure, try to generalize or state that you cannot fulfill the request.

**User Input Structure:**
Your input will include:
- `input`: The original user's question.
- `preprocessed_data`: A dictionary containing `original_query`, `normalized_query`, and a `corrected_entities` dictionary which might have `person_aka` and `country` keys with their normalized/corrected values. **Always prioritize these `corrected_entities` if present.**

**Example of Input Structure you will receive:**
`{'input': 'Muéstrame los raperos de México', 'preprocessed_data': {'original_query': 'Muéstrame los raperos de México', 'normalized_query': 'muestrame los raperos de mexico', 'corrected_entities': {'country': 'mexico'}}}`

**Your Output Format Example:**
`SELECT p.aka FROM persons p WHERE p.country = 'mexico';`
"""

# Few-shot examples (importante para guiar al LLM)
few_shot_examples = [
    HumanMessage(content="Muéstrame los participantes de México."),
    AIMessage(content="SELECT p.aka FROM persons p WHERE p.country = 'mexico';"),

    HumanMessage(content="Cuántas batallas ha ganado el Aczino?"),
    AIMessage(content="SELECT COUNT(*) FROM battles b JOIN persons p ON b.winner_id = p.person_id WHERE p.aka = 'aczino';"),

    HumanMessage(content="¿Quién ganó la Final Internacional de 2023?"),
    AIMessage(content="SELECT p.aka FROM battles b JOIN persons p ON b.winner_id = p.person_id JOIN events e ON b.evento_id = e.evento_id WHERE e.name = 'final internacional 2023';"),

    HumanMessage(content="Dame las batallas donde participó Trueno."),
    AIMessage(content="SELECT b.name FROM battles b JOIN persons p1 ON b.person_1_id = p1.person_id JOIN persons p2 ON b.person_2_id = p2.person_id WHERE p1.aka = 'trueno' OR p2.aka = 'trueno';"),

    HumanMessage(content="Busca los eventos en España."),
    AIMessage(content="SELECT e.name, e.date FROM events e WHERE e.country = 'españa';"),
    
    HumanMessage(content="Muéstrame los raperos de Méxicou."), # Ejemplo de typo en input
    AIMessage(content="SELECT p.aka FROM persons p WHERE p.country = 'mexico';"), # El LLM debe usar el valor corregido.
]

# Creamos un prompt de chat para el agente SQL
# El Agente `openai-tools` construye un prompt internamente, y `extra_prompt_messages`
# permite añadir mensajes al principio del historial de conversación que ve el LLM.
# Usaremos esto para inyectar nuestras instrucciones y ejemplos.
# El Agente también añade su propia información de esquema y herramientas.
# Para que el Agente "vea" `preprocessed_data`, necesitamos una cadena LCEL que prepare la entrada.

# El agente por defecto espera un `input` string.
# Para pasar `preprocessed_data`, tenemos que construir una cadena personalizada.

# Definimos el agent_executor como un componente.
# El prompt real se construirá dinámicamente en la cadena.
# NOTA: `create_sql_agent` ya tiene un prompt predeterminado.
# Para inyectar `preprocessed_data` en el prompt del agente, la forma más limpia
# es crear un prompt personalizado que el agente usará.
# Para `openai-tools`, podemos usar `agent_executor.with_config(prompt=my_custom_prompt)`.

# Agente SQL base (sin prompt inyectado todavía)
base_sql_agent = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="openai-tools",
    verbose=True, # Muy útil para depurar
    # No inyectamos extra_prompt_messages aquí, lo haremos en la cadena LCEL para
    # que el prompt pueda ver el `preprocessed_data`
)

# --- Cadena LCEL Completa ---
full_chain = (
    # 1. Recibir la entrada del usuario y pre-procesarla
    RunnablePassthrough.assign(
        preprocessed_data=RunnableLambda(preprocess_user_query)
    )
    | RunnablePassthrough.assign(
        # 2. Construir el prompt final para el LLM/Agente
        # Este prompt incluirá las instrucciones, los ejemplos few-shot,
        # y la información de las entidades corregidas.
        # El agente "openai-tools" necesita un historial de mensajes.
        # Aquí construimos el historial que el LLM del agente verá.
        messages=RunnableLambda(lambda x: [
            HumanMessage(content=system_message_content), # Mensaje del sistema con guías
            *few_shot_examples, # Ejemplos few-shot
            # Mensaje del usuario final incluyendo la data pre-procesada para que el LLM la use
            HumanMessage(content=x["input"], additional_kwargs={"preprocessed_data": x["preprocessed_data"]})
        ])
    )
    | RunnablePassthrough.assign(
        # 3. Invocar al agente con el prompt personalizado.
        # El agente internamente usará las herramientas para interactuar con la DB
        # y generar la SQL.
        # Estamos sobrescribiendo el prompt del agente para cada invocación.
        sql_agent_output=RunnableLambda(lambda x: base_sql_agent.invoke({"input": x["input"], "chat_history": x["messages"]}))
        # Nota: `create_sql_agent` ya maneja `chat_history` si le pasas `MessagesPlaceholder("chat_history")` en su prompt.
        # Para que el agente vea el `preprocessed_data` como parte de la conversación,
        # lo inyectamos en `additional_kwargs` de `HumanMessage`. El LLM lo verá.
    )
    | RunnablePassthrough.assign(
        # 4. Extraer la SQL generada por el agente
        generated_sql=RunnableLambda(lambda x: x["sql_agent_output"]["output"])
    )
    | RunnablePassthrough.assign(
        # 5. Validar la SQL generada
        validated_sql=RunnableLambda(validate_sql_query)
    )
    | RunnablePassthrough.assign(
        # 6. Ejecutar la SQL validada y obtener los resultados
        db_results=RunnableLambda(lambda x: db.run(x["validated_sql"]))
    )
    | RunnableLambda(lambda x: {
        "pregunta_original": x["input"],
        "entidades_corregidas": x["preprocessed_data"]["corrected_entities"],
        "sql_generada_y_validada": x["validated_sql"],
        "resultados_db": x["db_results"]
    })
)


# --- Endpoint principal de FastAPI ---
@app.get("/")
def index():
    return {"message": "API de consultas de Red Bull Batalla. Usa /consultar para hacer preguntas."}

@app.post("/consultar")
async def consultar(request: Request):
    data = await request.json()
    pregunta = data.get('message')

    if not pregunta:
        raise HTTPException(status_code=400, detail="El campo 'message' es requerido.")
    
    try:
        # Ejecutar la cadena completa de LangChain
        response_data = await full_chain.ainvoke({"input": pregunta})
        
        # Convertir los resultados de la DB a un formato más amigable (ej. lista de dicts)
        # db.run() devuelve un string con las filas. Necesitamos parsearlo.
        # Para esto es mejor usar `engine.connect()` directamente.

        # Adaptamos para que `db.run()` devuelva algo más estructurado o lo parseamos aquí
        # Por defecto, db.run() devuelve un string multilínea, como 'col1,col2\nval1,val2\nval3,val4'
        # Lo ideal es que el LLM genere la SQL y tú la ejecutes para tener control total del formato.
        
        # Re-ejecutar la SQL directamente para obtener un formato de Pandas
        # Esto es más robusto que parsear el string de `db.run()`
        sql_to_execute = response_data["sql_generada_y_validada"]
        with engine.connect() as connection:
            df = pd.read_sql_query(sql_to_execute, connection)
        
        return {
            "pregunta_original": response_data["pregunta_original"],
            "entidades_corregidas": response_data["entidades_corregidas"],
            "sql_generada_y_validada": sql_to_execute,
            "resultados": df.to_dict(orient="records") # Convertir DataFrame a lista de diccionarios
            # "debug_output": response_data["db_results"] # Puedes mantener esto para debugging
        }

    except ValueError as ve:
        # Errores de validación de SQL o errores conocidos
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Otros errores inesperados
        print(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=f"Ocurrió un error en el servidor: {e}")

# S3 (comentado según tu código original)
# s3 = boto3.client(
#     "s3",
#     aws_access_key_id=AWS_ACCESS_KEY,
#     aws_secret_access_key=AWS_SECRET_KEY
# )

# def generar_y_subir_archivo(df):
#     archivo_local = f"/tmp/{uuid.uuid4()}.csv"
#     archivo_s3 = f"consultas/{uuid.uuid4()}.csv"
#     df.to_csv(archivo_local, index=False)
#     s3.upload_file(archivo_local, BUCKET_NAME, archivo_s3, ExtraArgs={'ACL': 'public-read'})
#     url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{archivo_s3}"
#     return url