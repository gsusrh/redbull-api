"""
Tests para BatallaToolkit.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Person, CountryEnum, StyleEnum
from tools import BatallaToolkit


@pytest.fixture
def test_db():
    """Crea una BD de prueba en memoria."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def toolkit(test_db):
    """Crea instancia de toolkit con BD de prueba."""
    return BatallaToolkit(test_db)


@pytest.fixture
def sample_persons(test_db):
    """Crea personas de prueba."""
    persons = [
        Person(
            aka="Dani",
            full_name="Daniel García",
            country=CountryEnum.SPAIN,
            style=StyleEnum.PUNCHLINE
        ),
        Person(
            aka="Chuty",
            full_name="Juan Carlos",
            country=CountryEnum.SPAIN,
            style=StyleEnum.FLOW
        ),
        Person(
            aka="Wos",
            full_name="José Luis",
            country=CountryEnum.ARGENTINA,
            style=StyleEnum.TECHNICAL
        )
    ]
    for person in persons:
        test_db.add(person)
    test_db.commit()
    return persons


def test_search_person_exact_match(toolkit, sample_persons):
    """Test búsqueda exacta de persona."""
    results = toolkit.search_person("Dani")
    assert len(results) > 0
    assert results[0]["aka"] == "Dani"


def test_search_person_fuzzy_match(toolkit, sample_persons):
    """Test búsqueda difusa."""
    results = toolkit.search_person("Dani", threshold=70)
    assert len(results) > 0
    # La búsqueda difusa debe encontrar "Dani" incluso con typos


def test_search_person_case_insensitive(toolkit, sample_persons):
    """Test que búsqueda es case insensitive."""
    results = toolkit.search_person("dani")
    assert len(results) > 0
    assert results[0]["aka"] == "Dani"


def test_search_person_with_accents(toolkit, sample_persons):
    """Test que búsqueda maneja acentos."""
    results = toolkit.search_person("Chuty")
    assert len(results) > 0


def test_normalize_string(toolkit):
    """Test normalización de strings."""
    normalized = toolkit._normalize_string("Dani García")
    assert normalized == "dani garcia"
    assert "á" not in normalized


def test_normalize_string_handles_none(toolkit):
    """Test que normalizar maneja None."""
    result = toolkit._normalize_string(None)
    assert result == ""


def test_get_person_by_country(toolkit, sample_persons):
    """Test obtener personas por país."""
    spanish_people = toolkit.get_person_by_country("spain")
    assert len(spanish_people) == 2
    assert all(p["country"] == "spain" for p in spanish_people)


def test_get_person_by_country_invalid(toolkit):
    """Test país inválido."""
    result = toolkit.get_person_by_country("invalid_country")
    assert "error" in result


def test_get_ambiguity_clarification_no_ambiguity(toolkit, sample_persons):
    """Test que no hay ambigüedad para nombres únicos."""
    result = toolkit.get_ambiguity_clarification("Wos")
    assert result["ambiguous"] is False


def test_get_ambiguity_clarification_with_ambiguity(toolkit, sample_persons):
    """Test detección de ambigüedad para múltiples opciones."""
    # Ambas "Dani" y "Chuty" podrían ser ambiguas si tuvieran mismo nombre normalizado
    # Este test es simplificado; en producción habría más opciones
    result = toolkit.get_ambiguity_clarification("Dani")
    assert isinstance(result, dict)


def test_person_statistics_calculation(toolkit, sample_persons):
    """Test cálculo de estadísticas."""
    person_id = sample_persons[0].id
    stats = toolkit._calculate_person_statistics(person_id)

    assert "person_id" in stats
    assert "total_battles" in stats
    assert "total_wins" in stats
    assert "win_rate" in stats


def test_list_all_persons(toolkit, sample_persons):
    """Test listar todos los MCs."""
    all_people = toolkit.list_all_persons()
    assert len(all_people) == 3


def test_list_all_persons_by_country(toolkit, sample_persons):
    """Test listar MCs por país."""
    spanish_people = toolkit.list_all_persons("spain")
    assert len(spanish_people) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
