"""
Servicio de scraping para ingesta de datos desde URLs de wikis y fuentes externas.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from models import Person, Event, Battle, CountryEnum, EventTypeEnum
from services.normalization_service import NormalizationService


class ScraperService:
    """Servicio para scrapear y procesar datos de eventos freestyle."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.normalizer = NormalizationService()

    async def scrape_event_participants(self, url: str) -> Dict[str, Any]:
        """
        Scrape participantes de un evento desde una URL.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            participants = []
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        name_cell = cells[0].get_text(strip=True)
                        country_cell = cells[1].get_text(strip=True) if len(cells) > 1 else None

                        if name_cell and country_cell:
                            participants.append({
                                "name": name_cell,
                                "country": country_cell
                            })

            return {
                "status": "success",
                "participants_found": len(participants),
                "participants": participants
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    async def scrape_battle_results(self, url: str) -> Dict[str, Any]:
        """
        Scrape resultados de batallas desde una URL.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            battles = []
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        mc1 = cells[0].get_text(strip=True)
                        mc2 = cells[1].get_text(strip=True)
                        winner = cells[2].get_text(strip=True)

                        battles.append({
                            "mc1": mc1,
                            "mc2": mc2,
                            "winner": winner
                        })

            return {
                "status": "success",
                "battles_found": len(battles),
                "battles": battles
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def ingest_person(self, aka: str, full_name: Optional[str],
                     country: str, style: Optional[str] = None,
                     debut_year: Optional[int] = None) -> Dict[str, Any]:
        """
        Ingiere una persona en la base de datos.
        Maneja duplicados mediante normalización.
        """
        try:
            # Normalizar país
            normalized_country = self.normalizer.normalize(country)
            country_enum = self._map_country(normalized_country)

            if not country_enum:
                return {
                    "status": "error",
                    "error": f"País no reconocido: {country}"
                }

            # Verificar si ya existe (por AKA normalizado + país)
            normalized_aka = self.normalizer.normalize(aka)
            existing = self.db.query(Person).filter(
                Person.aka == aka,
                Person.country == country_enum
            ).first()

            if existing:
                return {
                    "status": "exists",
                    "person_id": existing.id,
                    "message": f"La persona {aka} ya existe en la base de datos"
                }

            # Crear nueva persona
            person = Person(
                aka=aka,
                full_name=full_name,
                country=country_enum,
                style=self._map_style(style) if style else None,
                debut_year=debut_year
            )

            self.db.add(person)
            self.db.commit()

            return {
                "status": "created",
                "person_id": person.id,
                "aka": person.aka,
                "country": person.country.value
            }

        except Exception as e:
            self.db.rollback()
            return {
                "status": "error",
                "error": str(e)
            }

    def ingest_event(self, name: str, event_type: str, year: int,
                    country: str, city: Optional[str] = None,
                    place: Optional[str] = None,
                    total_participants: Optional[int] = None) -> Dict[str, Any]:
        """
        Ingiere un evento en la base de datos.
        """
        try:
            # Normalizar país
            normalized_country = self.normalizer.normalize(country)
            country_enum = self._map_country(normalized_country)

            if not country_enum:
                return {
                    "status": "error",
                    "error": f"País no reconocido: {country}"
                }

            # Normalizar tipo de evento
            event_type_enum = self._map_event_type(event_type)

            if not event_type_enum:
                return {
                    "status": "error",
                    "error": f"Tipo de evento no reconocido: {event_type}"
                }

            # Verificar duplicados
            existing = self.db.query(Event).filter(
                Event.name == name,
                Event.year == year,
                Event.country == country_enum
            ).first()

            if existing:
                return {
                    "status": "exists",
                    "event_id": existing.id,
                    "message": f"El evento {name} {year} ya existe"
                }

            # Crear nuevo evento
            event = Event(
                name=name,
                event_type=event_type_enum,
                year=year,
                country=country_enum,
                city=city,
                place=place,
                total_participants=total_participants
            )

            self.db.add(event)
            self.db.commit()

            return {
                "status": "created",
                "event_id": event.id,
                "name": event.name,
                "year": event.year,
                "country": event.country.value
            }

        except Exception as e:
            self.db.rollback()
            return {
                "status": "error",
                "error": str(e)
            }

    def ingest_battle(self, event_id: int, mc1_id: int, mc2_id: int,
                     winner_id: Optional[int] = None,
                     round_name: Optional[str] = None,
                     battle_format: str = "1v1") -> Dict[str, Any]:
        """
        Ingiere una batalla en la base de datos.
        """
        try:
            # Verificar que el evento existe
            event = self.db.query(Event).filter(Event.id == event_id).first()
            if not event:
                return {"status": "error", "error": f"Evento {event_id} no encontrado"}

            # Verificar que los MCs existen
            mc1 = self.db.query(Person).filter(Person.id == mc1_id).first()
            mc2 = self.db.query(Person).filter(Person.id == mc2_id).first()

            if not mc1 or not mc2:
                return {"status": "error", "error": "Uno o ambos MCs no encontrados"}

            # Normalizar ronda
            round_enum = self._map_round(round_name) if round_name else None

            # Crear batalla
            battle = Battle(
                event_id=event_id,
                mc1_id=mc1_id,
                mc2_id=mc2_id,
                winner_id=winner_id,
                round=round_enum,
                battle_format=self._map_battle_format(battle_format)
            )

            self.db.add(battle)
            self.db.commit()

            return {
                "status": "created",
                "battle_id": battle.id,
                "event_id": event_id,
                "mc1": mc1.aka,
                "mc2": mc2.aka
            }

        except Exception as e:
            self.db.rollback()
            return {
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    def _map_country(country_str: str) -> Optional[CountryEnum]:
        """Mapea string de país a enum."""
        mapping = {
            "spain": CountryEnum.SPAIN,
            "espana": CountryEnum.SPAIN,
            "españa": CountryEnum.SPAIN,
            "argentina": CountryEnum.ARGENTINA,
            "mexico": CountryEnum.MEXICO,
            "méxico": CountryEnum.MEXICO,
            "colombia": CountryEnum.COLOMBIA,
            "chile": CountryEnum.CHILE,
            "peru": CountryEnum.PERU,
            "perú": CountryEnum.PERU,
        }

        normalized = NormalizationService.normalize(country_str)
        return mapping.get(normalized)

    @staticmethod
    def _map_event_type(event_type_str: str) -> Optional[EventTypeEnum]:
        """Mapea string de tipo de evento a enum."""
        mapping = {
            "nacional": EventTypeEnum.NACIONAL,
            "internacional": EventTypeEnum.INTERNACIONAL,
            "regional": EventTypeEnum.REGIONAL,
            "street": EventTypeEnum.STREET,
        }

        normalized = NormalizationService.normalize(event_type_str)
        return mapping.get(normalized)

    @staticmethod
    def _map_round(round_str: str):
        """Mapea string de ronda a enum."""
        from models import RoundEnum
        mapping = {
            "final": RoundEnum.FINAL,
            "semifinal": RoundEnum.SEMIFINALS,
            "semifinales": RoundEnum.SEMIFINALS,
            "cuartos": RoundEnum.QUARTERFINALS,
            "quarterfinals": RoundEnum.QUARTERFINALS,
            "round_16": RoundEnum.ROUND_16,
            "16": RoundEnum.ROUND_16,
            "qualifying": RoundEnum.QUALIFYING,
        }

        normalized = NormalizationService.normalize(round_str)
        return mapping.get(normalized)

    @staticmethod
    def _map_battle_format(format_str: str) -> str:
        """Mapea string de formato a enum."""
        mapping = {
            "1v1": "1v1",
            "2v2": "2v2",
            "tag_team": "tag_team",
            "tournament": "tournament",
            "exhibition": "exhibition",
        }

        normalized = NormalizationService.normalize(format_str)
        return mapping.get(normalized, "1v1")

    @staticmethod
    def _map_style(style_str: str):
        """Mapea string de estilo a enum."""
        from models import StyleEnum
        mapping = {
            "punchline": StyleEnum.PUNCHLINE,
            "flow": StyleEnum.FLOW,
            "trap": StyleEnum.TRAP,
            "wordplay": StyleEnum.WORDPLAY,
            "storytelling": StyleEnum.STORYTELLING,
            "aggressive": StyleEnum.AGGRESSIVE,
            "agresivo": StyleEnum.AGGRESSIVE,
            "technical": StyleEnum.TECHNICAL,
            "tecnico": StyleEnum.TECHNICAL,
            "mixed": StyleEnum.MIXED,
        }

        normalized = NormalizationService.normalize(style_str)
        return mapping.get(normalized)
