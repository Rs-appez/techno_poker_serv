from enum import StrEnum


class ClientEvent(StrEnum):
    """Events received FROM clients."""

    LIST_TABLES = "list_tables"
    CREATE_TABLE = "create_table"
    JOIN_TABLE = "join_table"
    QUIT_TABLE = "quit_table"

    START_GAME = "start_game"

    BET = "bet"
    FOLD = "fold"
    CALL = "call"


class ServerEvent(StrEnum):
    """Events emitted TO clients."""

    ERROR = "error"
    AUTH_TOKEN = "auth_token"

    JOINED_TABLE = "joined_table"

    GAME_STARTED = "game_started"
    YOUR_TURN = "your_turn"

    PLAYER_ACTION = "player_action"

    CARDS_DEALT = "cards_dealt"
    NEXT_ROUND = "next_round"

    END_GAME = "end_game"
