from models import Card, Deck, Player


class Table:
    def __init__(self, players: list[Player]):
        self.players = players
        self.deck = Deck.create_standard_deck()

        self.table_cards: list[Card] = []
