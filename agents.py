"""
Agent Orchestrator para Red Bull Batalla Suite.
Coordina el flujo de herramientas, validación y generación de respuestas.
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from tools import BatallaToolkit
from models import CountryEnum, RoundEnum, StyleEnum


class BatallaAgent:
    """
    Agente orquestador para consultas sobre Red Bull Batalla.
    Implementa un ciclo de tool-loop con validación estricta.
    """

    def __init__(self, db_session: Session, llm_config: Dict[str, Any]):
        self.db = db_session
        self.toolkit = BatallaToolkit(db_session)
        self.llm = ChatOpenAI(
            model=llm_config.get("model_id", "deepseek-chat"),
            temperature=llm_config.get("temperature", 0.2),
            openai_api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url", "https://api.deepseek.com")
        )
        self.max_iterations = 10
        self.iteration_count = 0

    def _extract_intent(self, query: str) -> Dict[str, Any]:
        """
        Extrae la intención del usuario desde la consulta.
        Clasifica el tipo de pregunta (búsqueda, estadísticas, comparación, etc.)
        """
        query_lower = query.lower()

        intent = {
            "type": None,
            "entities": {},
            "confidence": 0.0
        }

        # Detección de tipo de consulta
        if any(x in query_lower for x in ["comparar", "versus", "vs", "vs.", "h2h", "cara a cara"]):
            intent["type"] = "head_to_head"
            intent["confidence"] = 0.95

        elif any(x in query_lower for x in ["ranking", "top", "mejores", "campeones"]):
            intent["type"] = "ranking"
            intent["confidence"] = 0.95

        elif any(x in query_lower for x in ["estadísticas", "estadisticas", "stats", "record"]):
            intent["type"] = "statistics"
            intent["confidence"] = 0.90

        elif any(x in query_lower for x in ["evento", "batalla", "participantes"]):
            intent["type"] = "event_details"
            intent["confidence"] = 0.85

        elif any(x in query_lower for x in ["historial", "batallas", "enfrentamientos", "timeline"]):
            intent["type"] = "history"
            intent["confidence"] = 0.90

        elif any(x in query_lower for x in ["estilo", "punchlines", "técnica"]):
            intent["type"] = "style_analysis"
            intent["confidence"] = 0.80

        else:
            intent["type"] = "general_search"
            intent["confidence"] = 0.70

        # Extracción de entidades (nombres, países, años, etc.)
        intent["entities"] = self._extract_entities(query)

        return intent

    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extrae entidades clave del usuario: nombres, países, años, etc.
        """
        entities = {
            "names": [],
            "countries": [],
            "years": [],
            "rounds": [],
            "styles": []
        }

        # Búsqueda de años (4 dígitos entre 2000 y 2050)
        years = re.findall(r'\b(20\d{2})\b', query)
        entities["years"] = [int(y) for y in years if 2000 <= int(y) <= 2050]

        # Búsqueda de rondas
        rounds_keywords = {
            "final": "final",
            "semifinal": "semifinals",
            "cuartos": "quarterfinals",
            "round_16": "round_16",
            "qualifying": "qualifying"
        }
        for keyword, round_value in rounds_keywords.items():
            if keyword in query.lower():
                entities["rounds"].append(round_value)

        # Búsqueda de países (simplificado, se hará más refinado con búsqueda)
        country_keywords = {
            "españa": "spain",
            "espana": "spain",
            "argentina": "argentina",
            "méxico": "mexico",
            "mexico": "mexico",
            "colombia": "colombia",
            "chile": "chile"
        }
        for keyword, country in country_keywords.items():
            if keyword in query.lower():
                entities["countries"].append(country)

        # Búsqueda de estilos
        style_keywords = {
            "punchline": "punchline",
            "flow": "flow",
            "trap": "trap",
            "wordplay": "wordplay",
            "storytelling": "storytelling",
            "agresivo": "aggressive",
            "agresiva": "aggressive",
            "técnico": "technical",
            "tecnico": "technical"
        }
        for keyword, style in style_keywords.items():
            if keyword in query.lower():
                entities["styles"].append(style)

        return entities

    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Procesa una consulta completa usando el ciclo de tool-loop.
        Retorna resultado con pensamiento, herramientas usadas y respuesta final.
        """
        self.iteration_count = 0
        result = {
            "query": user_query,
            "intent": None,
            "tool_calls": [],
            "ambiguities": [],
            "final_answer": "",
            "error": None
        }

        try:
            # Paso 1: Extraer intención
            intent = self._extract_intent(user_query)
            result["intent"] = intent

            # Paso 2: Ciclo de tool-loop
            tool_result = self._execute_tool_loop(user_query, intent)

            if tool_result.get("error"):
                result["error"] = tool_result["error"]
                return result

            if tool_result.get("ambiguities"):
                result["ambiguities"] = tool_result["ambiguities"]

            result["tool_calls"] = tool_result.get("tool_calls", [])

            # Paso 3: Generar respuesta final
            final_answer = self._generate_response(
                user_query,
                tool_result.get("data", {}),
                intent
            )
            result["final_answer"] = final_answer

        except Exception as e:
            result["error"] = str(e)

        return result

    def _execute_tool_loop(self, query: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el ciclo de herramientas basado en la intención.
        Implementa validación y manejo de ambigüedades.
        """
        self.iteration_count = 0
        tool_calls = []
        data = {}
        ambiguities = []

        try:
            match intent["type"]:
                case "head_to_head":
                    tool_calls, data, ambiguities = self._handle_head_to_head(query)

                case "ranking":
                    tool_calls, data, ambiguities = self._handle_ranking(query)

                case "statistics":
                    tool_calls, data, ambiguities = self._handle_statistics(query)

                case "event_details":
                    tool_calls, data, ambiguities = self._handle_event_details(query)

                case "history":
                    tool_calls, data, ambiguities = self._handle_history(query)

                case "style_analysis":
                    tool_calls, data, ambiguities = self._handle_style_analysis(query)

                case _:
                    tool_calls, data, ambiguities = self._handle_general_search(query)

            return {
                "tool_calls": tool_calls,
                "data": data,
                "ambiguities": ambiguities
            }

        except Exception as e:
            return {"error": str(e)}

    def _handle_head_to_head(self, query: str) -> Tuple[List, Dict, List]:
        """Maneja consultas de H2H entre dos MCs."""
        tool_calls = []
        ambiguities = []

        # Buscar dos nombres en la consulta
        parts = query.split("vs" if "vs" in query.lower() else "versus")
        if len(parts) != 2:
            return tool_calls, {}, ["No se pueden identificar dos oponentes claros"]

        name1 = parts[0].strip()
        name2 = parts[1].strip()

        # Búsqueda de ambos nombres
        results1 = self.toolkit.search_person(name1)
        results2 = self.toolkit.search_person(name2)

        # Validación de ambigüedades
        if len(results1) > 1:
            ambiguities.append({
                "field": "mc1",
                "query": name1,
                "options": results1
            })
        if len(results2) > 1:
            ambiguities.append({
                "field": "mc2",
                "query": name2,
                "options": results2
            })

        if ambiguities:
            return tool_calls, {}, ambiguities

        if not results1 or not results2:
            return tool_calls, {}, ["No se encontraron uno o ambos MCs"]

        person1_id = results1[0]["id"]
        person2_id = results2[0]["id"]

        # Llamada a herramienta
        tool_calls.append({
            "tool": "get_head_to_head",
            "params": {"person1_id": person1_id, "person2_id": person2_id}
        })

        h2h_data = self.toolkit.get_head_to_head(person1_id, person2_id)

        return tool_calls, {"h2h": h2h_data}, ambiguities

    def _handle_ranking(self, query: str) -> Tuple[List, Dict, List]:
        """Maneja consultas de ranking y top performers."""
        tool_calls = []

        # Extraer país si está disponible
        country = None
        for entity_country in self._extract_entities(query)["countries"]:
            country = entity_country
            break

        tool_calls.append({
            "tool": "get_top_performers",
            "params": {"country": country, "limit": 10}
        })

        top_performers = self.toolkit.get_top_performers(country, limit=10)

        return tool_calls, {"top_performers": top_performers}, []

    def _handle_statistics(self, query: str) -> Tuple[List, Dict, List]:
        """Maneja consultas de estadísticas."""
        tool_calls = []

        # Buscar MC
        results = self.toolkit.search_person(query)
        if not results:
            return tool_calls, {}, ["No se encontró el MC"]

        person_id = results[0]["id"]

        tool_calls.append({
            "tool": "get_person_statistics",
            "params": {"person_id": person_id}
        })

        stats = self.toolkit.get_person_statistics(person_id)
        battles = self.toolkit.get_battles_by_person(person_id, limit=10)

        return tool_calls, {"statistics": stats, "recent_battles": battles}, []

    def _handle_event_details(self, query: str) -> Tuple[List, Dict, List]:
        """Maneja consultas de eventos."""
        tool_calls = []

        results = self.toolkit.search_event(query)
        if not results:
            return tool_calls, {}, ["No se encontró el evento"]

        event_id = results[0]["id"]

        tool_calls.append({
            "tool": "get_event_details",
            "params": {"event_id": event_id}
        })

        event_data = self.toolkit.get_event_details(event_id)

        return tool_calls, {"event": event_data}, []

    def _handle_history(self, query: str) -> Tuple[List, Dict, List]:
        """Maneja consultas de historial."""
        tool_calls = []

        results = self.toolkit.search_person(query)
        if not results:
            return tool_calls, {}, ["No se encontró el MC"]

        person_id = results[0]["id"]

        tool_calls.append({
            "tool": "get_timeline",
            "params": {"person_id": person_id}
        })

        timeline = self.toolkit.get_timeline(person_id)
        events = self.toolkit.get_person_events(person_id)

        return tool_calls, {"timeline": timeline, "events": events}, []

    def _handle_style_analysis(self, query: str) -> Tuple[List, Dict, List]:
        """Maneja análisis de estilos."""
        tool_calls = []
        entities = self._extract_entities(query)

        if not entities["styles"]:
            return tool_calls, {}, ["No se especificó un estilo"]

        style = entities["styles"][0]

        tool_calls.append({
            "tool": "search_by_style",
            "params": {"style": style}
        })

        people_by_style = self.toolkit.search_by_style(style)

        return tool_calls, {"people_by_style": people_by_style}, []

    def _handle_general_search(self, query: str) -> Tuple[List, Dict, List]:
        """Maneja búsquedas generales."""
        tool_calls = []

        # Intentar búsqueda como persona primero
        person_results = self.toolkit.search_person(query, threshold=70)
        if person_results:
            tool_calls.append({"tool": "search_person", "params": {"query": query}})
            return tool_calls, {"people": person_results}, []

        # Intentar búsqueda como evento
        event_results = self.toolkit.search_event(query, threshold=70)
        if event_results:
            tool_calls.append({"tool": "search_event", "params": {"query": query}})
            return tool_calls, {"events": event_results}, []

        return tool_calls, {}, ["No se encontraron resultados para la búsqueda"]

    def _generate_response(self, query: str, data: Dict[str, Any], intent: Dict[str, Any]) -> str:
        """
        Genera una respuesta en lenguaje natural basada en los datos obtenidos.
        """
        if not data:
            return "No se encontraron resultados para tu consulta."

        # Prompt para generar respuesta natural
        prompt_template = ChatPromptTemplate.from_template(
            """
        Pregunta del usuario: {query}

        Tipo de consulta detectado: {intent_type}

        Datos obtenidos:
        {data}

        Por favor, responde la pregunta original de forma clara, conversacional y en ESPAÑOL.
        Si los datos no responden completamente la pregunta, indica qué información está disponible.
        Sé conciso pero informativo. Si hay números (win rates, estadísticas), preséntales de forma clara.
        """
        )

        chain = prompt_template | self.llm | StrOutputParser()

        response = chain.invoke({
            "query": query,
            "intent_type": intent.get("type", "general"),
            "data": json.dumps(data, ensure_ascii=False, indent=2, default=str)
        })

        return response.strip()


class AmbiguityResolver:
    """Manejador para resolver ambigüedades en consultas."""

    @staticmethod
    def ask_for_clarification(ambiguities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Crea un mensaje para pedir aclaración al usuario.
        """
        return {
            "status": "ambiguous",
            "message": "Se encontraron múltiples opciones. Por favor, especifica cuál prefieres:",
            "ambiguities": ambiguities
        }

    @staticmethod
    def resolve_with_context(ambiguities: List[Dict[str, Any]], user_clarification: str) -> Optional[int]:
        """
        Resuelve ambigüedades basándose en aclaración del usuario.
        """
        # Lógica de resolución simple
        if ambiguities:
            # En una implementación real, buscaría coincidencias en la aclaración
            return ambiguities[0]["options"][0]["id"]
        return None
