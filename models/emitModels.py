from dataclasses import dataclass
from typing import override

from models import Player, Table
from models.events import ClientEvent


@dataclass
class EmitError:
    message: str

    def to_dict(self):
        return {"message": self.message}


@dataclass
class EmitPlayer:
    player_name: str
    chips: int
    current_bet: int
    is_folded: bool
    is_out: bool
    hand: EmitHand | None = None

    def to_dict(self) -> dict[str, str | int | bool | list[dict[str, str]]]:
        return {
            "player_name": self.player_name,
            "hand": self.hand.to_dict()["hand"] if self.hand else [],
            "chips": self.chips,
            "current_bet": self.current_bet,
            "is_folded": self.is_folded,
            "is_out": self.is_out,
        }

    @classmethod
    def from_player(cls, player: Player, hide_hand: bool = True) -> "EmitPlayer":
        return cls(
            player_name=player.name,
            chips=player.chips,
            current_bet=player.current_bet,
            is_folded=player.is_folded,
            is_out=player.is_out,
            hand=EmitHand.from_player(player) if not hide_hand else None,
        )


@dataclass
class EmitHand:
    hand: list[dict[str, str]]

    def to_dict(self):
        return {"hand": self.hand}

    @classmethod
    def from_player(cls, player: Player) -> "EmitHand":
        return cls(
            hand=[card.to_dict() for card in player.hand],
        )


@dataclass
class EmitTable:
    table_id: int
    host_name: str
    table_cards: list[dict[str, str]]
    pot: int
    players: list[EmitPlayer]
    small_blind_value: int
    big_blind_value: int
    current_player_name: str | None = None
    small_blind_player_name: str | None = None
    big_blind_player_name: str | None = None

    def to_dict(
        self,
    ) -> dict:
        return {
            "table_id": self.table_id,
            "host_name": self.host_name,
            "table_cards": self.table_cards,
            "pot": self.pot,
            "players": [player.to_dict() for player in self.players],
            "current_player_name": self.current_player_name,
            "small_blind_value": self.small_blind_value,
            "big_blind_value": self.big_blind_value,
            "small_blind_player_name": self.small_blind_player_name,
            "big_blind_player_name": self.big_blind_player_name,
        }

    @classmethod
    def from_table(cls, table: Table) -> "EmitTable":
        return cls(
            table_id=table.id,
            host_name=table.host_player.name,
            table_cards=[card.to_dict() for card in table.table_cards],
            pot=table.pot,
            players=[EmitPlayer.from_player(player) for player in table.players],
            current_player_name=table.current_player.name
            if table.current_player
            else None,
            small_blind_value=table.small_blind_value,
            big_blind_value=table.big_blind_value,
            small_blind_player_name=table.small_blind_player.name
            if table.small_blind_player
            else None,
            big_blind_player_name=table.big_blind_player.name
            if table.big_blind_player
            else None,
        )


@dataclass
class EmitChangeTable:
    player: EmitPlayer
    entered: bool
    host_name: str

    def to_dict(self):
        return {
            "player": self.player.to_dict(),
            "entered": self.entered,
            "host_name": self.host_name,
        }


@dataclass
class EmitPlayerAction:
    action: ClientEvent
    table: Table
    player: Player
    amount: int | None = None

    def to_dict(self):
        payload = {
            "action": self.action,
            "table": EmitTable.from_table(self.table).to_dict(),
            "player": EmitPlayer.from_player(self.player).to_dict(),
            "amount": self.amount if self.amount is not None else None,
        }
        return payload
