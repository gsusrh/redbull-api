import os, re, json
import traceback
import asyncio
import unidecode
import pandas as pd
from sqlalchemy import create_engine, text

from pydantic import BaseModel, Field
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class KeepAliveMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Especialmente para rutas de streaming
        if request.url.path == "/api/chat" and request.method == "POST":
            response.headers["Connection"] = "keep-alive"
            response.headers["Cache-Control"] = "no-cache"
            response.headers["X-Accel-Buffering"] = "no"  # Para Nginx
        
        return response
    
# --- Asunciones de Archivos ---
# Se asume que estos archivos existen en la misma carpeta o en el path de Python.
# Si no, reemplázalos con datos hardcodeados o la lógica adecuada.
try:
    from services.persons_mapper import COUNTRY_VARIATIONS_MAP
except ImportError:
    print("Advertencia: No se pudo importar COUNTRY_VARIATIONS_MAP. Usando un mapa vacío.")
    COUNTRY_VARIATIONS_MAP = {}
try:
    from training_prompts import few_shot_examples
except ImportError:
    print("Advertencia: No se pudo importar few_shot_examples. Usando una lista vacía.")
    few_shot_examples = []
# --- Fin de Asunciones ---


# --- Configuración ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-cd23ed33b5e34e45a6ca9c2438bfe1ee")
DB_URI = os.getenv("DATABASE_URI", "postgresql://postgres:HUOMtnXMvadivsKSrzQCmpxOqfTxaZJz@maglev.proxy.rlwy.net:30559/railway")

# --- Inicializar App y Conexiones ---
app = FastAPI()

