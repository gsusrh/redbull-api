"""
Intent Training Dataset - Red Bull Batalla
100 ejemplos naturales por cada intención posible
Incluye typos, acentos mal puestos, español coloquial, variaciones regionales
"""

INTENT_DATASET = {
    "head_to_head": {
        "description": "Comparar dos MCs, quien gana en batalla, historial directo",
        "examples": [
            # Variaciones comunes "vs"
            "Dani vs Chuty",
            "Dani versus Chuty",
            "Dani v.s. Chuty",
            "quien gana entre Dani y Chuty",
            "quien es mejor Dani o Chuty",
            "Dani enfrenta a Chuty",
            "batalla Dani contra Chuty",
            "Dani choca con Chuty",
            "Dani pelea contra Chuty",
            "enfrentamiento Dani Chuty",

            # Typos y acentos incorrectos
            "Dani vs Chuty historico",
            "Dani vs Chuty historico",  # Sin acento
            "Dani v/s Chuty",
            "Dani VS Chuty",
            "Dani Vs Chuty",
            "dani vs chuty",
            "DANI VS CHUTY",
            "Dani  vs  Chuty",  # Espacios extras
            "Dani vs Chuty ?",
            "Dani vs Chuty !!",

            # Variaciones español latino
            "Dani le gana a Chuty",
            "entre Dani y Chuty quien es mejor",
            "si pelearán Dani y Chuty",
            "batalla entre Dani y Chuty",
            "cómo sería Dani contra Chuty",
            "Dani y Chuty quien gana",
            "Dani con Chuty",
            "quien gana Dani o Chuty",
            "quien es más fuerte Dani o Chuty",
            "comparacion Dani Chuty",

            # Variaciones España
            "Dani versus Chuty histórico",
            "historial Dani Chuty",
            "cara a cara Dani Chuty",
            "enfrentamientos Dani Chuty",
            "duelos Dani Chuty",
            "combates Dani Chuty",
            "batallas Dani contra Chuty",
            "qué pasó en Dani vs Chuty",
            "cómo fue Dani vs Chuty",
            "resultado Dani Chuty",

            # Variaciones con más MCs
            "Wos vs Trueno",
            "Chuty vs Dtoke",
            "Reverse vs Arcangel",
            "Yartzi vs Acertijo",
            "Papo vs Black",
            "Aczino vs Red",
            "Skone vs Skill",
            "Sayonara vs Pekeño",
            "Jey M vs Norykko",
            "Replik vs Dani",

            # Frases más naturales
            "me interesa saber Dani versus Chuty",
            "necesito saber el historial de Dani y Chuty",
            "cuál es el récord de Dani contra Chuty",
            "quiero saber quién ganó más Dani o Chuty",
            "cómo es la cabeza a cabeza de Dani y Chuty",
            "comparame Dani con Chuty",
            "dime las batallas entre Dani y Chuty",
            "cuántas veces se enfrentaron Dani y Chuty",
            "Dani le gana a Chuty cuántas veces",
            "Dani está mejor que Chuty",

            # Typos más realistas
            "Dani vss Chuty",
            "Dani vs Chuty",  # Mal escrito pero común
            "dani vs chuty 2023",
            "Dani vs Chuty españa",
            "Dani vs Chuty batalla",
            "Dani vs Chuty quien",
            "Dani vs Chuty resultado",
            "Dani vs Chuty ganador",
            "Dani vs Chuty historial",
            "Dani vs Chuty final",

            # Preguntas variadas
            "¿Dani vs Chuty?",
            "¿quién gana Dani o Chuty?",
            "¿Dani gana a Chuty?",
            "¿y entre Dani y Chuty?",
            "¿cómo es Dani vs Chuty?",
            "¿Dani vs Chuty alguna vez?",
            "¿se enfrentaron Dani y Chuty?",
            "¿quién es mejor Dani o Chuty?",
            "¿récord Dani Chuty?",
            "¿batallas Dani Chuty?",

            # Coloquial
            "dime Dani vs Chuty",
            "Dani contra Chuty pal",
            "ey Dani vs Chuty",
            "Dani vs Chuty boludo",
            "Dani vs Chuty che",
            "che Dani y Chuty",
            "boludo Dani vs Chuty",
            "hermano Dani vs Chuty",
            "carnal Dani vs Chuty",
            "tío Dani vs Chuty",

            # Variaciones con años
            "Dani vs Chuty 2023",
            "Dani vs Chuty 2022",
            "Dani vs Chuty 2021",
            "Dani vs Chuty españa 2023",
            "Dani vs Chuty final españa",
            "Dani vs Chuty cuartos",
            "Dani vs Chuty semifinal",
            "Dani vs Chuty final",
            "Dani vs Chuty clasificatoria",
            "Dani vs Chuty historia",

            # Búsqueda de patrón "X vs Y"
            "Aczino vs Dtoke",
            "Red vs Acertijo",
            "Skone vs Skill",
            "Yartzi vs Black",
            "Reverse vs Jey M",
            "Trueno vs Wos",
            "Klan vs Arcangel",
            "Valenzuela vs Replik",
            "Sayonara vs Pekeño",
            "Norykko vs Chuty",
        ]
    },

    "statistics": {
        "description": "Estadísticas de un MC específico, records, win rate, rachas",
        "examples": [
            # Variaciones "estadísticas"
            "estadísticas de Dani",
            "estadisticas de Dani",  # Sin acento
            "estadistícas de Dani",  # Acento mal puesto
            "estadisticas Dani",
            "stats de Dani",
            "stat Dani",
            "estadisticas Dani 2023",
            "record de Dani",
            "récord de Dani",
            "recordes Dani",  # Plural mal

            # Typos variados
            "Dani estádisticas",
            "Dani estadisticas",
            "Dani estatisticas",  # Error común
            "Dani estadísticas",
            "Dani stats",
            "Dani records",
            "Dani récords",
            "Dani resultados",
            "Dani numeros",
            "Dani números",

            # Preguntas naturales
            "¿cómo le fue a Dani?",
            "¿cómo está Dani en números?",
            "¿cuál es el record de Dani?",
            "¿cuántas batallas ganó Dani?",
            "¿cuál es el win rate de Dani?",
            "¿cuántas victorias tiene Dani?",
            "¿cuántas derrotas tiene Dani?",
            "¿qué racha lleva Dani?",
            "¿cuál es la racha actual de Dani?",
            "¿Dani cuántas gana?",

            # Variaciones en diferentes dialectos
            "dame las estadísticas de Dani",
            "dime los números de Dani",
            "necesito saber las stats de Dani",
            "quiero ver las estadísticas de Dani",
            "muéstrame los records de Dani",
            "cómo va Dani en números",
            "en qué anda Dani estadísticamente",
            "cuál es el desempeño de Dani",
            "cómo anda Dani",
            "qué tal Dani en batalla",

            # Más variaciones con typos
            "estadisticas Dani",
            "estadísticas dani",
            "ESTADÍSTICAS DANI",
            "Estadísticas Dani",
            "estádisticas Dani",
            "estadisticas  Dani",  # Espacio extra
            "estadísticas  de  Dani",  # Espacios extras
            "estadisticas-Dani",
            "estadisticas:Dani",
            "estadisticas/ Dani",

            # Diferentes MCs
            "estadísticas de Chuty",
            "estadísticas de Wos",
            "estadísticas de Trueno",
            "estadísticas de Aczino",
            "estadísticas de Red",
            "estadísticas de Acertijo",
            "estadísticas de Reverse",
            "estadísticas de Arcangel",
            "estadísticas de Skone",
            "estadísticas de Yartzi",

            # Con años específicos
            "estadísticas de Dani 2023",
            "estadísticas de Dani 2022",
            "estadísticas de Dani 2021",
            "Dani stats 2023",
            "Dani record 2023",
            "números de Dani 2023",
            "desempeño Dani 2023",
            "resultados Dani 2023",
            "batallas Dani 2023",
            "victorias Dani 2023",

            # Coloquial
            "ey cuáles son los números de Dani",
            "boludo dame las stats de Dani",
            "che Dani qué números tiene",
            "tío Dani cómo anda en batalla",
            "hermano Dani estadísticas",
            "pal quiero los records de Dani",
            "Dani me pasa las stats",
            "Dani números porfa",
            "Dani cuéntame tus números",
            "Dani cómo te va en batalla",

            # Búsqueda de información general
            "información sobre Dani",
            "info de Dani",
            "datos de Dani",
            "perfil de Dani",
            "biografía de Dani",
            "carrera de Dani",
            "trayectoria de Dani",
            "historial de Dani",
            "desempeño de Dani",
            "performance de Dani",

            # Preguntas específicas
            "¿Dani cuántas batallas ha ganado?",
            "¿Dani en qué anda?",
            "¿cómo está la racha de Dani?",
            "¿Dani en qué ranking está?",
            "¿Dani es el mejor?",
            "¿Dani ganador o perdedor?",
            "¿Dani cuántas ha ganado?",
            "¿Dani cuántas ha perdido?",
            "¿Dani racha ganadora?",
            "¿Dani sigue ganando?",

            # Variantes de "stats"
            "stats Dani",
            "estadísticas Dani",
            "números Dani",
            "records Dani",
            "resultados Dani",
            "palmarés Dani",
            "achievement Dani",
            "logros Dani",
            "métricas Dani",
            "indicadores Dani",
        ]
    },

    "ranking": {
        "description": "Rankings, top performers, mejores MCs, leaderboard",
        "examples": [
            # Variaciones "top"
            "top 10 mejores freestylers",
            "top 10",
            "top10",
            "top 5",
            "top 20",
            "top 30",
            "top mejores",
            "top MCs",
            "top raperos",
            "los top freestylers",

            # Variaciones "ranking"
            "ranking de mejores",
            "ranking general",
            "ranking España",
            "ranking latinoamérica",
            "ranking mundial",
            "ranking 2023",
            "ranking actual",
            "ranking general MCs",
            "ranking freestylers",
            "ranking battle rappers",

            # Typos
            "rankin",
            "rankinng",
            "rankng",
            "rankinn",
            "ranking",
            "rankig",
            "top 10 mejores",
            "top 10 mejor",
            "top10mejores",
            "top 10 mejors",  # Typo español

            # Preguntas variadas
            "¿quiénes son los mejores freestylers?",
            "¿cuál es el top 10 actual?",
            "¿quién es el mejor MC?",
            "¿cuál es el ranking actual?",
            "¿quiénes están en el top?",
            "¿cuál es la mejor alineación?",
            "¿quiénes ganaron más batallas?",
            "¿cuáles son los mejores?",
            "¿quién está primero?",
            "¿cuál es el top en España?",

            # Variaciones dialectales
            "dame el ranking de mejores",
            "dime el top 10 actual",
            "necesito el ranking",
            "quiero ver el ranking",
            "muéstrame los mejores",
            "cuáles son los top",
            "qué tal el ranking",
            "cómo anda el ranking",
            "cuál es el top hoy",
            "dame los mejores",

            # Coloquial
            "ey dame el top 10 boludo",
            "che qué onda el ranking",
            "tío cuál es el top",
            "hermano dame los mejores",
            "pal top 10",
            "Dani en el ranking",
            "Wos en el ranking",
            "ranking con todos",
            "top con Dani",
            "top con Wos",

            # Por país
            "top 10 España",
            "ranking España",
            "mejores de España",
            "top Argentina",
            "ranking Argentina",
            "mejores de Argentina",
            "top México",
            "ranking México",
            "top Colombia",
            "ranking Colombia",

            # Búsquedas específicas
            "quién es número 1",
            "quién es primero en ranking",
            "quién es el mejor del momento",
            "quién lidera el ranking",
            "quién es el más ganador",
            "quién tiene mayor win rate",
            "ranking por ganancias",
            "ranking por victorias",
            "ranking por derrotas",
            "ranking por racha",

            # Variantes
            "leaderboard",
            "tabla de posiciones",
            "posiciones actuales",
            "clasificación general",
            "clasificación actual",
            "standings",
            "chart",
            "tabla de rankings",
            "podio",
            "campeón",

            # Preguntas más naturales
            "¿cómo está el ranking en estos días?",
            "¿quién ocupa el número 1?",
            "¿quién está ganando más últimamente?",
            "¿cuál es la alineación de mejores MCs?",
            "¿cuál es el podio actual?",
            "¿quiénes son los dominantes?",
            "¿cuál es el top en este momento?",
            "¿cuáles son los más fuertes ahora?",
            "¿quiénes están en forma?",
            "¿quiénes ganan más batallas?",

            # Búsquedas amplias
            "dame un ranking",
            "necesito ranking",
            "quiero saber el ranking",
            "cuéntame el ranking",
            "cómo está el ranking",
            "qué dicen del ranking",
            "ranking de verdad",
            "ranking confiable",
            "ranking reciente",
            "ranking actualizado",
        ]
    },

    "event_details": {
        "description": "Información sobre eventos específicos, detalles, participantes, ganadores",
        "examples": [
            # Variaciones "evento"
            "evento Red Bull 2023",
            "evento Red Bull",
            "evento batalla",
            "evento freestyle",
            "evento españa",
            "evento batalla españa",
            "Red Bull evento",
            "batalla evento",
            "competencia Red Bull",
            "torneo Red Bull",

            # Variaciones "batalla"
            "batalla españa 2023",
            "batalla españa",
            "batalla gallos",
            "batalla de gallos",
            "batalla gallos españa",
            "batalla gallos 2023",
            "batalla 2023",
            "batalla 2022",
            "batalla internacional",
            "batalla argentina",

            # Typos comunes
            "batala españa",  # Typo común
            "batalla españa",
            "batlala 2023",
            "batalla 023",  # Números
            "batalla 2o23",
            "batalla dos mil veintitrés",
            "batalla dos veintitres",
            "batalla espana",  # Sin tilde
            "batalla España",
            "batalla ESPAÑA",

            # Preguntas variadas
            "¿cómo fue la batalla de españa 2023?",
            "¿quién ganó la batalla?",
            "¿cuándo fue la batalla?",
            "¿dónde fue la batalla?",
            "¿quiénes participaron?",
            "¿cuál fue el resultado?",
            "¿quién fue el campeón?",
            "¿en qué ciudad fue?",
            "¿cuántos participantes?",
            "¿cómo fue la final?",

            # Búsquedas naturales
            "información de la batalla españa 2023",
            "detalles del evento españa 2023",
            "qué pasó en la batalla españa",
            "resultados batalla españa",
            "participantes batalla españa",
            "ganador batalla españa",
            "final batalla españa",
            "semifinal batalla españa",
            "cuartos batalla españa",
            "fases batalla españa",

            # Diferentes eventos
            "batalla españa",
            "batalla argentina",
            "batalla méxico",
            "batalla colombia",
            "batalla chile",
            "batalla perú",
            "batalla internacional",
            "batalla mundial",
            "batalla regional",
            "batalla local",

            # Coloquial
            "ey cómo fue la batalla boludo",
            "che qué pasó en el evento",
            "tío detalles del evento",
            "hermano quién ganó",
            "pal cuéntame del evento",
            "dime qué pasó",
            "dame los detalles",
            "hazme el resumen",
            "cuéntame todo",
            "qué onda con la batalla",

            # Con años
            "batalla españa 2005",
            "batalla españa 2010",
            "batalla españa 2015",
            "batalla españa 2020",
            "batalla españa 2021",
            "batalla españa 2022",
            "evento 2023",
            "evento 2024",
            "evento reciente",
            "evento pasado",

            # Búsquedas de información específica
            "¿cuál fue el formato de la batalla?",
            "¿cuántas rondas?",
            "¿cuántas fases?",
            "¿cuál fue el lugar?",
            "¿cuál fue la fecha?",
            "¿cuántas personas?",
            "¿quién arbitró?",
            "¿cuál fue el premio?",
            "¿dónde se transmitió?",
            "¿cuál fue la organización?",

            # Variantes
            "Red Bull Batalla españa",
            "Red Bull batalla españa",
            "BATALLA ESPAÑA",
            "batalla españa 2023",
            "Batalla De Los Gallos",
            "batalla de los gallos",
            "gallos españa",
            "gallos 2023",
            "gallos freestyle",
            "gallos batalla",
        ]
    },

    "history": {
        "description": "Historial, línea de tiempo, carrera de un MC, evolución temporal",
        "examples": [
            # Variaciones "historial"
            "historial de Dani",
            "historial Dani",
            "historia de Dani",
            "historia Dani",
            "trayectoria de Dani",
            "trayectoria Dani",
            "carrera de Dani",
            "carrera Dani",
            "evolución de Dani",
            "evolución Dani",

            # Typos
            "historial",
            "histral",
            "histoial",
            "historial",
            "hsitorial",
            "historia",
            "history",
            "trayectoria",
            "trayectória",
            "trayectoria",

            # Preguntas naturales
            "¿cuál es el historial de Dani?",
            "¿cómo fue la carrera de Dani?",
            "¿cómo evolucionó Dani?",
            "¿cuál fue el inicio de Dani?",
            "¿dónde empezó Dani?",
            "¿cuándo empezó Dani?",
            "¿de dónde es Dani?",
            "¿cuál es la historia de Dani?",
            "¿cómo llegó Dani a ser top?",
            "¿cómo fue el viaje de Dani?",

            # Búsquedas temporales
            "Dani desde el inicio",
            "Dani a lo largo del tiempo",
            "Dani línea de tiempo",
            "cronología de Dani",
            "timeline de Dani",
            "trayectoria por años",
            "batallas de Dani año por año",
            "progreso de Dani",
            "crecimiento de Dani",
            "desarrollo de Dani",

            # Coloquial
            "ey dame el historial boludo",
            "che cómo fue Dani desde el comienzo",
            "tío cuéntame la historia de Dani",
            "hermano cómo empezó Dani",
            "pal historial de Dani",
            "dime de dónde viene Dani",
            "cuéntame el viaje de Dani",
            "hazme la historia de Dani",
            "qué pasó con Dani",
            "Dani cómo fuiste",

            # Diferentes MCs
            "historial de Chuty",
            "historial de Wos",
            "historial de Trueno",
            "historial de Aczino",
            "historial de Red",
            "historial de Arcangel",
            "historial de Skone",
            "historial de Acertijo",
            "historial de Yartzi",
            "historial de Black",

            # Con períodos
            "historial de Dani 2020-2023",
            "carrera de Dani 2021-2024",
            "evolución Dani últimos 5 años",
            "cómo fue Dani en 2020",
            "Dani 2015 vs Dani 2023",
            "Dani principios vs fin de carrera",
            "Dani antes vs después",
            "Dani en los 2010s",
            "Dani en los 2020s",
            "Dani en la actualidad",

            # Variantes de búsqueda
            "dime sobre Dani",
            "cuéntame de Dani",
            "información sobre Dani",
            "datos sobre Dani",
            "perfil de Dani",
            "biografía de Dani",
            "quién es Dani",
            "orígenes de Dani",
            "raíces de Dani",
            "legado de Dani",

            # Preguntas más específicas
            "¿Dani dónde nació?",
            "¿Dani cuándo empezó?",
            "¿Dani cómo es?",
            "¿Dani ha ganado?",
            "¿Dani es campeón?",
            "¿Dani fue el mejor?",
            "¿Dani sigue activo?",
            "¿Dani se retiró?",
            "¿Dani aún participa?",
            "¿Dani qué hace ahora?",
        ]
    },

    "style_analysis": {
        "description": "Análisis de estilo, flow, técnica, características de un MC",
        "examples": [
            # Variaciones "estilo"
            "estilo de Dani",
            "estilo Dani",
            "flow de Dani",
            "flow Dani",
            "técnica de Dani",
            "técnica Dani",
            "como fluye Dani",
            "cómo fluye Dani",
            "estilo de freestyle",
            "técnica freestyle",

            # Typos
            "estilo",
            "estilo",
            "estilos",
            "flow",
            "flou",
            "flu",
            "tecnica",
            "técnica",
            "tehnica",
            "teknica",

            # Preguntas variadas
            "¿cuál es el estilo de Dani?",
            "¿cómo fluye Dani?",
            "¿cuál es la técnica de Dani?",
            "¿cuál es la fortaleza de Dani?",
            "¿en qué destaca Dani?",
            "¿cuál es el punto fuerte de Dani?",
            "¿Dani es punchline o flow?",
            "¿Dani es agresivo o técnico?",
            "¿Dani es rápido o lento?",
            "¿Dani es melódico o duro?",

            # Búsquedas de características
            "características de Dani",
            "fortalezas de Dani",
            "habilidades de Dani",
            "cualidades de Dani",
            "puntos fuertes de Dani",
            "puntos débiles de Dani",
            "debilidades de Dani",
            "versatilidad de Dani",
            "versatilidad en batalla",
            "capacidad técnica",

            # Coloquial
            "ey cómo fluye Dani boludo",
            "che el estilo de Dani",
            "tío la técnica de Dani",
            "hermano Dani es punchline o qué",
            "pal cómo es Dani en batalla",
            "dime cómo fluye",
            "cuéntame sus moves",
            "qué tiene de especial",
            "en qué es bueno",
            "cuál es lo suyo",

            # Análisis comparativo
            "estilo Dani vs Chuty",
            "flow Dani comparado con Wos",
            "técnica Dani vs Aczino",
            "estilo de Dani similar a quién",
            "Dani comparado con otros",
            "¿a quién se parece Dani?",
            "Dani tiene estilo de",
            "Dani fluye como",
            "Dani batalla como",
            "Dani es parecido a",

            # Categorías de estilo
            "¿Dani es punchline?",
            "¿Dani es flow?",
            "¿Dani es trap?",
            "¿Dani es wordplay?",
            "¿Dani es storytelling?",
            "¿Dani es agresivo?",
            "¿Dani es técnico?",
            "¿Dani es melódico?",
            "¿Dani es rápido?",
            "¿Dani es lento?",

            # Variantes
            "análisis Dani",
            "análisis de batalla Dani",
            "por qué gana Dani",
            "cómo batalla Dani",
            "dinámica de Dani",
            "estrategia de Dani",
            "táctica de Dani",
            "movimiento de Dani",
            "presencia de Dani",
            "versatilidad de Dani",
        ]
    },

    "battle_details": {
        "description": "Detalles de una batalla específica, rondas, desempeño, análisis",
        "examples": [
            # Variaciones "batalla"
            "batalla Dani vs Chuty",
            "batalla Dani Chuty",
            "batalla entre Dani y Chuty",
            "batalla españa 2023 final",
            "batalla españa 2023 semifinal",
            "batalla españa 2023 cuartos",
            "battle Dani Chuty",
            "confrontación Dani Chuty",
            "enfrentamiento Dani Chuty",
            "pelea Dani Chuty",

            # Typos
            "batala Dani Chuty",
            "batla Dani",
            "batlaa Dani",
            "batal Dani",
            "batalla",
            "batles",
            "batalas",
            "batallatoria",
            "batallita",
            "batayon",

            # Preguntas variadas
            "¿cómo fue la batalla de Dani?",
            "¿cómo Dani en la final?",
            "¿qué pasó en la batalla?",
            "¿quién ganó?",
            "¿cómo perdió Dani?",
            "¿cómo ganó Dani?",
            "¿cuál fue el score?",
            "¿cuál fue el marcador?",
            "¿cómo fue ronda por ronda?",
            "¿qué dijo la audiencia?",

            # Búsquedas de análisis
            "análisis batalla Dani Chuty",
            "detalles batalla Dani Chuty",
            "resumen batalla Dani Chuty",
            "puntuación batalla Dani Chuty",
            "evaluación batalla",
            "crítica batalla",
            "opinión batalla",
            "reacción batalla",
            "comentario batalla",
            "flashback batalla",

            # Coloquial
            "ey cómo fue esa batalla boludo",
            "che qué pasó en el ring",
            "tío dame los detalles",
            "hermano cómo batalla Dani",
            "pal cuéntame la batalla",
            "dime ronda por ronda",
            "qué pasó en cada ronda",
            "quién ganó cada ronda",
            "quién fue mejor",
            "cómo fue la final",

            # Búsquedas de momentos específicos
            "batalla españa 2023 final Dani",
            "batalla españa 2023 semifinal Dani",
            "batalla españa 2023 cuartos Dani",
            "batalla españa 2023 clasificatoria",
            "batalla españa 2023 primera ronda",
            "batalla españa 2023 segunda ronda",
            "batalla españa 2023 tercera ronda",
            "batalla españa 2023 fase de grupos",
            "batalla españa 2023 llaves",
            "batalla españa 2023 bracket",

            # Análisis de desempeño
            "¿Dani cómo batalló?",
            "¿Dani dominó?",
            "¿Dani se defendió?",
            "¿Dani fue dominado?",
            "¿Dani fue favorito?",
            "¿Dani fue sorpresa?",
            "¿Dani fue consistente?",
            "¿Dani fue irregular?",
            "¿Dani fue superior?",
            "¿Dani fue inferior?",

            # Variantes
            "performance Dani en batalla",
            "desempeño Dani",
            "comportamiento Dani",
            "actitud Dani",
            "estrategia en batalla",
            "táctica en batalla",
            "movimientos en batalla",
            "puntos ganados",
            "rondas ganadas",
            "momentos clave",
        ]
    },

    "battle_search": {
        "description": "Buscar batallas por criterios (MC, evento, país, año, etc)",
        "examples": [
            # Variaciones "batallas de"
            "batallas de Dani",
            "batallas Dani",
            "batallas con Dani",
            "batallas participó Dani",
            "batallas en que participó Dani",
            "todas las batallas de Dani",
            "lista de batallas Dani",
            "batallas 2023 de Dani",
            "batallas españa de Dani",
            "batallas internacionales de Dani",

            # Typos
            "batalas de Dani",
            "batlas Dani",
            "batlaa Dani",
            "batalas",
            "battallas",
            "batallas",
            "batailes",
            "batalles",
            "batalas de Dani",
            "batals Dani",

            # Preguntas variadas
            "¿cuántas batallas ha hecho Dani?",
            "¿cuáles son las batallas de Dani?",
            "¿dónde batalló Dani en 2023?",
            "¿batallas de Dani en españa?",
            "¿batallas de Dani en argentina?",
            "¿batallas recientes de Dani?",
            "¿batallas antiguas de Dani?",
            "¿batallas importantes de Dani?",
            "¿batallas famosas de Dani?",
            "¿todas las batallas de Dani?",

            # Búsquedas por evento
            "batallas españa 2023",
            "batallas españa 2022",
            "batallas españa 2021",
            "batallas españa",
            "batallas argentina",
            "batallas méxico",
            "batallas internacionales",
            "batallas nacionales",
            "batallas clasificatoria",
            "batallas finales",

            # Búsquedas por período
            "batallas últimas 5 años",
            "batallas últimos 3 años",
            "batallas últimas 10 batallas",
            "batallas más recientes",
            "batallas más antiguas",
            "batallas de 2020",
            "batallas de 2019",
            "batallas antes de 2020",
            "batallas después de 2020",
            "batallas en 2023",

            # Coloquial
            "ey cuáles fueron las batallas boludo",
            "che dime de las batallas",
            "tío lista de batallas",
            "hermano todas las batallas",
            "pal batallas de Dani",
            "dame el listado",
            "cuéntame cuáles batalló",
            "dónde batalló",
            "con quién batalló",
            "en qué año batalló",

            # Variantes
            "búsqueda de batallas",
            "filtro de batallas",
            "búsqueda batallas Dani",
            "mostrar batallas Dani",
            "listar batallas",
            "catálogo de batallas",
            "archivo de batallas",
            "base de datos batallas",
            "batallas registradas",
            "batallas documentadas",
        ]
    },

    "mc_search": {
        "description": "Buscar, identificar, conocer información de un MC específico",
        "examples": [
            # Variaciones "quién es"
            "¿quién es Dani?",
            "quién es Dani",
            "quién es Dani freestyle",
            "quién es Dani batalla",
            "quién es Dani Red Bull",
            "¿quién es el MC Dani?",
            "¿quién es Dani el rapero?",
            "info de Dani",
            "información de Dani",
            "datos de Dani",

            # Typos
            "quien es Dani",  # Sin acento
            "q es Dani",
            "quién Dani",
            "cuién es Dani",  # Error común
            "quien es Dani?",
            "quién es Dani",
            "quiénes son",
            "quien soi",
            "quién es",
            "quiénes es",

            # Preguntas variadas
            "¿de dónde es Dani?",
            "¿dónde nació Dani?",
            "¿de qué país es Dani?",
            "¿cómo es Dani en persona?",
            "¿cuál es el verdadero nombre de Dani?",
            "¿Dani es colombiano?",
            "¿Dani es argentino?",
            "¿Dani es español?",
            "¿Dani es mexicano?",
            "¿cuál es la edad de Dani?",

            # Búsquedas de identificación
            "búsqueda de Dani",
            "buscar Dani",
            "encontrar Dani",
            "Dani freestyler",
            "Dani rapero",
            "Dani batalla",
            "Dani MC",
            "Dani artista",
            "Dani competidor",
            "Dani participante",

            # Coloquial
            "ey quién es Dani boludo",
            "che dime de Dani",
            "tío quién es Dani",
            "hermano cuéntame sobre Dani",
            "pal quién sería Dani",
            "dame info sobre Dani",
            "cuéntame de Dani",
            "hazme un perfil de Dani",
            "Dani quién eres",
            "Dani de dónde",

            # Diferentes MCs
            "quién es Chuty",
            "quién es Wos",
            "quién es Trueno",
            "quién es Aczino",
            "quién es Red",
            "quién es Arcangel",
            "quién es Skone",
            "quién es Acertijo",
            "quién es Yartzi",
            "quién es Black",

            # Variantes de búsqueda
            "perfil de Dani",
            "biografía de Dani",
            "sobre Dani",
            "presentación Dani",
            "introducción Dani",
            "quién sería Dani",
            "cómo es Dani",
            "cuéntame Dani",
            "Dani qué tal",
            "Dani cuéntate",

            # Con aclaraciones
            "Dani freestyle",
            "Dani Red Bull",
            "Dani batalla gallos",
            "Dani España",
            "Dani competidor",
            "Dani freestyler español",
            "Dani MC batalla",
            "Dani participante Red Bull",
            "Dani rapero freestyle",
            "Dani artista hip hop",
        ]
    },

    "country_analysis": {
        "description": "Análisis por país, MCs de un país, ranking por país",
        "examples": [
            # Variaciones "MCs de"
            "MCs de España",
            "MCs España",
            "freestylers España",
            "raperos España",
            "mejores de España",
            "top España",
            "ranking España",
            "MCs españoles",
            "competidores España",
            "participantes España",

            # Typos
            "MCs de españa",
            "mcs españa",
            "MCsEspaña",
            "MCs Espana",  # Sin tilde
            "MCs España",
            "MCs españa",
            "ESPAÑA",
            "españa",
            "Espana",
            "españa.",

            # Preguntas variadas
            "¿quiénes son los MCs de España?",
            "¿cuáles son los mejores de España?",
            "¿quién es el mejor de España?",
            "¿hay buenos MCs en España?",
            "¿cómo está el nivel en España?",
            "¿quién es el número 1 en España?",
            "¿España tiene buenos freestylers?",
            "¿cuál es el ranking de España?",
            "¿cómo anda España en el ranking?",
            "¿España es competitivo?",

            # Por países específicos
            "MCs de Argentina",
            "MCs de México",
            "MCs de Colombia",
            "MCs de Chile",
            "MCs de Perú",
            "MCs de Brasil",
            "MCs de Estados Unidos",
            "MCs de Francia",
            "MCs de Italia",
            "MCs de Portugal",

            # Búsquedas de análisis
            "análisis España",
            "análisis Argentina",
            "análisis México",
            "escena España",
            "escena Argentina",
            "escena México",
            "nivel España",
            "nivel Argentina",
            "competitividad España",
            "competitividad Argentina",

            # Coloquial
            "ey quiénes son los buenos de España boludo",
            "che MCs de Argentina",
            "tío mejores de España",
            "hermano quién es el top de España",
            "pal ranking de España",
            "dame los mejores de España",
            "cuéntame de España",
            "cómo está España en ranking",
            "España cómo anda",
            "España qué nivel tiene",

            # Búsquedas de comparación
            "España vs Argentina",
            "España vs México",
            "Argentina vs Colombia",
            "México vs Chile",
            "quién tiene mejor nivel",
            "quién es más competitivo",
            "cuál país tiene mejores MCs",
            "cuál país es dominante",
            "ranking por país",
            "países en ranking",

            # Variantes
            "competidores por país",
            "MCs por país",
            "distribución geográfica",
            "participación por país",
            "representantes España",
            "representantes Argentina",
            "alianza España",
            "equipo España",
            "delegación España",
            "región España",
        ]
    },

    "year_statistics": {
        "description": "Estadísticas por año, tendencias anuales, comparativas entre años",
        "examples": [
            # Variaciones "año"
            "estadísticas 2023",
            "estadísticas 2022",
            "estadísticas 2021",
            "stats 2023",
            "números 2023",
            "batallas 2023",
            "evento 2023",
            "año 2023",
            "durante 2023",
            "en 2023",

            # Typos
            "estadisticas 2023",  # Sin acento
            "estadísticas dos mil veintitrés",
            "estadísticas veinte veintitrés",
            "stats 2o23",
            "numeros 2023",
            "números 2023",
            "año dos mil veintitrés",
            "año 2o23",
            "2023",
            "2023",

            # Preguntas variadas
            "¿qué pasó en 2023?",
            "¿cómo fue 2023?",
            "¿quién ganó más en 2023?",
            "¿cuántas batallas en 2023?",
            "¿cuántos eventos en 2023?",
            "¿cuál fue el evento del año 2023?",
            "¿quien fue el mejor de 2023?",
            "¿cómo fue el año 2023?",
            "¿qué año fue mejor?",
            "¿2023 vs 2022?",

            # Búsquedas de tendencias
            "tendencias 2023",
            "cambios 2023",
            "evolución 2023",
            "resumen 2023",
            "repaso 2023",
            "balance 2023",
            "análisis 2023",
            "retrospectiva 2023",
            "yearbook 2023",
            "anuario 2023",

            # Coloquial
            "ey qué pasó en 2023 boludo",
            "che cómo fue ese año",
            "tío mejores del 2023",
            "hermano ganador de 2023",
            "pal 2023 cómo fue",
            "dime 2023 qué pasó",
            "cuéntame del 2023",
            "2023 fue épico",
            "qué onda con 2023",
            "2023 bueno malo",

            # Comparativas entre años
            "2023 vs 2022",
            "2022 vs 2021",
            "2021 vs 2020",
            "2020 vs 2019",
            "2023 mejor que 2022",
            "2022 mejor que 2021",
            "cuál año fue mejor",
            "cuál año fue peor",
            "comparación años",
            "evolución años",

            # Búsquedas específicas
            "ganador 2023",
            "ganador 2022",
            "ganador 2021",
            "batalla del año 2023",
            "evento más importante 2023",
            "highlights 2023",
            "momentos 2023",
            "récords 2023",
            "sorpresas 2023",
            "decepciones 2023",
        ]
    },

    "tournament_info": {
        "description": "Información de torneos específicos, estructura, fases, bracket",
        "examples": [
            # Variaciones "torneo"
            "torneo Red Bull",
            "torneo freestyle",
            "torneo batalla",
            "torneo españa",
            "torneo 2023",
            "torneo clasificatorio",
            "torneo internacional",
            "torneo nacional",
            "torneos de batalla",
            "campeonato",

            # Typos
            "torneio",
            "tornei",
            "torneo",
            "tornei",
            "torneoo",
            "torneoe",
            "tornio",
            "tornoe",
            "tornaento",
            "tornemaento",

            # Preguntas variadas
            "¿cómo es el torneo?",
            "¿cuál es la estructura?",
            "¿cuántas fases?",
            "¿cuántos participantes?",
            "¿qué sistema de puntuación?",
            "¿cómo se califica?",
            "¿qué es lo que pasa?",
            "¿cuál es el formato?",
            "¿cómo funciona el torneo?",
            "¿cuál es el reglamento?",

            # Búsquedas de información
            "información torneo",
            "detalles torneo",
            "reglamento torneo",
            "estructura torneo",
            "fases torneo",
            "brackets torneo",
            "participantes torneo",
            "formato torneo",
            "sistema torneo",
            "premiación torneo",

            # Coloquial
            "ey cómo funciona el torneo boludo",
            "che explícame el torneo",
            "tío detalles del torneo",
            "hermano cómo es la estructura",
            "pal dame el reglamento",
            "dime cómo es",
            "cuéntame cómo funciona",
            "explícame el sistema",
            "hazme un resumen",
            "qué onda con el torneo",

            # Búsquedas de fases
            "fase de grupos",
            "clasificatorias",
            "cuartos de final",
            "semifinal",
            "final",
            "tercera posición",
            "repechaje",
            "llave 1",
            "llave 2",
            "bracket completo",

            # Variantes
            "campeonato Red Bull",
            "competencia Red Bull",
            "evento principal",
            "evento clasificatorio",
            "play-in",
            "grupo",
            "llave",
            "confrontación",
            "matchup",
            "emparejamientos",
        ]
    },

    "general_search": {
        "description": "Búsquedas generales, preguntas abiertas, información diversa",
        "examples": [
            # Preguntas generales
            "¿qué es Red Bull Batalla?",
            "¿qué es una batalla de gallos?",
            "¿cómo funciona freestyle?",
            "¿qué es freestyle?",
            "¿cómo se puntúa?",
            "¿cuáles son las reglas?",
            "¿cómo empezó Red Bull?",
            "¿de dónde viene la batalla?",
            "¿dónde puedo ver batallas?",
            "¿cómo puedo participar?",

            # Búsquedas simples
            "Red Bull",
            "batalla",
            "freestyle",
            "batalla de gallos",
            "batalla de los gallos",
            "rap freestyle",
            "freestyler",
            "MC",
            "rapper",
            "competencia",

            # Typos variados
            "red bull",
            "redbull",
            "rdbull",
            "batallah",
            "batallaaa",
            "freestyle",
            "frestyle",
            "freesyle",
            "freestyle",
            "freestyyle",

            # Preguntas sobre registro
            "¿cómo me registro?",
            "¿cómo participo?",
            "¿dónde me inscribo?",
            "¿cuál es el proceso?",
            "¿qué debo hacer?",
            "¿qué requisitos?",
            "¿cuándo es la siguiente?",
            "¿dónde es la próxima?",
            "¿cuándo puedo participar?",
            "¿qué tengo que hacer?",

            # Búsquedas de transmisión
            "¿dónde puedo ver?",
            "¿dónde se transmite?",
            "¿en qué canal?",
            "¿cuándo es la transmisión?",
            "¿a qué hora?",
            "¿dónde veo la batalla?",
            "¿cómo veo en vivo?",
            "¿YouTube?",
            "¿Twitch?",
            "¿streaming?",

            # Preguntas sobre reglas
            "¿cuáles son las reglas?",
            "¿qué está permitido?",
            "¿qué no está permitido?",
            "¿cuánto dura?",
            "¿cuántas rondas?",
            "¿cuánto tiempo por ronda?",
            "¿cómo se puntúa?",
            "¿quién juzga?",
            "¿cómo es el juicio?",
            "¿hay árbitro?",

            # Coloquial
            "boludo qué es esto",
            "che qué onda",
            "tío explícame",
            "hermano esto cómo funciona",
            "pal cuéntame del tema",
            "dime de qué va",
            "cuéntame todo",
            "hazme un resumen",
            "qué necesito saber",
            "cómo comienzo",

            # Búsquedas variadas
            "información general",
            "datos Red Bull",
            "curiosidades",
            "hechos",
            "historia",
            "orígenes",
            "evolución",
            "futuro",
            "próximos eventos",
            "cronograma",
        ]
    }
}

