from models import Card, Deck, Player


class Table:
    def __init__(self, players: list[Player]):
        self._players = players
        self._deck = Deck.create_standard_deck()
        self._has_started = False

        self._table_cards: list[Card] = []

    @property
    def has_started(self):
        return self._has_started

    @property
    def players(self):
        return self._players

    @property
    def table_cards(self):
        return self._table_cards
