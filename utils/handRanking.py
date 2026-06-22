from enum import Enum
from itertools import combinations

from models import Card, Player, Rank


class HandValue(Enum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9


def _evaluate_five(cards: list[Card]) -> tuple:
    """Evaluate exactly 5 cards. Returns a comparable tuple:
    (hand_value, tiebreaker_ranks...) where higher is better."""
    ranks = sorted((card.rank.value for card in cards), reverse=True)
    suits = [card.suit for card in cards]

    is_flush = len(set(suits)) == 1

    # Count occurrences of each rank
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1

    # Order ranks by (count, rank) descending for tiebreaking
    ordered = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    counts = [count for _, count in ordered]
    tiebreak = tuple(rank for rank, _ in ordered)

    # Check straight (handle wheel: A-2-3-4-5)
    unique_ranks = sorted(set(ranks), reverse=True)
    is_straight = False
    straight_high = None
    if len(unique_ranks) == 5:
        if unique_ranks[0] - unique_ranks[4] == 4:
            is_straight = True
            straight_high = unique_ranks[0]
        # Wheel: A,5,4,3,2
        elif unique_ranks == [Rank.ACE.value, 5, 4, 3, 2]:
            is_straight = True
            straight_high = 5

    if is_straight and is_flush:
        if straight_high == Rank.ACE.value:
            return (HandValue.ROYAL_FLUSH.value, straight_high)
        return (HandValue.STRAIGHT_FLUSH.value, straight_high)
    if counts == [4, 1]:
        return (HandValue.FOUR_OF_A_KIND.value,) + tiebreak
    if counts == [3, 2]:
        return (HandValue.FULL_HOUSE.value,) + tiebreak
    if is_flush:
        return (HandValue.FLUSH.value,) + tuple(ranks)
    if is_straight:
        return (HandValue.STRAIGHT.value, straight_high)
    if counts == [3, 1, 1]:
        return (HandValue.THREE_OF_A_KIND.value,) + tiebreak
    if counts == [2, 2, 1]:
        return (HandValue.TWO_PAIR.value,) + tiebreak
    if counts == [2, 1, 1, 1]:
        return (HandValue.ONE_PAIR.value,) + tiebreak
    return (HandValue.HIGH_CARD.value,) + tuple(ranks)


def evaluate_hand(table: list[Card], hand: list[Card]) -> tuple:
    """Return the best 5-card hand score from the 7 available cards."""
    all_cards = table + hand
    return max(_evaluate_five(list(combo)) for combo in combinations(all_cards, 5))


def find_winner(table: list[Card], players: list[Player]) -> list[Player]:
    players_scores = {player: evaluate_hand(table, player.hand) for player in players}
    best_score = max(players_scores.values())
    return [player for player, score in players_scores.items() if score == best_score]