# Función helper para obtener todas las intenciones
def get_all_intents():
    """Retorna lista de todas las intenciones disponibles"""
    return list(INTENT_DATASET.keys())

# Función helper para obtener ejemplos de una intención
def get_examples_for_intent(intent: str) -> list:
    """Retorna lista de ejemplos para una intención específica"""
    if intent in INTENT_DATASET:
        return INTENT_DATASET[intent]["examples"]
    return []

# Estadísticas del dataset
def print_dataset_stats():
    """Imprime estadísticas del dataset"""
    print("\n" + "="*70)
    print("ESTADÍSTICAS DEL DATASET DE INTENCIONES")
    print("="*70)

    total_intents = len(INTENT_DATASET)
    total_examples = 0

    for intent, data in INTENT_DATASET.items():
        examples_count = len(data["examples"])
        total_examples += examples_count
        print(f"✓ {intent.upper()}: {examples_count} ejemplos")

    print("\n" + "-"*70)
    print(f"TOTAL: {total_intents} intenciones × ~100 ejemplos cada una")
    print(f"TOTAL DE EJEMPLOS: {total_examples}")
    print(f"PROMEDIO POR INTENCIÓN: {total_examples // total_intents}")
    print("="*70 + "\n")

if __name__ == "__main__":
    print_dataset_stats()
