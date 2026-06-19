from models import Card, Deck, Player


class Table:
    def __init__(self, host_player: Player, players: list[Player] | None = None):
        self._players = [host_player]
        if players:
            self._players.extend(players)

        self._deck = Deck.create_standard_deck()
        self._has_started = False

        self._small_blind_value = 10
        self._big_blind_value = 20

        self._table_cards: list[Card] = []
        self._current_bets: dict[Player, int] = {player: 0 for player in self._players}

        self._small_blind_index = 0

    @property
    def id(self):
        return id(self)

    @property
    def has_started(self):
        return self._has_started

    @property
    def players(self):
        return tuple(self._players)

    @property
    def table_cards(self):
        return tuple(self._table_cards)

    @property
    def pot(self):
        return sum(self._current_bets.values())

    @property
    def small_blind_value(self):
        return self._small_blind_value

    @property
    def big_blind_value(self):
        return self._big_blind_value

    @property
    def small_blind_player(self):
        return self._players[self._small_blind_index]

    @property
    def big_blind_player(self):
        return self._players[(self._small_blind_index + 1) % len(self._players)]

    def add_player(self, player: Player):
        if self._has_started:
            raise ValueError("Cannot join a game that has already started.")
        if player in self._players:
            raise ValueError("Player is already in the game.")
        self._players.append(player)
        self._current_bets[player] = 0

    def start_game(self):
        if self._has_started:
            raise ValueError("Game has already started.")
        if len(self._players) < 2:
            raise ValueError("At least two players are required to start the game.")
        self._has_started = True

    def _deal_blinds(self):
        small_blind_bet, big_blind_bet = self._small_blind_value, self._big_blind_value

        self.small_blind_player.bet(small_blind_bet)
        self.big_blind_player.bet(big_blind_bet)

        self._current_bets[self.small_blind_player] += small_blind_bet
        self._current_bets[self.big_blind_player] += big_blind_bet

    def _deal_table_cards(self, number: int):
        for _ in range(number):
            self._table_cards.append(self._deck.draw())

    def _deal_player_cards(self, player: Player):
        player.add_card_to_hand(self._deck.draw())
        player.add_card_to_hand(self._deck.draw())
