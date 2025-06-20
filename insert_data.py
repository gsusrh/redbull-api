import pandas as pd
import unidecode
from sqlalchemy import create_engine, text

# Conexión a PostgreSQL
db_url = "postgresql://postgres:HUOMtnXMvadivsKSrzQCmpxOqfTxaZJz@maglev.proxy.rlwy.net:30559/railway"
engine = create_engine(db_url)

# Cargar Excel
file_path = "plantilla_red_bull_batalla.xlsx"
events_df = pd.read_excel(file_path, sheet_name="events")
persons_df = pd.read_excel(file_path, sheet_name="persons")
battles_df = pd.read_excel(file_path, sheet_name="battles")

# Normalizar texto
def normalize_text_data(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.lower().apply(unidecode.unidecode)
    return df

events_df = normalize_text_data(events_df)
persons_df = normalize_text_data(persons_df)
battles_df = normalize_text_data(battles_df)

# Crear tablas con relaciones
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS battle_participants CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS battles CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS persons CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS events CASCADE"))

    conn.execute(text("""
        CREATE TABLE events (
            evento_id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            country TEXT,
            city TEXT,
            place TEXT,
            date DATE
        );
    """))

    conn.execute(text("""
        CREATE TABLE persons (
            person_id INTEGER PRIMARY KEY,
            aka TEXT NOT NULL,
            full_name TEXT,
            country TEXT,
            active BOOLEAN
        );
    """))

    conn.execute(text("""
        CREATE TABLE battles (
            battle_id INTEGER PRIMARY KEY,
            evento_id INTEGER REFERENCES events(evento_id),
            name TEXT,
            phase TEXT
        );
    """))

    conn.execute(text("""
        CREATE TABLE battle_participants (
            battle_id INTEGER REFERENCES battles(battle_id),
            person_id INTEGER REFERENCES persons(person_id),
            position INTEGER,          -- 1 o 2
            is_winner BOOLEAN,         -- TRUE si ganó
            PRIMARY KEY (battle_id, person_id)
        );
    """))

# Insertar eventos y personas
events_df.to_sql("events", engine, if_exists="append", index=False)
persons_df.to_sql("persons", engine, if_exists="append", index=False)

# Insertar batallas (sin los campos person_1_id, person_2_id, winner_id)
battles_core_df = battles_df[["battle_id", "evento_id", "name", "phase"]]
battles_core_df.to_sql("battles", engine, if_exists="append", index=False)

# Crear tabla intermedia: battle_participants
participants_data = []

for _, row in battles_df.iterrows():
    battle_id = row["battle_id"]
    for pos in [1, 2]:
        person_id = row[f"person_{pos}_id"]
        is_winner = person_id == row["winner_id"]
        participants_data.append({
            "battle_id": battle_id,
            "person_id": person_id,
            "position": pos,
            "is_winner": is_winner
        })

battle_participants_df = pd.DataFrame(participants_data)
battle_participants_df.to_sql("battle_participants", engine, if_exists="append", index=False)

print("✅ Base de datos reestructurada con tabla intermedia battle_participants y datos cargados correctamente.")
