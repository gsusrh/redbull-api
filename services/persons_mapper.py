import unidecode # Para remover acentos

# --- MAPAS DE SINÓNIMOS Y VARIACIONES ---
# Asegúrate que los VALORES de este mapa sean las formas canónicas y normalizadas
# que existen en tu base de datos y por tanto en `all_countries`.

def _normalize_for_map_key(s: str) -> str:
    if not isinstance(s, str):
        return ""
    return unidecode.unidecode(s).lower().strip()
    
CANONICAL_PERU = "peru"
CANONICAL_ECUADOR = "ecuador"
CANONICAL_VENEZUELA = "venezuela"
CANONICAL_DOMINICANA = "dominicana"
CANONICAL_CHILE = "chile"
CANONICAL_ARGENTINA = "argentina"
CANONICAL_MEXICO = "mexico"
CANONICAL_COLOMBIA = "colombia"
CANONICAL_USA = "usa"
CANONICAL_BOLIVIA = "bolivia"
CANONICAL_COSTA_RICA = "costa rica"
CANONICAL_SPAIN = "spain" 
CANONICAL_URUGUAY = "uruguay"
CANONICAL_CUBA = "cuba"
CANONICAL_PANAMA = "panama"
CANONICAL_PUERTO_RICO = "puerto rico"
CANONICAL_GUATEMALA = "guatemala"

COUNTRY_VARIATIONS_MAP = {
    # Perú
    _normalize_for_map_key("peru"): CANONICAL_PERU,
    _normalize_for_map_key("perú"): CANONICAL_PERU,
    # Ecuador
    _normalize_for_map_key("ecuador"): CANONICAL_ECUADOR,
    # Venezuela
    _normalize_for_map_key("venezuela"): CANONICAL_VENEZUELA,
    _normalize_for_map_key("vzla"): CANONICAL_VENEZUELA,
    # República Dominicana
    _normalize_for_map_key("dominicana"): CANONICAL_DOMINICANA,
    _normalize_for_map_key("república dominicana"): CANONICAL_DOMINICANA,
    _normalize_for_map_key("republica dominicana"): CANONICAL_DOMINICANA,
    _normalize_for_map_key("r. dominicana"): CANONICAL_DOMINICANA,
    _normalize_for_map_key("rep dominicana"): CANONICAL_DOMINICANA,
    _normalize_for_map_key("rd"): CANONICAL_DOMINICANA,
    # Chile
    _normalize_for_map_key("chile"): CANONICAL_CHILE,
    # Argentina
    _normalize_for_map_key("argentina"): CANONICAL_ARGENTINA,
    _normalize_for_map_key("arg"): CANONICAL_ARGENTINA,
    # México
    _normalize_for_map_key("mexico"): CANONICAL_MEXICO,
    _normalize_for_map_key("méxico"): CANONICAL_MEXICO,
    _normalize_for_map_key("mejico"): CANONICAL_MEXICO, # Misspelling común
    _normalize_for_map_key("méjico"): CANONICAL_MEXICO, # Misspelling común
    # Colombia
    _normalize_for_map_key("colombia"): CANONICAL_COLOMBIA,
    _normalize_for_map_key("col"): CANONICAL_COLOMBIA,
    # USA / Estados Unidos
    _normalize_for_map_key("usa"): CANONICAL_USA,
    _normalize_for_map_key("eeuu"): CANONICAL_USA,
    _normalize_for_map_key("estados unidos"): CANONICAL_USA,
    _normalize_for_map_key("estados unidos de america"): CANONICAL_USA,
    _normalize_for_map_key("united states"): CANONICAL_USA,
    _normalize_for_map_key("america"): CANONICAL_USA, # Ambiguo, pero a veces usado
    # Bolivia
    _normalize_for_map_key("bolivia"): CANONICAL_BOLIVIA,
    # Costa Rica
    _normalize_for_map_key("costa rica"): CANONICAL_COSTA_RICA,
    _normalize_for_map_key("cr"): CANONICAL_COSTA_RICA,
    # España / Spain
    _normalize_for_map_key("españa"): CANONICAL_SPAIN,
    _normalize_for_map_key("espana"): CANONICAL_SPAIN, # unidecode de españa
    _normalize_for_map_key("spain"): CANONICAL_SPAIN,
    _normalize_for_map_key("es"): CANONICAL_SPAIN, # Código ISO, a veces usado
    # Uruguay
    _normalize_for_map_key("uruguay"): CANONICAL_URUGUAY,
    _normalize_for_map_key("uru"): CANONICAL_URUGUAY,
    # Cuba
    _normalize_for_map_key("cuba"): CANONICAL_CUBA,
    # Panamá
    _normalize_for_map_key("panama"): CANONICAL_PANAMA,
    _normalize_for_map_key("panamá"): CANONICAL_PANAMA,
    # Puerto Rico
    _normalize_for_map_key("puerto rico"): CANONICAL_PUERTO_RICO,
    _normalize_for_map_key("pr"): CANONICAL_PUERTO_RICO,
    # Guatemala
    _normalize_for_map_key("guatemala"): CANONICAL_GUATEMALA,
    _normalize_for_map_key("guate"): CANONICAL_GUATEMALA,

    # --- Variantes comunes adicionales y posibles errores de tipeo (ejemplos) ---
    # (Estas son más para el fuzzy matching si el mapa no los cubre,
    #  pero algunas pueden ser explícitas si son muy comunes)

    # Errores de tipeo para México
    _normalize_for_map_key("mexco"): CANONICAL_MEXICO,
    _normalize_for_map_key("mxico"): CANONICAL_MEXICO,

    # Errores de tipeo para Colombia
    _normalize_for_map_key("colobia"): CANONICAL_COLOMBIA,
    _normalize_for_map_key("colomia"): CANONICAL_COLOMBIA,

    # Errores de tipeo para Argentina
    _normalize_for_map_key("argetina"): CANONICAL_ARGENTINA,
    _normalize_for_map_key("argentna"): CANONICAL_ARGENTINA,
    
    # ... y así sucesivamente para otros países y errores comunes que observes.
}