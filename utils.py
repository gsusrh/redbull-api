"""
Utilidades generales para Red Bull Batalla Agent Suite.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class ResponseFormatter:
    """Formatea respuestas para diferentes contextos."""

    @staticmethod
    def format_error(error: str, code: int = 400) -> Dict[str, Any]:
        """Formatea error para respuesta HTTP."""
        return {
            "status": "error",
            "error": error,
            "code": code,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def format_success(data: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea respuesta exitosa."""
        return {
            "status": "success",
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def format_list(items: List[Dict[str, Any]], count: Optional[int] = None) -> Dict[str, Any]:
        """Formatea lista de resultados."""
        return {
            "status": "success",
            "items": items,
            "count": count or len(items),
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def format_sse(data: Dict[str, Any], event: Optional[str] = None) -> str:
        """Formatea datos para Server-Sent Events."""
        json_data = json.dumps(data, ensure_ascii=False, default=str)
        message = f"data: {json_data}\n\n"
        if event:
            message = f"event: {event}\n{message}"
        return message


class DataValidator:
    """Valida datos de entrada."""

    @staticmethod
    def validate_year(year: int) -> bool:
        """Valida que un año sea válido."""
        return 1990 <= year <= datetime.utcnow().year + 1

    @staticmethod
    def validate_country(country: str) -> bool:
        """Valida que un país sea válido."""
        from models import CountryEnum
        try:
            CountryEnum[country.upper().replace(" ", "_")]
            return True
        except KeyError:
            return False

    @staticmethod
    def validate_round(round_name: str) -> bool:
        """Valida que una ronda sea válida."""
        from models import RoundEnum
        try:
            RoundEnum[round_name.upper().replace("-", "_")]
            return True
        except KeyError:
            return False

    @staticmethod
    def validate_style(style: str) -> bool:
        """Valida que un estilo sea válido."""
        from models import StyleEnum
        try:
            StyleEnum[style.upper()]
            return True
        except KeyError:
            return False

    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email básico."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_url(url: str) -> bool:
        """Valida formato de URL básico."""
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None


class StatisticsCalculator:
    """Calcula estadísticas avanzadas."""

    @staticmethod
    def calculate_win_rate(wins: int, total: int) -> float:
        """Calcula porcentaje de victorias."""
        if total == 0:
            return 0.0
        return (wins / total) * 100

    @staticmethod
    def calculate_streak_efficiency(streak: int, total_battles: int) -> float:
        """Calcula eficiencia de racha."""
        if total_battles == 0:
            return 0.0
        return (streak / total_battles) * 100

    @staticmethod
    def calculate_head_to_head_advantage(wins: int, losses: int) -> float:
        """Calcula ventaja H2H."""
        total = wins + losses
        if total == 0:
            return 0.0
        return ((wins - losses) / total) * 100

    @staticmethod
    def calculate_consistency_score(wins: int, total: int) -> str:
        """Determina consistencia basada en win rate."""
        if total < 5:
            return "Datos insuficientes"

        rate = StatisticsCalculator.calculate_win_rate(wins, total)

        if rate >= 70:
            return "Muy consistente"
        elif rate >= 50:
            return "Consistente"
        elif rate >= 40:
            return "Promedio"
        else:
            return "Inconsistente"


class DateTimeHelper:
    """Ayudantes para manejo de fechas."""

    @staticmethod
    def format_date(date: datetime) -> str:
        """Formatea fecha para presentación."""
        if not date:
            return "Sin fecha"
        return date.strftime("%d/%m/%Y")

    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Formatea fecha y hora."""
        if not dt:
            return "Sin fecha"
        return dt.strftime("%d/%m/%Y %H:%M")

    @staticmethod
    def days_ago(date: datetime) -> int:
        """Calcula días desde una fecha."""
        if not date:
            return None
        delta = datetime.utcnow() - date
        return delta.days

    @staticmethod
    def format_duration(seconds: Optional[int]) -> str:
        """Formatea duración en segundos."""
        if not seconds:
            return "Duración desconocida"

        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"


class TextProcessor:
    """Procesa y formatea texto."""

    @staticmethod
    def truncate(text: str, max_length: int = 100) -> str:
        """Trunca texto a longitud máxima."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    @staticmethod
    def escape_html(text: str) -> str:
        """Escapa caracteres HTML."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    @staticmethod
    def clean_text(text: str) -> str:
        """Limpia texto removiendo caracteres especiales."""
        import re
        # Remover caracteres no imprimibles
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def highlight(text: str, keyword: str) -> str:
        """Destaca palabra clave en texto."""
        import re
        pattern = f"({re.escape(keyword)})"
        return re.sub(pattern, r"<mark>\1</mark>", text, flags=re.IGNORECASE)


class ComparisonHelper:
    """Ayuda en comparaciones de datos."""

    @staticmethod
    def compare_win_rates(rate1: float, rate2: float) -> Dict[str, Any]:
        """Compara dos win rates."""
        difference = rate1 - rate2
        better = "MC1" if difference > 0 else "MC2" if difference < 0 else "Igual"

        return {
            "rate1": rate1,
            "rate2": rate2,
            "difference": abs(difference),
            "better": better
        }

    @staticmethod
    def compare_streaks(streak1: int, streak2: int) -> Dict[str, Any]:
        """Compara rachas de victorias."""
        difference = streak1 - streak2
        better = "MC1" if difference > 0 else "MC2" if difference < 0 else "Igual"

        return {
            "streak1": streak1,
            "streak2": streak2,
            "difference": abs(difference),
            "better": better
        }

    @staticmethod
    def compare_statistics(stats1: Dict, stats2: Dict) -> Dict[str, Any]:
        """Compara estadísticas generales."""
        comparisons = {
            "win_rate": ComparisonHelper.compare_win_rates(
                stats1.get("win_rate", 0),
                stats2.get("win_rate", 0)
            ),
            "total_battles": {
                "mc1": stats1.get("total_battles", 0),
                "mc2": stats2.get("total_battles", 0)
            },
            "current_streak": ComparisonHelper.compare_streaks(
                stats1.get("current_win_streak", 0),
                stats2.get("current_win_streak", 0)
            )
        }
        return comparisons
