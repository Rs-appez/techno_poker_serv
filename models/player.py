from models import Card


class Player:
    def __init__(self, name):
        self._name = name
        self._hand: list[Card] = []
        self._chips = 1000

    @property
    def name(self):
        return self._name

    @property
    def hand(self):
        return self._hand

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
        self._chips -= amount
        return amount

    def win(self, amount: int):
        self._chips += amount
