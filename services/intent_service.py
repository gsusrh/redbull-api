"""
Intent Service - Integración con BatallaAgent
Reemplaza _extract_intent() con clasificador MiniLM robusto
"""

import logging
from typing import Dict, Any, Optional
import time

from services.minilm_intent_classifier import (
    get_intent_classifier,
    IntentPrediction
)

logger = logging.getLogger(__name__)


class IntentService:
    """
    Servicio para extraer intenciones de queries
    Usa MiniLM + fallback heurístico
    """

    # Mapeo de intenciones MiniLM a tipos de handler
    INTENT_HANDLERS = {
        "head_to_head": "head_to_head",
        "statistics": "statistics",
        "ranking": "ranking",
        "event_details": "event_details",
        "history": "history",
        "style_analysis": "style_analysis",
        "battle_details": "battle_details",
        "battle_search": "battle_search",
        "mc_search": "mc_search",
        "country_analysis": "country_analysis",
        "year_statistics": "year_statistics",
        "tournament_info": "tournament_info",
        "general_search": "general_search",
    }

    def __init__(self):
        """Inicializa el servicio"""
        self.classifier = get_intent_classifier(use_fallback=True)
        logger.info("✅ IntentService inicializado con MiniLM")

    def extract_intent(self, query: str) -> Dict[str, Any]:
        """
        Extrae intención de una query
        Mucho más robusto que la versión anterior

        Args:
            query: Pregunta del usuario

        Returns:
            Dict con:
                - type: tipo de intención
                - confidence: confianza (0-1)
                - similarity_score: similitud con ejemplos
                - description: descripción de intención
                - alternatives: intenciones alternativas
        """
        start_time = time.time()

        # Clasifica con MiniLM
        prediction: IntentPrediction = self.classifier.classify(query)

        elapsed_ms = (time.time() - start_time) * 1000

        logger.info(
            f"🎯 Intent: {prediction.intent} "
            f"({prediction.confidence:.2%}) "
            f"[{elapsed_ms:.1f}ms]"
        )

        return {
            "type": prediction.intent,
            "confidence": prediction.confidence,
            "similarity_score": prediction.similarity_score,
            "description": self.classifier.classifier.get_description(prediction.intent),
            "alternatives": [
                {"intent": alt[0], "score": alt[1]}
                for alt in prediction.alternatives
            ],
            "elapsed_ms": elapsed_ms,
            "model": "minilm-l12-v2"
        }

    def extract_intent_with_explanation(self, query: str) -> Dict[str, Any]:
        """
        Extrae intención con explicación detallada
        Útil para debugging y análisis
        """
        prediction = self.classifier.classify(query)
        explanation = self.classifier.classifier.explain_prediction(query, prediction)

        return {
            "query": query,
            "predicted_intent": prediction.intent,
            "confidence": prediction.confidence,
            "description": explanation["description"],
            "examples_from_dataset": explanation["examples_from_dataset"],
            "alternatives": explanation["alternatives"],
            "similarity_score": prediction.similarity_score,
        }

    def batch_extract_intents(self, queries: list) -> list:
        """
        Extrae intenciones para múltiples queries de una vez
        Más eficiente que llamar extract_intent() para cada una
        """
        start_time = time.time()

        predictions = self.classifier.classifier.batch_predict(queries)

        elapsed_ms = (time.time() - start_time) * 1000

        results = []
        for query, prediction in zip(queries, predictions):
            results.append({
                "query": query,
                "type": prediction.intent,
                "confidence": prediction.confidence,
                "similarity_score": prediction.similarity_score,
            })

        logger.info(f"✅ Batch: {len(queries)} queries en {elapsed_ms:.1f}ms")

        return results

    def is_confident(self, query: str, threshold: float = 0.70) -> bool:
        """
        Retorna True si la confianza está por encima del threshold
        """
        intent_result = self.extract_intent(query)
        return intent_result["confidence"] >= threshold

    def get_fallback_intent_from_keywords(self, query: str) -> Optional[str]:
        """
        Intenta extraer intención usando palabras clave simples
        Para casos donde MiniLM no está disponible
        """
        query_lower = query.lower()

        keywords_map = {
            "head_to_head": ["vs", "versus", "enfrenta", "batalla entre", "contra", "pelea"],
            "ranking": ["top", "ranking", "mejores", "leaderboard", "posiciones"],
            "statistics": ["estadísticas", "estadisticas", "stats", "números", "record", "win rate"],
            "event_details": ["evento", "batalla", "gallos", "final"],
            "history": ["historial", "carrera", "trayectoria", "historia"],
            "style_analysis": ["estilo", "flow", "técnica", "cómo fluye"],
            "battle_search": ["batallas de", "todas las batallas"],
            "mc_search": ["quién es", "quien es", "información de"],
        }

        for intent, keywords in keywords_map.items():
            if any(kw in query_lower for kw in keywords):
                return intent

        return None


# Instancia global del servicio
_intent_service: IntentService = None


def get_intent_service() -> IntentService:
    """Factory para obtener instancia del servicio (singleton)"""
    global _intent_service

    if _intent_service is None:
        _intent_service = IntentService()

    return _intent_service


# Para usar en BatallaAgent
def extract_intent_minilm(query: str) -> Dict[str, Any]:
    """
    Función helper para reemplazar agents._extract_intent()
    Uso:
        from services.intent_service import extract_intent_minilm
        intent = extract_intent_minilm("Dani vs Chuty")
    """
    service = get_intent_service()
    return service.extract_intent(query)
