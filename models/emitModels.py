from dataclasses import dataclass


@dataclass
class ChangeTable:
    player_name: str
    entered: bool


@dataclass
class Player:
    player_name: str
    chips: int
    is_folded: bool
    is_current_player: bool
    is_small_blind: bool
    is_big_blind: bool


@dataclass
class Myplayer(Player):
    hand: list[dict[str, str]]


@dataclass
class Table:
    table_id: int
    host_name: str
    table_cards: list[dict[str, str]]
    pot: int
    players: list[Player]
