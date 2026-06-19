from models import Card


class Player:
    def __init__(self, name, sid):
        self._name = name
        self._sid = sid
        self._hand: list[Card] = []
        self._chips = 1000
        self._is_folded = False

    @property
    def name(self):
        return self._name

    @property
    def sid(self):
        return self._sid

    @property
    def hand(self):
        return self._hand

    @property
    def is_folded(self):
        return self._is_folded

    @property
    def chips(self):
        return self._chips

    def add_card_to_hand(self, card: Card):
        self._hand.append(card)

    def reset_hand(self):
        self._hand = []

    def bet(self, amount: int):
        if amount > self._chips:
            raise ValueError("Not enough chips to bet that amount.")
        elif amount <= 0:
            raise ValueError("Bet amount must be greater than zero.")
        self._chips -= amount

    def win(self, amount: int):
        self._chips += amount

    def fold(self):
        self._hand = []
