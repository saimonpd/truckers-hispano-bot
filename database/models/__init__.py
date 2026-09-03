from database.models.company import TABLE_SCHEMA as COMPANY_TABLE
from database.models.event import TABLE_SCHEMA as EVENT_TABLE
from database.models.event_participant import TABLE_SCHEMA as EVENT_PARTICIPANT_TABLE
from database.models.suggestion import TABLE_SCHEMA as SUGGESTION_TABLE
from database.models.vote import TABLE_SCHEMA as VOTE_TABLE
from database.models.route import TABLE_SCHEMA as ROUTE_TABLE
from database.models.route_participant import TABLE_SCHEMA as ROUTE_PARTICIPANT_TABLE

# Lista ordenada de todos los esquemas a crear
ALL_TABLES = [
    COMPANY_TABLE,
    EVENT_TABLE,
    EVENT_PARTICIPANT_TABLE,
    SUGGESTION_TABLE,
    VOTE_TABLE,
    ROUTE_TABLE,
    ROUTE_PARTICIPANT_TABLE
]
