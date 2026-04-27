"""
Modelos SQLAlchemy para Red Bull Batalla Agent Suite.
Define la estructura completa de la base de datos relacional.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey,
    Enum as SQLEnum, Table, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class CountryEnum(str, enum.Enum):
    SPAIN = "spain"
    ARGENTINA = "argentina"
    MEXICO = "mexico"
    COLOMBIA = "colombia"
    CHILE = "chile"
    PERU = "peru"
    ECUADOR = "ecuador"
    VENEZUELA = "venezuela"
    BRAZIL = "brazil"
    PANAMA = "panama"
    COSTA_RICA = "costa_rica"
    CUBA = "cuba"
    DOMINICAN_REPUBLIC = "dominican_republic"
    PUERTO_RICO = "puerto_rico"
    USA = "usa"
    FRANCE = "france"
    ITALY = "italy"
    PORTUGAL = "portugal"
    GERMANY = "germany"


class RoundEnum(str, enum.Enum):
    QUALIFYING = "qualifying"
    ROUND_16 = "round_16"
    QUARTERFINALS = "quarterfinals"
    SEMIFINALS = "semifinals"
    FINAL = "final"
    EXHIBITION = "exhibition"


class BattleFormatEnum(str, enum.Enum):
    ONE_VS_ONE = "1v1"
    TWO_VS_TWO = "2v2"
    TAG_TEAM = "tag_team"
    TOURNAMENT = "tournament"
    EXHIBITION = "exhibition"


class EventTypeEnum(str, enum.Enum):
    NACIONAL = "nacional"
    INTERNACIONAL = "internacional"
    REGIONAL = "regional"
    STREET = "street"


class StyleEnum(str, enum.Enum):
    PUNCHLINE = "punchline"
    FLOW = "flow"
    TRAP = "trap"
    WORDPLAY = "wordplay"
    STORYTELLING = "storytelling"
    AGGRESSIVE = "aggressive"
    TECHNICAL = "technical"
    MIXED = "mixed"


class Person(Base):
    """Modelo para MCs/Freestylers."""
    __tablename__ = "persons"
    __table_args__ = (
        UniqueConstraint("aka", "country", name="uq_person_aka_country"),
        Index("idx_aka", "aka"),
        Index("idx_country", "country"),
    )

    id = Column(Integer, primary_key=True, index=True)
    aka = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    country = Column(SQLEnum(CountryEnum), nullable=False, index=True)
    style = Column(SQLEnum(StyleEnum), nullable=True, default=StyleEnum.MIXED)
    debut_year = Column(Integer, nullable=True)
    biography = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    battles_as_mc1 = relationship("Battle", foreign_keys="Battle.mc1_id", back_populates="mc1")
    battles_as_mc2 = relationship("Battle", foreign_keys="Battle.mc2_id", back_populates="mc2")
    battles_as_winner = relationship("Battle", foreign_keys="Battle.winner_id", back_populates="winner")
    interventions = relationship("Intervention", back_populates="person")

    def __repr__(self):
        return f"<Person(id={self.id}, aka={self.aka}, country={self.country})>"


class Event(Base):
    """Modelo para eventos (nacionales, internacionales, etc.)."""
    __tablename__ = "events"
    __table_args__ = (
        Index("idx_event_name", "name"),
        Index("idx_event_country", "country"),
        Index("idx_event_year", "year"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    event_type = Column(SQLEnum(EventTypeEnum), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=True)
    country = Column(SQLEnum(CountryEnum), nullable=False, index=True)
    city = Column(String(255), nullable=True)
    place = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    total_participants = Column(Integer, nullable=True)
    prize_pool = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    battles = relationship("Battle", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event(id={self.id}, name={self.name}, year={self.year})>"


class Battle(Base):
    """Modelo para batallas individuales."""
    __tablename__ = "battles"
    __table_args__ = (
        Index("idx_battle_event", "event_id"),
        Index("idx_battle_mc1", "mc1_id"),
        Index("idx_battle_mc2", "mc2_id"),
        Index("idx_battle_winner", "winner_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    mc1_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    mc2_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    winner_id = Column(Integer, ForeignKey("persons.id"), nullable=True, index=True)
    battle_date = Column(DateTime, nullable=True)
    round = Column(SQLEnum(RoundEnum), nullable=True)
    battle_format = Column(SQLEnum(BattleFormatEnum), default=BattleFormatEnum.ONE_VS_ONE)
    duration_seconds = Column(Integer, nullable=True)
    video_url = Column(String(500), nullable=True)
    judges_decision = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    event = relationship("Event", back_populates="battles")
    mc1 = relationship("Person", foreign_keys=[mc1_id], back_populates="battles_as_mc1")
    mc2 = relationship("Person", foreign_keys=[mc2_id], back_populates="battles_as_mc2")
    winner = relationship("Person", foreign_keys=[winner_id], back_populates="battles_as_winner")
    interventions = relationship("Intervention", back_populates="battle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Battle(id={self.id}, event={self.event_id}, mc1={self.mc1_id}, mc2={self.mc2_id})>"


class Intervention(Base):
    """Modelo para intervenciones (barras) dentro de una batalla."""
    __tablename__ = "interventions"
    __table_args__ = (
        Index("idx_intervention_battle", "battle_id"),
        Index("idx_intervention_person", "person_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(Integer, ForeignKey("battles.id"), nullable=False, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    turn_number = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    battle = relationship("Battle", back_populates="interventions")
    person = relationship("Person", back_populates="interventions")
    lyric_analysis = relationship("LyricAnalysis", uselist=False, back_populates="intervention", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Intervention(id={self.id}, battle={self.battle_id}, person={self.person_id})>"


class LyricAnalysis(Base):
    """Modelo para análisis de letras/barras (metadatos lingüísticos)."""
    __tablename__ = "lyric_analysis"

    id = Column(Integer, primary_key=True, index=True)
    intervention_id = Column(Integer, ForeignKey("interventions.id"), nullable=False, unique=True)
    punchline_count = Column(Integer, default=0)
    rhyme_density = Column(Float, nullable=True)
    word_count = Column(Integer, default=0)
    unique_word_count = Column(Integer, default=0)
    offensive_language_count = Column(Integer, default=0)
    person_references_count = Column(Integer, default=0)
    style_tags = Column(String(500), nullable=True)
    keywords = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    intervention = relationship("Intervention", back_populates="lyric_analysis")

    def __repr__(self):
        return f"<LyricAnalysis(id={self.id}, intervention={self.intervention_id})>"


class PersonStatistic(Base):
    """Modelo para estadísticas pre-calculadas de personas (cache)."""
    __tablename__ = "person_statistics"
    __table_args__ = (
        Index("idx_person_stat_person", "person_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, unique=True)
    total_battles = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    current_win_streak = Column(Integer, default=0)
    longest_win_streak = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    avg_battle_duration = Column(Float, nullable=True)
    total_interventions = Column(Integer, default=0)
    avg_words_per_intervention = Column(Float, nullable=True)
    favorite_opponent_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    most_difficult_opponent_id = Column(Integer, ForeignKey("persons.id"), nullable=True)
    battles_by_country = Column(String(1000), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    person = relationship("Person", foreign_keys=[person_id])
    favorite_opponent = relationship("Person", foreign_keys=[favorite_opponent_id])
    most_difficult_opponent = relationship("Person", foreign_keys=[most_difficult_opponent_id])

    def __repr__(self):
        return f"<PersonStatistic(id={self.id}, person={self.person_id})>"


class BattleStatistic(Base):
    """Modelo para estadísticas detalladas de batallas."""
    __tablename__ = "battle_statistics"
    __table_args__ = (
        Index("idx_battle_stat_battle", "battle_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(Integer, ForeignKey("battles.id"), nullable=False, unique=True)
    mc1_avg_rhyme_density = Column(Float, nullable=True)
    mc2_avg_rhyme_density = Column(Float, nullable=True)
    mc1_total_punchlines = Column(Integer, default=0)
    mc2_total_punchlines = Column(Integer, default=0)
    mc1_avg_words_per_intervention = Column(Float, nullable=True)
    mc2_avg_words_per_intervention = Column(Float, nullable=True)
    mc1_offensive_language = Column(Integer, default=0)
    mc2_offensive_language = Column(Integer, default=0)
    total_interventions = Column(Integer, default=0)
    crowd_reaction = Column(String(255), nullable=True)
    judges_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    battle = relationship("Battle")

    def __repr__(self):
        return f"<BattleStatistic(id={self.id}, battle={self.battle_id})>"


class HeadToHeadRecord(Base):
    """Modelo para registrar históricos directos entre MCs."""
    __tablename__ = "head_to_head_records"
    __table_args__ = (
        UniqueConstraint("person1_id", "person2_id", name="uq_h2h"),
        Index("idx_h2h_person1", "person1_id"),
        Index("idx_h2h_person2", "person2_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    person1_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    person2_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    person1_wins = Column(Integer, default=0)
    person2_wins = Column(Integer, default=0)
    total_encounters = Column(Integer, default=0)
    last_encounter_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    person1 = relationship("Person", foreign_keys=[person1_id])
    person2 = relationship("Person", foreign_keys=[person2_id])

    def __repr__(self):
        return f"<HeadToHeadRecord(id={self.id}, p1={self.person1_id}, p2={self.person2_id})>"


class EventParticipation(Base):
    """Modelo para registrar participación de personas en eventos."""
    __tablename__ = "event_participations"
    __table_args__ = (
        UniqueConstraint("person_id", "event_id", name="uq_event_participation"),
        Index("idx_participation_person", "person_id"),
        Index("idx_participation_event", "event_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    placement = Column(Integer, nullable=True)
    eliminated_round = Column(SQLEnum(RoundEnum), nullable=True)
    battles_in_event = Column(Integer, default=0)
    wins_in_event = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    person = relationship("Person")
    event = relationship("Event")

    def __repr__(self):
        return f"<EventParticipation(person={self.person_id}, event={self.event_id})>"
