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
    is_folded: bool
    is_current_player: bool
    is_small_blind: bool
    is_big_blind: bool

    def to_dict(self) -> dict[str, str | int | bool | list[dict[str, str]]]:
        return {
            "player_name": self.player_name,
            "chips": self.chips,
            "is_folded": self.is_folded,
            "is_current_player": self.is_current_player,
            "is_small_blind": self.is_small_blind,
            "is_big_blind": self.is_big_blind,
        }

    @classmethod
    def from_player(cls, player: Player, table: Table) -> "EmitPlayer":
        return cls(
            player_name=player.name,
            chips=player.chips,
            is_folded=player.is_folded,
            is_current_player=player == table.current_player,
            is_small_blind=player == table.small_blind_player,
            is_big_blind=player == table.big_blind_player,
        )


@dataclass
class EmitMyplayer(EmitPlayer):
    hand: list[dict[str, str]]

    @override
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict["hand"] = self.hand
        return base_dict

    @classmethod
    @override
    def from_player(cls, player: Player, table: Table) -> "EmitMyplayer":
        emit_player = super().from_player(player, table)
        return cls(
            player_name=emit_player.player_name,
            chips=emit_player.chips,
            is_folded=emit_player.is_folded,
            is_current_player=emit_player.is_current_player,
            is_small_blind=emit_player.is_small_blind,
            is_big_blind=emit_player.is_big_blind,
            hand=[card.to_dict() for card in player.hand],
        )


@dataclass
class EmitTable:
    table_id: int
    host_name: str
    table_cards: list[dict[str, str]]
    pot: int
    players: list[EmitPlayer]

    def to_dict(
        self,
    ) -> dict[
        str,
        str
        | int
        | list[dict[str, str]]
        | list[dict[str, str | int | bool | list[dict[str, str]]]],
    ]:
        return {
            "table_id": self.table_id,
            "host_name": self.host_name,
            "table_cards": self.table_cards,
            "pot": self.pot,
            "players": [player.to_dict() for player in self.players],
        }

    @classmethod
    def from_table(cls, table: Table) -> "EmitTable":
        return cls(
            table_id=table.id,
            host_name=table.host_player.name,
            table_cards=[card.to_dict() for card in table.table_cards],
            pot=table.pot,
            players=[EmitPlayer.from_player(player, table) for player in table.players],
        )


@dataclass
class EmitChangeTable:
    player: EmitPlayer
    entered: bool

    def to_dict(self):
        return {
            "player_name": self.player.to_dict(),
            "entered": self.entered,
        }


@dataclass
class EmitPlayerAction:
    action: ClientEvent
    table_id: int
    player: str
    amount: int | None = None

    def to_dict(self):
        payload = {
            "action": self.action,
            "table_id": self.table_id,
            "player": self.player,
        }
        if self.amount is not None:
            payload["amount"] = self.amount
        return payload
