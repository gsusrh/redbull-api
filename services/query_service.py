import logging
import json
from fastapi.responses import StreamingResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from openai import OpenAI
from config import DATABASE_URL, OPENAI_API_KEY
from utils import clean_sql_query
from typing import List, Dict, Any
from sqlalchemy import create_engine, inspect

logger = logging.getLogger(__name__)

# Inicializa la base de datos
db = SQLDatabase.from_uri(DATABASE_URL)

def get_table_info(db: SQLDatabase):
    # Crear engine de SQLAlchemy
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    table_info_lines = []
    
    # Obtener todos los nombres de tablas
    table_names = inspector.get_table_names()
    
    for table_name in table_names:
        table_info_lines.append(f"Tabla: {table_name}")
        # Obtener columnas de cada tabla
        columns = inspector.get_columns(table_name)
        for column in columns:
            table_info_lines.append(f"- {column['name']}: {column['type']}")
            
    return "\n".join(table_info_lines)

# # Obtener la información del esquema
schema_info = get_table_info(db)

# Prompt para generar consultas SQL
sql_prompt = ChatPromptTemplate.from_template("""
Dada la siguiente información sobre las tablas de la base de datos:
{schema_info}

Genera una consulta SQL válida que responda a la siguiente pregunta:
{question}

Instrucciones específicas para generar la consulta:
0. Detalles sobre la estructura:
    - created_at son solo fechas de creacion del registro.

1. Si la pregunta se refiere a **eventos** o **batallas relacionadas a un evento**, **DEBES** incluir los siguientes campos en la consulta:
   - country.
   - year.
   - scope.
   - event_id.
   - COUNT(battle_id) AS total_battles.

2. Si la pregunta se refiere a un **MC** (participante), asegúrate de incluir los siguientes campos en la consulta:
   - Nombre del MC.
   - AKA (alias) del MC.
   - Nacionalidad del MC.

3. Si la pregunta se refiere a una **batalla**, asegúrate de incluir los siguientes campos en la consulta:
   - El nombre del evento al que pertenece la batalla.
   - Los MCs involucrados en la batalla.
   - El resultado de la batalla (si está disponible).
   -se ordenan por Ronda

4. Si la pregunta combina varios conceptos (por ejemplo, eventos y MCs), asegúrate de incluir todos los campos relevantes mencionados anteriormente.
5. NO coloques LIMIT, solo si el usuario lo pide.

Asegúrate de devolver SOLO la consulta SQL, sin texto adicional ni bloques de código.
""")

# Instrucciones del sistema para generar respuestas naturales
system_instructions = """
Eres un agente Red Bull Batalla. Genera una respuesta con estas características:

- Estructura tu respuesta con títulos y subtítulos claros usando los formatos # y ## de Markdown.
- Si hay datos numéricos, preséntalo en una tabla Markdown bien formateada con encabezados claros.
- Si hay listas de elementos (mcs, eventos, etc.), usa viñetas o listas numeradas según corresponda.
- Destaca información importante usando **negrita** o *cursiva* cuando sea apropiado.
- Si hay estadísticas destacables, resáltalas en forma de citas con > para crear bloques destacados.
- Al mencionar nombres de personas o eventos, resáltalos con negrita.
- Si la información está incompleta o no disponible, indícalo claramente.
- Cuando menciones fechas de eventos, usa formato consistente y destácalas apropiadamente.
- Se directo con las respuestas.
- No agregues datos más allá del resultado de la base de datos.
- Entrega los datos completos, no realices ningún resumen.

Asegúrate de que tu respuesta tenga un formato Markdown.
"""

# Inicialización del modelo LangChain para SQL
llm_langchain = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=OPENAI_API_KEY,
    temperature=0,
    streaming=False  # No necesitamos streaming aquí
)

# Crear la cadena SQL con LangChain
sql_chain = create_sql_query_chain(
        llm_langchain, 
        db,
        k=1000  # Esto elimina el LIMIT 5 automático
    )



async def handle_query_stream(client, query: str):
    try:
        # Generar la consulta SQL usando LangChain
        generated_sql = await sql_chain.ainvoke({"question": query})
        
        # Limpiar la consulta SQL
        sql_cleaned = clean_sql_query(generated_sql)        
        
        print(sql_cleaned)
        
        # Ejecutar la consulta SQL en la base de datos
        result = db.run(sql_cleaned)
        
        # Usar las system instructions
        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": f"Pregunta del usuario: {query}\nResultado de la base de datos: {result}"}
        ]
                
        async def generate():
            try:
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0,
                    stream=True
                )
                
                accumulated_content = ""
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        accumulated_content += content
                        yield f"data: {json.dumps({'content': content, 'status': 'streaming'})}\n\n"

                    if chunk.choices and chunk.choices[0].finish_reason == "stop":
                        yield f"data: {json.dumps({'content': accumulated_content, 'status': 'done'})}\n\n"
                        break

            except Exception as e:
                logger.error(f"Error in generate(): {e}")
                yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
        
        return generate()
    
    except Exception as e:
        logger.error(f"Error in handle_query_stream: {str(e)}")
        
        async def error_generator():
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
        
        return error_generator()
    

async def handle_query(messages: List[Dict[str, Any]]):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        # Filtrar mensajes válidos
        valid_messages = [msg for msg in messages if msg.get("content")]

        last_message = valid_messages[-1]
        query = last_message["content"]
        
        # Generar stream de respuesta
        stream_generator = await handle_query_stream(client, query)
        
        return StreamingResponse(stream_generator, media_type="text/event-stream")
    
    except Exception as e:
        logger.error(f"Error in handle_chat: {str(e)}")
        
        async def error_stream(error):
            yield f"data: {json.dumps({'status': 'error', 'message': str(error)})}\n\n"
        
        return StreamingResponse(error_stream(e), media_type="text/event-stream")
