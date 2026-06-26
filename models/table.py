from random import shuffle
from typing import TYPE_CHECKING

from models import Card, Deck, Player
from utils.handRanking import find_winner

if TYPE_CHECKING:
    from models import Emitter


class Table:
    def __init__(
        self,
        host_player: Player,
        players: list[Player] | None = None,
        emitter: Emitter | None = None,
    ):
        self._emitter = emitter

        self._host_player = host_player
        self._players = [host_player]
        if players:
            self._players.extend(players)

        self._deck = Deck.create_standard_deck()
        self._has_started = False

        self._orfan_pot = 0
        self._small_blind_value = 10
        self._big_blind_value = 20

        self._table_cards: list[Card] = []

        self._small_blind_index = 0
        self._current_player_index = self._small_blind_index

    @property
    def id(self) -> int:
        return id(self)

    @property
    def room(self) -> str:
        return f"table_{self.id}"

    @property
    def has_started(self) -> bool:
        return self._has_started

    @property
    def host_player(self) -> Player:
        return self._host_player

    @host_player.setter
    def host_player(self, player: Player) -> None:
        if player not in self._players:
            raise ValueError("Host player must be one of the players at the table.")
        self._host_player = player

    @property
    def players(self) -> tuple[Player, ...]:
        return tuple(self._players)

    @property
    def current_player(self) -> Player | None:
        if not self._has_started:
            return None
        return self._players[self._current_player_index]

    @property
    def table_cards(self) -> tuple[Card, ...]:
        return tuple(self._table_cards)

    @property
    def pot(self) -> int:
        return sum(player.current_bet for player in self._players) + self._orfan_pot

    @property
    def max_current_bet(self) -> int:
        return max(player.current_bet for player in self._players)

    @property
    def small_blind_value(self) -> int:
        return self._small_blind_value

    @property
    def big_blind_value(self) -> int:
        return self._big_blind_value

    @property
    def small_blind_player(self) -> Player | None:
        if not self._players:
            return None
        return self._players[self._small_blind_index]

    @property
    def big_blind_player(self) -> Player | None:
        if not self._players:
            return None
        return self._players[(self._small_blind_index - 1) % len(self._players)]

    def __str__(self) -> str:
        return (
            f"players={[str(player) for player in self._players]}, "
            f"pot={self.pot}, "
            f"current_player={self.current_player.name if self.current_player else None})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def add_player(self, player: Player) -> None:
        if self._has_started:
            raise ValueError("Cannot join a game that has already started.")
        if len(self._players) >= 12:
            raise ValueError("Table is full. Maximum 12 players allowed.")
        if player in self._players:
            raise ValueError("Player is already in the game.")
        if player.name in [p.name for p in self._players]:
            raise ValueError("A player with that name is already in the game.")

        self._players.append(player)

    def remove_player(self, player: Player) -> None:
        if player not in self._players:
            raise ValueError("Player is not in the game.")
        if self._has_started:
            self._orfan_pot += player.current_bet
        self._players.remove(player)

    def start_game(self) -> None:
        if self._has_started:
            raise ValueError("Game has already started.")
        if len(self._players) < 2:
            raise ValueError("At least two players are required to start the game.")
        shuffle(self._players)
        self._has_started = True
        self._reset_game()

    def place_bet(self, player: Player, amount: int) -> None:
        current_max_bet = self.max_current_bet
        if player.current_bet + amount < current_max_bet:
            raise ValueError(
                f"Bet must be at least {current_max_bet - player.current_bet} to call."
            )
        player.bet(amount)
        self._advance_turn()

    def fold(self, player: Player) -> None:
        player.fold()
        self._advance_turn()

    def call(self, player: Player) -> int:
        current_max_bet = self.max_current_bet
        call_amount = current_max_bet - player.current_bet
        player.bet(call_amount)
        self._advance_turn()

        return call_amount

    def _advance_turn(self) -> None:
        if not self._check_end_round():
            n = len(self._players)
            for _ in range(n):
                self._current_player_index = (self._current_player_index + 1) % n
                if self._players[self._current_player_index].is_active:
                    return
        else:
            for player in self._players:
                player.has_acted = False

            self._reset_current_player_index()

    def _check_end_round(self) -> bool:
        active_players = [player for player in self._players if player.is_active]

        if len(active_players) == 1:
            winner = active_players[0]
            winner.win(self.pot)
            self._reset_game()
            return True

        max_bet = self.max_current_bet
        betting_settled = all(
            player.current_bet == max_bet or player.is_all_in
            for player in active_players
        )

        if betting_settled and all(player.has_acted for player in active_players):
            if len(self._table_cards) == 0:
                self._deal_table_cards(3)
            elif len(self._table_cards) < 5:
                self._deal_table_cards(1)
            else:
                self._showdown()

            return True

        return False

    def _reset_game(self) -> None:
        self._deck = Deck.create_standard_deck()
        self._table_cards = []
        self._orfan_pot = 0
        for player in self._players:
            player.reset_for_new_round()
            if player.is_active:
                self._deal_player_cards(player)
        self._small_blind_index = (self._small_blind_index + 1) % len(self._players)
        self._reset_current_player_index()
        self._deal_blinds()

    def _reset_current_player_index(self) -> None:
        self._current_player_index = self._small_blind_index

    def _showdown(self) -> None:
        self._deal_table_cards(5 - len(self._table_cards))
        winners = find_winner(
            self._table_cards, [p for p in self._players if p.is_active]
        )
        pot_share = self.pot // len(winners)
        for winner in winners:
            winner.win(pot_share)

        self._reset_game()

    def _deal_blinds(self) -> None:
        small_blind_bet, big_blind_bet = self._small_blind_value, self._big_blind_value

        if sbp := self.small_blind_player:
            sbp.bet(small_blind_bet, acted=False)
        else:
            raise ValueError("Small blind player not found.")

        if bbp := self.big_blind_player:
            bbp.bet(big_blind_bet, acted=False)
        else:
            raise ValueError("Big blind player not found.")

    def _deal_table_cards(self, number: int) -> None:
        for _ in range(number):
            self._table_cards.append(self._deck.draw())

    def _deal_player_cards(self, player: Player) -> None:
        player.add_card_to_hand(self._deck.draw())
        player.add_card_to_hand(self._deck.draw())
