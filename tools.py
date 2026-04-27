"""
Red Bull Batalla Agent Toolkit: Suite completa de herramientas para consultas inteligentes.
Incluye búsqueda, estadísticas, análisis y validación de datos.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
import unidecode
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from models import (
    Person, Event, Battle, Intervention, PersonStatistic,
    BattleStatistic, HeadToHeadRecord, EventParticipation,
    CountryEnum, RoundEnum, StyleEnum, BattleFormatEnum
)


class BatallaToolkit:
    """Herramientas centralizadas para la suite de agentes de Red Bull Batalla."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self._normalize_cache = {}

    @staticmethod
    def _normalize_string(s: str) -> str:
        """Normaliza: sin acentos, minúsculas, espacios extra removidos."""
        if not isinstance(s, str):
            return ""
        return unidecode.unidecode(s).lower().strip()

    def search_person(self, query: str, threshold: int = 80) -> List[Dict[str, Any]]:
        """
        Busca un MC/freestyler por AKA con búsqueda difusa.
        Retorna lista de posibles coincidencias con score de similitud.
        """
        normalized_query = self._normalize_string(query)
        all_people = self.db.query(Person).all()

        if not all_people:
            return []

        matches = []
        for person in all_people:
            normalized_aka = self._normalize_string(person.aka)
            score = fuzz.token_set_ratio(normalized_query, normalized_aka)

            if score >= threshold:
                matches.append({
                    "id": person.id,
                    "aka": person.aka,
                    "full_name": person.full_name,
                    "country": person.country.value if person.country else None,
                    "style": person.style.value if person.style else None,
                    "debut_year": person.debut_year,
                    "match_score": score
                })

        return sorted(matches, key=lambda x: x["match_score"], reverse=True)

    def search_event(self, query: str, threshold: int = 75) -> List[Dict[str, Any]]:
        """
        Busca un evento por nombre con búsqueda difusa.
        """
        normalized_query = self._normalize_string(query)
        all_events = self.db.query(Event).all()

        if not all_events:
            return []

        matches = []
        for event in all_events:
            normalized_name = self._normalize_string(event.name)
            score = fuzz.token_set_ratio(normalized_query, normalized_name)

            if score >= threshold:
                matches.append({
                    "id": event.id,
                    "name": event.name,
                    "event_type": event.event_type.value if event.event_type else None,
                    "year": event.year,
                    "country": event.country.value if event.country else None,
                    "city": event.city,
                    "place": event.place,
                    "match_score": score
                })

        return sorted(matches, key=lambda x: x["match_score"], reverse=True)

    def get_person_by_id(self, person_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene información completa de una persona por ID."""
        person = self.db.query(Person).filter(Person.id == person_id).first()
        if not person:
            return None

        return {
            "id": person.id,
            "aka": person.aka,
            "full_name": person.full_name,
            "country": person.country.value if person.country else None,
            "style": person.style.value if person.style else None,
            "debut_year": person.debut_year,
            "biography": person.biography
        }

    def get_person_statistics(self, person_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene estadísticas completas de una persona.
        Incluye: wins, losses, win_rate, streaks, etc.
        """
        stats = self.db.query(PersonStatistic).filter(
            PersonStatistic.person_id == person_id
        ).first()

        if not stats:
            return self._calculate_person_statistics(person_id)

        return {
            "person_id": person_id,
            "total_battles": stats.total_battles,
            "total_wins": stats.total_wins,
            "total_losses": stats.total_losses,
            "win_rate": f"{stats.win_rate * 100:.2f}%",
            "current_win_streak": stats.current_win_streak,
            "longest_win_streak": stats.longest_win_streak,
            "avg_battle_duration_seconds": stats.avg_battle_duration,
            "total_interventions": stats.total_interventions,
            "avg_words_per_intervention": stats.avg_words_per_intervention,
            "updated_at": stats.updated_at
        }

    def _calculate_person_statistics(self, person_id: int) -> Dict[str, Any]:
        """Calcula estadísticas dinámicamente si no están cacheadas."""
        battles = self.db.query(Battle).filter(
            or_(Battle.mc1_id == person_id, Battle.mc2_id == person_id)
        ).all()

        wins = len([b for b in battles if b.winner_id == person_id])
        total = len(battles)
        win_rate = wins / total if total > 0 else 0.0

        # Racha de victorias actual
        current_streak = 0
        for battle in sorted(battles, key=lambda b: b.battle_date or datetime.utcnow(), reverse=True):
            if battle.winner_id == person_id:
                current_streak += 1
            else:
                break

        # Racha más larga
        longest_streak = 0
        temp_streak = 0
        for battle in sorted(battles, key=lambda b: b.battle_date or datetime.utcnow()):
            if battle.winner_id == person_id:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 0

        return {
            "person_id": person_id,
            "total_battles": total,
            "total_wins": wins,
            "total_losses": total - wins,
            "win_rate": f"{win_rate * 100:.2f}%",
            "current_win_streak": current_streak,
            "longest_win_streak": longest_streak,
            "status": "calculated_on_demand"
        }

    def get_head_to_head(self, person1_id: int, person2_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el historial directo entre dos MCs.
        """
        h2h = self.db.query(HeadToHeadRecord).filter(
            or_(
                and_(HeadToHeadRecord.person1_id == person1_id, HeadToHeadRecord.person2_id == person2_id),
                and_(HeadToHeadRecord.person1_id == person2_id, HeadToHeadRecord.person2_id == person1_id)
            )
        ).first()

        if not h2h:
            return self._calculate_head_to_head(person1_id, person2_id)

        person1 = self.get_person_by_id(person1_id)
        person2 = self.get_person_by_id(person2_id)

        return {
            "person1": person1["aka"],
            "person1_id": person1_id,
            "person1_wins": h2h.person1_wins if h2h.person1_id == person1_id else h2h.person2_wins,
            "person2": person2["aka"],
            "person2_id": person2_id,
            "person2_wins": h2h.person2_wins if h2h.person2_id == person2_id else h2h.person1_wins,
            "total_encounters": h2h.total_encounters,
            "last_encounter": h2h.last_encounter_date,
            "battles": self._get_h2h_battles(person1_id, person2_id)
        }

    def _calculate_head_to_head(self, person1_id: int, person2_id: int) -> Dict[str, Any]:
        """Calcula H2H dinámicamente."""
        battles = self.db.query(Battle).filter(
            or_(
                and_(Battle.mc1_id == person1_id, Battle.mc2_id == person2_id),
                and_(Battle.mc1_id == person2_id, Battle.mc2_id == person1_id)
            )
        ).all()

        person1_wins = len([b for b in battles if b.winner_id == person1_id])
        person2_wins = len([b for b in battles if b.winner_id == person2_id])

        person1 = self.get_person_by_id(person1_id)
        person2 = self.get_person_by_id(person2_id)

        return {
            "person1": person1["aka"],
            "person1_id": person1_id,
            "person1_wins": person1_wins,
            "person2": person2["aka"],
            "person2_id": person2_id,
            "person2_wins": person2_wins,
            "total_encounters": len(battles),
            "battles": self._get_h2h_battles(person1_id, person2_id)
        }

    def _get_h2h_battles(self, person1_id: int, person2_id: int) -> List[Dict[str, Any]]:
        """Obtiene los detalles de los enfrentamientos H2H."""
        battles = self.db.query(Battle).filter(
            or_(
                and_(Battle.mc1_id == person1_id, Battle.mc2_id == person2_id),
                and_(Battle.mc1_id == person2_id, Battle.mc2_id == person1_id)
            )
        ).order_by(desc(Battle.battle_date)).all()

        result = []
        for battle in battles:
            event = self.db.query(Event).filter(Event.id == battle.event_id).first()
            result.append({
                "battle_id": battle.id,
                "event": event.name if event else "Unknown",
                "year": event.year if event else None,
                "round": battle.round.value if battle.round else None,
                "winner_id": battle.winner_id,
                "winner_aka": self.get_person_by_id(battle.winner_id)["aka"] if battle.winner_id else "Draw",
                "date": battle.battle_date
            })

        return result

    def get_person_by_country(self, country: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los MCs de un país específico.
        """
        try:
            country_enum = CountryEnum[country.upper().replace(" ", "_")]
        except KeyError:
            return {"error": f"País no reconocido: {country}"}

        people = self.db.query(Person).filter(Person.country == country_enum).all()

        return [
            {
                "id": p.id,
                "aka": p.aka,
                "country": p.country.value,
                "style": p.style.value if p.style else None,
                "debut_year": p.debut_year
            }
            for p in people
        ]

    def get_event_participants(self, event_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los participantes de un evento.
        """
        participations = self.db.query(EventParticipation).filter(
            EventParticipation.event_id == event_id
        ).all()

        result = []
        for participation in participations:
            person = self.get_person_by_id(participation.person_id)
            result.append({
                "person": person,
                "placement": participation.placement,
                "eliminated_round": participation.eliminated_round.value if participation.eliminated_round else None,
                "battles_in_event": participation.battles_in_event,
                "wins_in_event": participation.wins_in_event
            })

        return result

    def get_battles_by_person(self, person_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtiene los últimos enfrentamientos de una persona.
        """
        battles = self.db.query(Battle).filter(
            or_(Battle.mc1_id == person_id, Battle.mc2_id == person_id)
        ).order_by(desc(Battle.battle_date)).limit(limit).all()

        result = []
        for battle in battles:
            opponent_id = battle.mc2_id if battle.mc1_id == person_id else battle.mc1_id
            opponent = self.get_person_by_id(opponent_id)
            event = self.db.query(Event).filter(Event.id == battle.event_id).first()

            result.append({
                "battle_id": battle.id,
                "opponent": opponent["aka"],
                "opponent_id": opponent_id,
                "event": event.name if event else "Unknown",
                "year": event.year if event else None,
                "round": battle.round.value if battle.round else None,
                "result": "WIN" if battle.winner_id == person_id else "LOSS" if battle.winner_id else "UNKNOWN",
                "date": battle.battle_date
            })

        return result

    def get_battles_by_event(self, event_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las batallas de un evento, organizadas por ronda.
        """
        battles = self.db.query(Battle).filter(
            Battle.event_id == event_id
        ).order_by(Battle.round, Battle.id).all()

        result = []
        for battle in battles:
            mc1 = self.get_person_by_id(battle.mc1_id)
            mc2 = self.get_person_by_id(battle.mc2_id)
            winner = self.get_person_by_id(battle.winner_id) if battle.winner_id else None

            result.append({
                "battle_id": battle.id,
                "round": battle.round.value if battle.round else None,
                "format": battle.battle_format.value if battle.battle_format else None,
                "mc1": mc1["aka"],
                "mc2": mc2["aka"],
                "winner": winner["aka"] if winner else "Not decided",
                "date": battle.battle_date
            })

        return result

    def get_event_details(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene todos los detalles de un evento.
        """
        event = self.db.query(Event).filter(Event.id == event_id).first()

        if not event:
            return None

        participants = self.get_event_participants(event_id)
        battles = self.get_battles_by_event(event_id)

        return {
            "id": event.id,
            "name": event.name,
            "event_type": event.event_type.value if event.event_type else None,
            "year": event.year,
            "country": event.country.value if event.country else None,
            "city": event.city,
            "place": event.place,
            "description": event.description,
            "total_participants": event.total_participants,
            "prize_pool": event.prize_pool,
            "participants": len(participants),
            "battles": len(battles),
            "battles_list": battles
        }

    def get_person_events(self, person_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los eventos en los que ha participado una persona.
        """
        participations = self.db.query(EventParticipation).filter(
            EventParticipation.person_id == person_id
        ).order_by(desc(EventParticipation.event_id)).all()

        result = []
        for participation in participations:
            event = self.db.query(Event).filter(Event.id == participation.event_id).first()
            result.append({
                "event_id": event.id,
                "event_name": event.name,
                "event_type": event.event_type.value if event.event_type else None,
                "year": event.year,
                "country": event.country.value if event.country else None,
                "placement": participation.placement,
                "eliminated_round": participation.eliminated_round.value if participation.eliminated_round else None,
                "battles_in_event": participation.battles_in_event,
                "wins_in_event": participation.wins_in_event
            })

        return result

    def get_battles_by_year(self, year: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las batallas de un año específico.
        """
        events = self.db.query(Event).filter(Event.year == year).all()
        event_ids = [e.id for e in events]

        if not event_ids:
            return []

        battles = self.db.query(Battle).filter(Battle.event_id.in_(event_ids)).all()

        result = []
        for battle in battles:
            mc1 = self.get_person_by_id(battle.mc1_id)
            mc2 = self.get_person_by_id(battle.mc2_id)
            event = self.db.query(Event).filter(Event.id == battle.event_id).first()

            result.append({
                "battle_id": battle.id,
                "event": event.name if event else "Unknown",
                "round": battle.round.value if battle.round else None,
                "mc1": mc1["aka"],
                "mc2": mc2["aka"],
                "winner": self.get_person_by_id(battle.winner_id)["aka"] if battle.winner_id else "Unknown",
                "date": battle.battle_date
            })

        return result

    def get_battles_by_round(self, event_id: int, round_name: str) -> List[Dict[str, Any]]:
        """
        Obtiene todas las batallas de una ronda específica en un evento.
        """
        try:
            round_enum = RoundEnum[round_name.upper().replace("-", "_")]
        except KeyError:
            return {"error": f"Ronda no reconocida: {round_name}"}

        battles = self.db.query(Battle).filter(
            and_(Battle.event_id == event_id, Battle.round == round_enum)
        ).all()

        result = []
        for battle in battles:
            mc1 = self.get_person_by_id(battle.mc1_id)
            mc2 = self.get_person_by_id(battle.mc2_id)
            winner = self.get_person_by_id(battle.winner_id) if battle.winner_id else None

            result.append({
                "battle_id": battle.id,
                "mc1": mc1["aka"],
                "mc2": mc2["aka"],
                "winner": winner["aka"] if winner else "Not decided",
                "date": battle.battle_date
            })

        return result

    def get_top_performers(self, country: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene los MCs con mejor win rate (top performers).
        Opcionalmente filtrado por país.
        """
        query = self.db.query(PersonStatistic).order_by(
            desc(PersonStatistic.win_rate)
        ).limit(limit)

        if country:
            try:
                country_enum = CountryEnum[country.upper().replace(" ", "_")]
                people = self.db.query(Person).filter(Person.country == country_enum).all()
                person_ids = [p.id for p in people]
                query = query.filter(PersonStatistic.person_id.in_(person_ids))
            except KeyError:
                return {"error": f"País no reconocido: {country}"}

        stats = query.all()

        result = []
        for stat in stats:
            person = self.get_person_by_id(stat.person_id)
            result.append({
                "aka": person["aka"],
                "country": person["country"],
                "total_battles": stat.total_battles,
                "wins": stat.total_wins,
                "win_rate": f"{stat.win_rate * 100:.2f}%",
                "current_streak": stat.current_win_streak
            })

        return result

    def search_by_style(self, style: str) -> List[Dict[str, Any]]:
        """
        Obtiene MCs que tengan un estilo específico.
        """
        try:
            style_enum = StyleEnum[style.upper()]
        except KeyError:
            return {"error": f"Estilo no reconocido: {style}"}

        people = self.db.query(Person).filter(Person.style == style_enum).all()

        return [
            {
                "id": p.id,
                "aka": p.aka,
                "country": p.country.value if p.country else None,
                "style": p.style.value,
                "debut_year": p.debut_year
            }
            for p in people
        ]

    def get_timeline(self, person_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene una línea de tiempo de batallas y logros de una persona.
        """
        battles = self.get_battles_by_person(person_id, limit=100)
        events = self.get_person_events(person_id)

        timeline = []
        for battle in battles:
            timeline.append({
                "type": "battle",
                "date": battle["date"],
                "event": battle["event"],
                "opponent": battle["opponent"],
                "result": battle["result"]
            })

        for event in events:
            timeline.append({
                "type": "event",
                "date": None,
                "year": event["year"],
                "event_name": event["event_name"],
                "placement": event["placement"]
            })

        return sorted(timeline, key=lambda x: x.get("date") or datetime.utcnow(), reverse=True)

    def get_ambiguity_clarification(self, aka: str) -> Dict[str, Any]:
        """
        Si hay ambigüedad (mismo AKA en diferentes países),
        retorna las opciones para que el usuario aclare.
        """
        normalized = self._normalize_string(aka)
        people = self.db.query(Person).all()

        matches = []
        for person in people:
            if self._normalize_string(person.aka) == normalized:
                matches.append({
                    "id": person.id,
                    "aka": person.aka,
                    "country": person.country.value if person.country else None,
                    "style": person.style.value if person.style else None
                })

        if len(matches) > 1:
            return {
                "ambiguous": True,
                "aka": aka,
                "options": matches,
                "message": f"Se encontraron {len(matches)} MCs con AKA similar. Por favor aclara cuál es:"
            }

        return {"ambiguous": False}

    def get_battle_analysis(self, battle_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene análisis detallado de una batalla.
        """
        battle = self.db.query(Battle).filter(Battle.id == battle_id).first()

        if not battle:
            return None

        mc1 = self.get_person_by_id(battle.mc1_id)
        mc2 = self.get_person_by_id(battle.mc2_id)
        event = self.db.query(Event).filter(Event.id == battle.event_id).first()
        stats = self.db.query(BattleStatistic).filter(BattleStatistic.battle_id == battle_id).first()

        return {
            "battle_id": battle.id,
            "event": event.name if event else "Unknown",
            "year": event.year if event else None,
            "round": battle.round.value if battle.round else None,
            "mc1": mc1["aka"],
            "mc1_id": battle.mc1_id,
            "mc2": mc2["aka"],
            "mc2_id": battle.mc2_id,
            "winner": self.get_person_by_id(battle.winner_id)["aka"] if battle.winner_id else "Unknown",
            "format": battle.battle_format.value if battle.battle_format else None,
            "duration_seconds": battle.duration_seconds,
            "video_url": battle.video_url,
            "judges_decision": battle.judges_decision,
            "statistics": {
                "mc1_punchlines": stats.mc1_total_punchlines if stats else None,
                "mc2_punchlines": stats.mc2_total_punchlines if stats else None,
                "mc1_rhyme_density": stats.mc1_avg_rhyme_density if stats else None,
                "mc2_rhyme_density": stats.mc2_avg_rhyme_density if stats else None,
                "crowd_reaction": stats.crowd_reaction if stats else None
            }
        }

    def list_all_events(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista todos los eventos, opcionalmente filtrados por año.
        """
        query = self.db.query(Event)

        if year:
            query = query.filter(Event.year == year)

        events = query.order_by(desc(Event.year)).all()

        return [
            {
                "id": e.id,
                "name": e.name,
                "event_type": e.event_type.value if e.event_type else None,
                "year": e.year,
                "country": e.country.value if e.country else None,
                "city": e.city,
                "participants": e.total_participants
            }
            for e in events
        ]

    def list_all_persons(self, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista todos los MCs, opcionalmente filtrados por país.
        """
        query = self.db.query(Person)

        if country:
            try:
                country_enum = CountryEnum[country.upper().replace(" ", "_")]
                query = query.filter(Person.country == country_enum)
            except KeyError:
                return {"error": f"País no reconocido: {country}"}

        people = query.order_by(Person.aka).all()

        return [
            {
                "id": p.id,
                "aka": p.aka,
                "country": p.country.value if p.country else None,
                "style": p.style.value if p.style else None,
                "debut_year": p.debut_year
            }
            for p in people
        ]