# Middleware para mantener conexiones abiertas
app.add_middleware(KeepAliveMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine(DB_URI)
db = SQLDatabase(engine=engine)
llm_agent = ChatOpenAI(model="deepseek-chat", temperature=0, openai_api_key=OPENAI_API_KEY, base_url="https://api.deepseek.com")

# --- Variables Globales para Caché ---
all_person_akas, all_countries, all_event_names, all_event_places, STOP_WORDS = [], [], [], [], set()

# --- Funciones de Utilidad (Definidas antes de su uso) ---

def _normalize_string(s: str) -> str:
    """Normaliza un string: sin acentos, a minúsculas y sin espacios extra."""
    if not isinstance(s, str): return ""
    return unidecode.unidecode(s).lower().strip()

def preprocess_user_query(query: str) -> dict:
    """Extrae y normaliza entidades clave de la pregunta del usuario."""
    corrected_entities = {}
    normalized_query = _normalize_string(query)
    
    # Mapeo simple basado en palabras clave
    if "españa" in normalized_query or "espana" in normalized_query:
        corrected_entities['country'] = 'spain' # Normaliza a 'spain' que está en la DB
    if "internacional" in normalized_query:
        corrected_entities["event_type"] = "internacional"
    if "final" in normalized_query:
        corrected_entities["phase"] = "final"
        
    # Aquí iría la lógica más compleja con rapidfuzz si fuera necesario
    # Por ejemplo, para corregir nombres de freestylers o eventos.
    
    return {"original_query": query, "corrected_entities": corrected_entities}

def validate_sql_query(sql_query: str) -> str:
    """Valida que la consulta SQL sea segura (solo SELECT)."""
    if not isinstance(sql_query, str):
        raise ValueError("La consulta SQL generada no es un string.")
    
    cleaned = sql_query.strip().lower()
    
    if not cleaned.startswith("select"):
        raise ValueError("Operación no permitida. Solo se aceptan consultas SELECT.")
    
    forbidden_keywords = ["drop", "delete", "update", "insert", "alter", "truncate", "grant", "revoke"]
    if any(k in cleaned.split() for k in forbidden_keywords):
        raise ValueError(f"Palabra clave prohibida encontrada en la consulta SQL.")
        
    return sql_query.strip().rstrip(';')

def extract_sql_from_agent_output(agent_output: dict) -> str | None:
    """Extrae la consulta SQL de la salida del agente LangChain."""
    # El método más fiable es buscar en los pasos intermedios
    intermediate_steps = agent_output.get("intermediate_steps", [])
    for step in reversed(intermediate_steps):
        action, _ = step
        if hasattr(action, 'tool') and action.tool == 'sql_db_query' and hasattr(action, 'tool_input'):
            tool_input = action.tool_input
            if isinstance(tool_input, dict) and 'query' in tool_input:
                return tool_input['query']
    
    # Fallback: buscar en el output final si el agente no usó la herramienta correctamente
    final_output = agent_output.get("output", "")
    if isinstance(final_output, str) and "select" in final_output.lower():
        # Extraer la primera consulta SQL que encuentre
        match = re.search(r"SELECT.*?;", final_output, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0)
            
    return None

def execute_sql(query: str | None) -> dict:
    """Ejecuta una consulta SQL validada y devuelve los resultados."""
    if not query:
        return {"data": [], "error": "No se proporcionó una consulta SQL para ejecutar."}
    try:
        validated_query = validate_sql_query(query)
        with engine.connect() as conn:
            df = pd.read_sql_query(text(validated_query), conn)
        return {"data": df.to_dict(orient="records"), "error": None}
    except Exception as e:
        print(f"Error ejecutando SQL: {e}\nQuery: {query}")
        return {"data": [], "error": str(e)}

def format_sse(data: dict, event: str | None = None) -> str:
    """Formatea un diccionario al formato Server-Sent Event (SSE), con nombre de evento opcional."""
    json_data = json.dumps(data, ensure_ascii=False)
    message = f"data: {json_data}\n\n"
    if event:
        message = f"event: {event}\n{message}"
    return message


# --- Carga de Datos en Caché al Iniciar la App ---
@app.on_event("startup")
async def load_initial_data():
    """Carga datos de referencia desde la DB al iniciar para mejorar el rendimiento."""
    global all_person_akas, all_countries, all_event_names, all_event_places, STOP_WORDS
    print("Iniciando carga de datos de referencia desde la DB...")
    
    def get_db_values(engine, table: str, column: str) -> list[str]:
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT DISTINCT {column} FROM {table};"))
                # Usa la función _normalize_string ya definida
                return sorted(list(set([_normalize_string(row[0]) for row in result.fetchall() if row[0] and isinstance(row[0], str)])))
        except Exception as e:
            print(f"Error al obtener valores de la DB ({table}.{column}): {e}")
            return []

    all_person_akas = get_db_values(engine, "persons", "aka")
    all_countries = sorted(list(set(get_db_values(engine, "events", "country") + get_db_values(engine, "persons", "country"))))
    all_event_names = get_db_values(engine, "events", "name")
    all_event_places = get_db_values(engine, "events", "place")
    STOP_WORDS = {"un", "una", "el", "la", "de", "del", "que", "cual", "quien", "han", "ha", "es", "son", "ganado", "una", "final"}
    print(f"Carga completada: {len(all_person_akas)} AKAs, {len(all_countries)} países, {len(all_event_names)} eventos, {len(all_event_places)} lugares.")


# --- Configuración del Agente y Prompts ---
system_message_content = "Tu tarea es convertir preguntas en SQL para PostgreSQL. Prioriza las `Preprocessed Entities` que se te proporcionan. Tu respuesta debe ser SOLO la consulta SQL, sin explicaciones adicionales."

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", system_message_content),
    *few_shot_examples,
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

base_sql_agent = create_sql_agent(
    llm=llm_agent,
    db=db,
    agent_type="openai-tools",
    verbose=True,
    prompt=agent_prompt,
    return_intermediate_steps=True,
)

final_response_prompt_template = ChatPromptTemplate.from_template(
    """
Pregunta Original: "{pregunta_original}"
Resultados de la Base de Datos: {resultados_sql}

Basándote únicamente en los resultados proporcionados, responde a la pregunta original de forma clara y concisa en ESPAÑOL.
Si los resultados están vacíos o no responden a la pregunta, indícalo amablemente.
Respuesta:"""
)

final_response_chain = (final_response_prompt_template | llm_agent | StrOutputParser())


# --- Lógica Principal de Streaming ---

async def stream_chain_process(pregunta: str):
    """
    Generador asíncrono que emite eventos SSE con nombre para el progreso,
    los tokens de la respuesta y un objeto final con todos los resultados.
    """
    full_process_details = {}
    final_answer_text = ""

    try:
        # PASO 1: Pre-procesamiento
        yield format_sse({"step": 1, "name": "Pre-procesamiento", "status": "completed", "details": "Analizando la pregunta..."}, event="progress_update")
        preprocessed_info = preprocess_user_query(pregunta)
        full_process_details["1_pregunta_original"] = pregunta
        full_process_details["2_entidades_extraidas"] = preprocessed_info['corrected_entities']
        
        # PASO 2: Generación de SQL
        yield format_sse({"step": 2, "name": "Generación de SQL", "status": "in_progress", "details": "Generando consulta SQL..."}, event="progress_update")
        agent_llm_input = f"User Query: \"{pregunta}\"\nPreprocessed Entities: {preprocessed_info['corrected_entities']}"
        agent_output = await base_sql_agent.ainvoke({"input": agent_llm_input})
        generated_sql = extract_sql_from_agent_output(agent_output)
        if not generated_sql: raise ValueError("El agente IA no pudo generar una consulta SQL válida.")
        full_process_details["3_entrada_al_agente"] = agent_llm_input
        full_process_details["4_pensamiento_agente"] = [str(s) for s in agent_output.get("intermediate_steps", [])]
        full_process_details["5_sql_generada"] = generated_sql
        yield format_sse({"step": 2, "name": "Generación de SQL", "status": "completed", "details": f"SQL: {generated_sql}"}, event="progress_update")

        # PASO 3: Ejecución de SQL
        yield format_sse({"step": 3, "name": "Ejecución de SQL", "status": "in_progress", "details": "Consultando la base de datos..."}, event="progress_update")
        sql_execution_result = await asyncio.to_thread(execute_sql, generated_sql)
        if sql_execution_result["error"]: raise Exception(f"Error en la ejecución de SQL: {sql_execution_result['error']}")
        full_process_details["6_resultado_ejecucion"] = sql_execution_result
        yield format_sse({"step": 3, "name": "Ejecución de SQL", "status": "completed", "details": f"Se obtuvieron {len(sql_execution_result['data'])} registros."}, event="progress_update")

        # PASO 4: Generación de Respuesta Final (con streaming de tokens)
        yield format_sse({"step": 4, "name": "Generación de Respuesta", "status": "streaming", "details": "Creando respuesta final..."}, event="progress_update")
        final_answer_stream = final_response_chain.astream({
            "pregunta_original": pregunta,
            "resultados_sql": sql_execution_result["data"]
        })
        async for token in final_answer_stream:
            final_answer_text += token
            yield format_sse({"chunk": token}, event="answer_chunk")
        full_process_details["7_respuesta_final_generada"] = final_answer_text
            
        # PASO 5: Enviar el resultado final consolidado
        yield format_sse(
            data={"proceso_de_consulta": full_process_details, "respuesta_final": final_answer_text},
            event="final_result"
        )

    except Exception as e:
        print(f"Error durante el streaming del proceso: {e}")
        traceback.print_exc()
        error_payload = {"error": "Ocurrió un error en el servidor.", "details": str(e)}
        yield format_sse(error_payload, event="error")


# --- Endpoints de FastAPI ---

@app.get("/")
def index():
    return {"message": "API de consultas de Red Bull Batalla. Usa el endpoint POST /consultar."}


class Message(BaseModel):
    role: str
    content: str = Field(..., min_length=1) # Asegura que content no esté vacío
    isComplete: bool | None = None

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., min_items=1) # Asegura que la lista no 
    
@app.post("/api/query")
async def consultar(chat_request: ChatRequest):
    """
    Recibe una solicitud de chat validada por Pydantic, extrae la última
    pregunta del usuario y devuelve el proceso usando Server-Sent Events.
    """
    # Gracias a Pydantic, ya no necesitamos la validación manual ni el try-except para JSON.
    # FastAPI lo maneja por nosotros. Si el formato es incorrecto, ya habrá devuelto un error 422.

    # Buscamos hacia atrás el último mensaje con role 'user'
    last_user_message = next((msg for msg in reversed(chat_request.messages) if msg.role == "user"), None)

    if not last_user_message:
        # Este caso es raro si usamos Pydantic con min_items=1, pero es una buena práctica de defensa
        raise HTTPException(
            status_code=422,
            detail="La lista 'messages' no contiene ningún mensaje con 'role': 'user'."
        )
    
    pregunta = last_user_message.content
    
    # El resto de la lógica es idéntica
    stream_generator = stream_chain_process(pregunta)
    return StreamingResponse(stream_generator, media_type="text/event-stream")

# Para ejecutar localmente:
# uvicorn main:app --reload