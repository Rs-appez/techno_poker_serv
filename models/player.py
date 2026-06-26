from typing import override

from models import Card


class Player:
    def __init__(self, name: str, sid: str):
        self._name = name
        self._sid = sid
        self._hand: list[Card] = []
        self._chips = 1000
        self._current_bet = 0

        self._is_all_in = False
        self._is_folded = False
        self._is_out = False
        self._has_acted = False

        self._is_round_ready = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def sid(self) -> str:
        return self._sid

    @sid.setter
    def sid(self, new_sid: str):
        self._sid = new_sid

    @property
    def hand(self) -> list[Card]:
        return self._hand

    @property
    def is_round_ready(self) -> bool:
        return self._is_round_ready

    @is_round_ready.setter
    def is_round_ready(self, value: bool):
        self._is_round_ready = value

    @property
    def is_folded(self) -> bool:
        return self._is_folded

    @property
    def is_out(self) -> bool:
        return self._is_out

    @property
    def is_active(self) -> bool:
        return not self._is_folded and not self._is_out

    @property
    def is_all_in(self) -> bool:
        return self._is_all_in

    @property
    def has_acted(self) -> bool:
        return self._has_acted or self.is_all_in

    @has_acted.setter
    def has_acted(self, value: bool):
        self._has_acted = value

    @property
    def chips(self) -> int:
        return self._chips

    @property
    def current_bet(self) -> int:
        return self._current_bet

    @override
    def __str__(self) -> str:
        return f"Player(name={self._name}, sid={self._sid}, chips={self._chips}, current_bet={self._current_bet}, is_folded={self._is_folded}, is_out={self._is_out}, is_all_in={self._is_all_in}, has_acted={self._has_acted})"

    @override
    def __eq__(self, other) -> bool:
        if not isinstance(other, Player):
            return False
        return self._sid == other._sid

    @override
    def __hash__(self) -> int:
        return hash(self._sid + self._name)

    def add_card_to_hand(self, card: Card):
        self._hand.append(card)

    def win(self, amount: int):
        self._chips += amount

    def bet(self, amount: int, acted: bool = True):
        if amount > self._chips:
            raise ValueError("Not enough chips to bet that amount.")
        elif amount < 0:
            raise ValueError("Bet amount must be greater than zero.")

        if acted:
            self._has_acted = True
        self._chips -= amount
        self._current_bet += amount

        if self._chips == 0:
            self._is_all_in = True

    def all_in(self) -> int:
        self._has_acted = True
        self._is_all_in = True
        self._current_bet += self._chips
        all_in_amount = self._chips
        self._chips = 0

        return all_in_amount

    def fold(self):
        self._hand = []
        self._has_acted = True
        self._is_folded = True

    def reset_for_new_round(self):
        self._hand = []
        self._current_bet = 0
        self._has_acted = False
        self._is_folded = False
        self._is_all_in = False
        self._is_round_ready = False
        if self.chips <= 0:
            self._is_out = True
