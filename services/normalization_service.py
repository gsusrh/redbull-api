"""
Servicio de normalización para manejar variaciones de nombres y entidades.
"""

import unidecode
from typing import Dict, List, Optional
from rapidfuzz import fuzz


class NormalizationService:
    """Normaliza strings y maneja variaciones de nombres."""

    @staticmethod
    def normalize(text: str) -> str:
        """
        Normaliza un string: sin acentos, minúsculas, espacios extra removidos.
        """
        if not isinstance(text, str):
            return ""
        # Remover acentos
        unaccented = unidecode.unidecode(text)
        # Minúsculas
        lowered = unaccented.lower()
        # Remover espacios extra
        stripped = lowered.strip()
        # Remover puntuación
        cleaned = ''.join(c for c in stripped if c.isalnum() or c.isspace())
        return cleaned

    @staticmethod
    def fuzzy_match(query: str, options: List[str], threshold: int = 80) -> List[tuple]:
        """
        Busca coincidencias difusas entre una consulta y opciones.
        Retorna lista de (opción, score) ordenada por score descendente.
        """
        matches = []
        normalized_query = NormalizationService.normalize(query)

        for option in options:
            normalized_option = NormalizationService.normalize(option)
            score = fuzz.token_set_ratio(normalized_query, normalized_option)

            if score >= threshold:
                matches.append((option, score))

        return sorted(matches, key=lambda x: x[1], reverse=True)

    @staticmethod
    def handle_typos(text: str) -> List[str]:
        """
        Genera variaciones plausibles de un texto para manejar typos.
        """
        variations = [text]

        # Si contiene 'z', añade versión con 's'
        if 'z' in text.lower():
            variations.append(text.replace('z', 's').replace('Z', 'S'))

        # Si contiene 'c', añade versión con 'k'
        if 'c' in text.lower():
            variations.append(text.replace('c', 'k').replace('C', 'K'))

        return variations

    @staticmethod
    def is_similar(text1: str, text2: str, threshold: int = 80) -> bool:
        """
        Verifica si dos textos son similares (fuzzy matching).
        """
        normalized1 = NormalizationService.normalize(text1)
        normalized2 = NormalizationService.normalize(text2)
        score = fuzz.token_set_ratio(normalized1, normalized2)
        return score >= threshold

    @staticmethod
    def extract_numbers(text: str) -> List[int]:
        """Extrae números de un texto."""
        import re
        return [int(x) for x in re.findall(r'\d+', text)]

    @staticmethod
    def remove_stop_words(text: str, stop_words: set = None) -> str:
        """Elimina palabras vacías (stop words)."""
        if stop_words is None:
            stop_words = {
                "un", "una", "el", "la", "de", "del", "que", "cual", "quien",
                "han", "ha", "es", "son", "ganado", "final", "y", "o", "en",
                "a", "los", "las", "te", "me", "mi", "se", "te"
            }

        words = text.lower().split()
        filtered = [w for w in words if w not in stop_words and len(w) > 2]
        return " ".join(filtered)
