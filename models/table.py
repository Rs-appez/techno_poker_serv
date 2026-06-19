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
        self._current_player_index = 0

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
    def current_player(self):
        if not self._has_started:
            return None
        return self._players[self._current_player_index]

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
        self._deal_blinds()

    def place_bet(self, player: Player, amount: int):
        current_max_bet = max(self._current_bets.values())
        player_current_bet = self._current_bets[player]
        if player_current_bet + amount < current_max_bet:
            raise ValueError(
                f"Bet must be at least {current_max_bet - player_current_bet} to call."
            )
        player.bet(amount)
        self._current_bets[player] += amount
        self._advance_turn()

    def fold(self, player: Player):
        player.fold()
        self._advance_turn()

    def call(self, player: Player) -> int:
        current_max_bet = max(self._current_bets.values())
        player_current_bet = self._current_bets[player]
        call_amount = current_max_bet - player_current_bet
        if call_amount > 0:
            player.bet(call_amount)
            self._current_bets[player] += call_amount
        self._advance_turn()

        return call_amount

    def _advance_turn(self):
        if not self._check_end_game():
            n = len(self._players)
            for _ in range(n):
                self._current_player_index = (self._current_player_index + 1) % n
                if not self._players[self._current_player_index].is_folded:
                    return

    def _check_end_game(self) -> bool:
        active_players = [player for player in self._players if not player.is_folded]
        if len(active_players) == 1:
            winner = active_players[0]
            winner.win(self.pot)
            self._reset_game()
            return True
        return False

    def _reset_game(self):
        self._deck = Deck.create_standard_deck()
        self._table_cards = []
        self._current_bets = {player: 0 for player in self._players}
        for player in self._players:
            player.reset_hand()
        self._small_blind_index = (self._small_blind_index + 1) % len(self._players)
        self._current_player_index = self._small_blind_index
        self._deal_blinds()

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
