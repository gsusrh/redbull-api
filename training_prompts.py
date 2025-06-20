from langchain_core.messages import HumanMessage, AIMessage

few_shot_examples = [

    # 1. Listar todos los eventos
    HumanMessage(content='User Query: "Muestrame todos los eventos de Red Bull"\nPreprocessed Entities: None'),
    AIMessage(content='SELECT name, type, country, city, place, date FROM events;'),

    # 2. Eventos por país
    HumanMessage(content='User Query: "Qué eventos hubo en Argentina?"\nPreprocessed Entities: {"country": "argentina"}'),
    AIMessage(content='SELECT name, type, city, place, date FROM events WHERE country = \'argentina\';'),

    # 3. Eventos por ciudad
    HumanMessage(content='User Query: "Eventos en Lima"\nPreprocessed Entities: {"city": "lima"}'),
    AIMessage(content='SELECT name, type, country, place, date FROM events WHERE city = \'lima\';'),

    # 4. Eventos por lugar
    HumanMessage(content='User Query: "Eventos en el Palacio de los Deportes"\nPreprocessed Entities: {"event_place": "palacio de los deportes"}'),
    AIMessage(content='SELECT name, type, country, city, date FROM events WHERE place = \'palacio de los deportes\';'),

    # 5. Eventos de un año específico
    HumanMessage(content='User Query: "Qué eventos se hicieron en 2022?"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT name, type, country, city, place, date FROM events WHERE date LIKE '2022%';"),

    # 6. Eventos entre dos fechas
    HumanMessage(content='User Query: "Eventos entre 2021 y 2023"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT name, type, country, city, place, date FROM events WHERE date BETWEEN '2021-01-01' AND '2023-12-31';"),

    # 7. Eventos internacionales
    HumanMessage(content='User Query: "Eventos internacionales de Red Bull"\nPreprocessed Entities: {"type": "internacional"}'),
    AIMessage(content="SELECT name, country, city, place, date FROM events WHERE type = 'internacional';"),

    # 8. Eventos nacionales
    HumanMessage(content='User Query: "Eventos nacionales"\nPreprocessed Entities: {"type": "nacional"}'),
    AIMessage(content="SELECT name, country, city, place, date FROM events WHERE type = 'nacional';"),

    # 9. Detalles de un evento específico
    HumanMessage(content='User Query: "Detalles de la final nacional chile 2021"\nPreprocessed Entities: {"event_name": "final nacional chile 2021"}'),
    AIMessage(content="SELECT name, type, country, city, place, date FROM events WHERE name = 'final nacional chile 2021';"),

    # 10. Fechas de eventos en México
    HumanMessage(content='User Query: "Cuándo fueron los eventos en México?"\nPreprocessed Entities: {"country": "mexico"}'),
    AIMessage(content="SELECT name, date FROM events WHERE country = 'mexico';"),

    # 11. Lugares donde se hizo Red Bull en Perú
    HumanMessage(content='User Query: "Dónde se hizo Red Bull en Perú?"\nPreprocessed Entities: {"country": "peru"}'),
    AIMessage(content="SELECT DISTINCT place FROM events WHERE country = 'peru';"),

    # 12. Cuántos eventos hubo por país
    HumanMessage(content='User Query: "Cuántos eventos hubo por país?"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT country, COUNT(*) AS total_eventos FROM events GROUP BY country ORDER BY total_eventos DESC;"),

    # 13. Último evento realizado
    HumanMessage(content='User Query: "Cuál fue el último evento?"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT name, date FROM events ORDER BY date DESC LIMIT 1;"),

    # 14. Primer evento registrado
    HumanMessage(content='User Query: "Cuál fue el primer evento?"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT name, date FROM events ORDER BY date ASC LIMIT 1;"),

    # 15. ¿Cuántos eventos se han hecho en total?
    HumanMessage(content='User Query: "Cuántos eventos se han hecho?"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT COUNT(*) FROM events;"),

    # 16. Eventos en 2023 en España
    HumanMessage(content='User Query: "Eventos en España en 2023"\nPreprocessed Entities: {"country": "españa"}'),
    AIMessage(content="SELECT name, type, city, place, date FROM events WHERE country = 'españa' AND date LIKE '2023%';"),

    # 17. Eventos internacionales en México
    HumanMessage(content='User Query: "Eventos internacionales en México"\nPreprocessed Entities: {"country": "mexico", "type": "internacional"}'),
    AIMessage(content="SELECT name, city, place, date FROM events WHERE country = 'mexico' AND type = 'internacional';"),

    # 18. ¿Qué tipo de eventos se realizan?
    HumanMessage(content='User Query: "Qué tipos de eventos hay?"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT DISTINCT type FROM events;"),

    # 19. ¿En qué ciudades se ha hecho Red Bull?
    HumanMessage(content='User Query: "En qué ciudades se ha hecho Red Bull?"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT DISTINCT city FROM events;"),

    # 20. ¿En qué lugares se ha repetido evento más de una vez?
    HumanMessage(content='User Query: "Qué lugares han tenido más de un evento?"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT place, COUNT(*) as cantidad FROM events GROUP BY place HAVING COUNT(*) > 1 ORDER BY cantidad DESC;"),

    
    
    
    
    # 1. Listar todos los eventos
    HumanMessage(content='User Query: "Muestrame todos los eventos de Red Bull"\nPreprocessed Entities: None'),
    AIMessage(content="SELECT name, type, country, city, place, date FROM events;"),

    # 2. Listar raperos activos de España
    HumanMessage(content='User Query: "Dame todos los MCs activos de españa"\nPreprocessed Entities: {"country": "españa", "active": true}'),
    AIMessage(content="SELECT aka, full_name FROM persons WHERE country = 'españa' AND active = TRUE;"),

    # 3. Eventos internacionales en 2023
    HumanMessage(content='User Query: "Eventos internacionales en 2023"\nPreprocessed Entities: {"event_type": "internacional", "year": "2023"}'),
    AIMessage(content="""
        SELECT name, country, city, place, date
        FROM events
        WHERE type = 'internacional' AND EXTRACT(YEAR FROM date) = 2023;
    """.strip()),

    # 4. Batallas semifinales en eventos nacionales
    HumanMessage(content='User Query: "Listar batallas semifinales en eventos nacionales"\nPreprocessed Entities: {"event_type": "nacional", "phase": "semifinal"}'),
    AIMessage(content="""
        SELECT b.name, e.name AS event_name, b.phase
        FROM battles b
        JOIN events e ON b.evento_id = e.evento_id
        WHERE e.type = 'nacional' AND b.phase = 'semifinal';
    """.strip()),

    # 5. Raperos venezolanos que han ganado una internacional (CORRECTO)
    HumanMessage(content='User Query: "Cuáles raperos venezolanos han ganado una internacional?"\nPreprocessed Entities: {"country": "venezuela", "event_type": "internacional", "phase": "final"}'),
    AIMessage(content="""
        SELECT DISTINCT p.aka
        FROM persons p
        JOIN battles b ON b.winner_id = p.person_id
        JOIN events e ON b.evento_id = e.evento_id
        WHERE p.country = 'venezuela'
          AND e.type = 'internacional'
          AND b.phase = 'final';
    """.strip()),

    # 6. Detalles de una batalla específica
    HumanMessage(content='User Query: "Dime detalles de la batalla final del evento Red Bull Nacional 2022"\nPreprocessed Entities: {"event_name": "red bull nacional 2022", "phase": "final"}'),
    AIMessage(content="""
        SELECT b.name, b.phase, e.name AS event_name, e.date
        FROM battles b
        JOIN events e ON b.evento_id = e.evento_id
        WHERE e.name = 'red bull nacional 2022' AND b.phase = 'final';
    """.strip()),

    # 7. Raperos que participaron en una batalla específica
    HumanMessage(content='User Query: "¿Quiénes participaron en la batalla final del evento internacional?"\nPreprocessed Entities: {"event_type": "internacional", "phase": "final"}'),
    AIMessage(content="""
        SELECT DISTINCT p.aka
        FROM persons p
        JOIN battle_participants bp ON p.person_id = bp.person_id
        JOIN battles b ON bp.battle_id = b.battle_id
        JOIN events e ON b.evento_id = e.evento_id
        WHERE e.type = 'internacional' AND b.phase = 'final';
    """.strip()),

    # 8. Eventos que ocurrieron en Madrid
    HumanMessage(content='User Query: "Eventos en Madrid"\nPreprocessed Entities: {"event_place": "madrid"}'),
    AIMessage(content="SELECT name, type, date FROM events WHERE place = 'madrid';"),

    # 9. Batallas ganadas por un rapero específico
    HumanMessage(content='User Query: "Batallas ganadas por akronimo"\nPreprocessed Entities: {"person_aka": "akronimo"}'),
    AIMessage(content="""
        SELECT b.name, e.name AS event_name, b.phase
        FROM battles b
        JOIN persons p ON p.person_id = b.winner_id
        JOIN events e ON b.evento_id = e.evento_id
        WHERE p.aka = 'akronimo';
    """.strip()),

    # 10. Raperos activos de México
    HumanMessage(content='User Query: "Lista de MCs activos de México"\nPreprocessed Entities: {"country": "mexico", "active": true}'),
    AIMessage(content="SELECT aka, full_name FROM persons WHERE country = 'mexico' AND active = TRUE;"),

    # 11. Raperos que han participado en eventos nacionales en 2021
    HumanMessage(content='User Query: "MCs que participaron en eventos nacionales de 2021"\nPreprocessed Entities: {"event_type": "nacional", "year": "2021"}'),
    AIMessage(content="""
        SELECT DISTINCT p.aka
        FROM persons p
        JOIN battle_participants bp ON p.person_id = bp.person_id
        JOIN battles b ON bp.battle_id = b.battle_id
        JOIN events e ON b.evento_id = e.evento_id
        WHERE e.type = 'nacional' AND EXTRACT(YEAR FROM e.date) = 2021;
    """.strip()),

    # 12. Lista de eventos por ciudad y año
    HumanMessage(content='User Query: "Eventos en Buenos Aires en 2020"\nPreprocessed Entities: {"event_place": "buenos aires", "year": "2020"}'),
    AIMessage(content="""
        SELECT name, type, date
        FROM events
        WHERE place = 'buenos aires' AND EXTRACT(YEAR FROM date) = 2020;
    """.strip()),

    # 13. Participantes de una batalla específica con sus posiciones
    HumanMessage(content='User Query: "Quiénes participaron en la batalla final y en qué posición?"\nPreprocessed Entities: {"phase": "final"}'),
    AIMessage(content="""
        SELECT p.aka, bp.position
        FROM battle_participants bp
        JOIN persons p ON bp.person_id = p.person_id
        JOIN battles b ON bp.battle_id = b.battle_id
        WHERE b.phase = 'final';
    """.strip()),

    # 14. Eventos internacionales realizados en España
    HumanMessage(content='User Query: "Eventos internacionales en España"\nPreprocessed Entities: {"country": "españa", "event_type": "internacional"}'),
    AIMessage(content="""
        SELECT name, city, place, date
        FROM events
        WHERE country = 'españa' AND type = 'internacional';
    """.strip()),

    # 15. Raperos que han participado en la final de un evento nacional
    HumanMessage(content='User Query: "MCs que participaron en la final de eventos nacionales"\nPreprocessed Entities: {"event_type": "nacional", "phase": "final"}'),
    AIMessage(content="""
        SELECT DISTINCT p.aka
        FROM persons p
        JOIN battle_participants bp ON p.person_id = bp.person_id
        JOIN battles b ON bp.battle_id = b.battle_id
        JOIN events e ON b.evento_id = e.evento_id
        WHERE e.type = 'nacional' AND b.phase = 'final';
    """.strip()),

    # 16. Batallas en las que un rapero específico participó y no ganó
    HumanMessage(content='User Query: "Batallas en las que participó ak66 y perdió"\nPreprocessed Entities: {"person_aka": "ak66"}'),
    AIMessage(content="""
        SELECT b.name, e.name AS event_name, b.phase
        FROM battles b
        JOIN battle_participants bp ON b.battle_id = bp.battle_id
        JOIN persons p ON bp.person_id = p.person_id
        JOIN events e ON b.evento_id = e.evento_id
        WHERE p.aka = 'ak66' AND b.winner_id <> p.person_id;
    """.strip()),

    # 17. Eventos realizados en 2022
    HumanMessage(content='User Query: "Eventos en 2022"\nPreprocessed Entities: {"year": "2022"}'),
    AIMessage(content="""
        SELECT name, type, country, city, place, date
        FROM events
        WHERE EXTRACT(YEAR FROM date) = 2022;
    """.strip()),

    # 18. Participantes que ganaron en la fase semifinal de un evento internacional
    HumanMessage(content='User Query: "Ganadores en semifinales internacionales"\nPreprocessed Entities: {"event_type": "internacional", "phase": "semifinal"}'),
    AIMessage(content="""
        SELECT DISTINCT p.aka
        FROM persons p
        JOIN battles b ON b.winner_id = p.person_id
        JOIN events e ON b.evento_id = e.evento_id
        WHERE e.type = 'internacional' AND b.phase = 'semifinal';
    """.strip()),

    # 19. Eventos en los que participó un rapero específico
    HumanMessage(content='User Query: "Eventos donde participó blackcode"\nPreprocessed Entities: {"person_aka": "blackcode"}'),
    AIMessage(content="""
        SELECT DISTINCT e.name, e.type, e.date
        FROM events e
        JOIN battles b ON e.evento_id = b.evento_id
        JOIN battle_participants bp ON b.battle_id = bp.battle_id
        JOIN persons p ON bp.person_id = p.person_id
        WHERE p.aka = 'blackcode';
    """.strip()),

    # 20. Raperos inactivos que participaron en eventos internacionales
    HumanMessage(content='User Query: "MCs inactivos en eventos internacionales"\nPreprocessed Entities: {"active": false, "event_type": "internacional"}'),
    AIMessage(content="""
        SELECT DISTINCT p.aka
        FROM persons p
        JOIN battle_participants bp ON p.person_id = bp.person_id
        JOIN battles b ON bp.battle_id = b.battle_id
        JOIN events e ON b.evento_id = e.evento_id
        WHERE p.active = FALSE AND e.type = 'internacional';
    """.strip()),

]
