from enum import Enum

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


def evaluate_hand(table: list[Card], hand: list[Card]) -> int:
    all_cards = table + hand
    all_cards.sort(key=lambda card: card.rank.value, reverse=True)

    # Check for flush
    suits = {card.suit for card in all_cards}
    is_flush = len(suits) == 1

    # Check for straight
    ranks = [card.rank.value for card in all_cards]
    if Rank.ACE.value in ranks and Rank.TWO.value in ranks:
        ranks.append(1)
        ranks.remove(Rank.ACE.value)
    is_straight = all(ranks[i] - 1 == ranks[i + 1] for i in range(len(ranks) - 1))

    if is_flush and is_straight:
        if ranks[0] == Rank.ACE.value:
            return HandValue.ROYAL_FLUSH.value
        return HandValue.STRAIGHT_FLUSH.value

    rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
    if 4 in rank_counts.values():
        return HandValue.FOUR_OF_A_KIND.value
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        return HandValue.FULL_HOUSE.value
    if is_flush:
        return HandValue.FLUSH.value
    if is_straight:
        return HandValue.STRAIGHT.value
    if 3 in rank_counts.values():
        return HandValue.THREE_OF_A_KIND.value
    if list(rank_counts.values()).count(2) == 2:
        return HandValue.TWO_PAIR.value
    if 2 in rank_counts.values():
        return HandValue.ONE_PAIR.value

    return HandValue.HIGH_CARD.value


def determine_high_card(table: list[Card], hand: list[Card]) -> list[Card]:
    all_cards = table + hand
    all_cards.sort(key=lambda card: card.rank.value, reverse=True)
    return all_cards


def find_winner(table: list[Card], players: list[Player]) -> list[Player]:
    players_scores = {player: evaluate_hand(table, player.hand) for player in players}
    max_score = max(players_scores.values())
    winners = [player for player, score in players_scores.items() if score == max_score]

    if len(winners) == 1:
        return winners

    player_high_cards = {
        player: determine_high_card(table, player.hand) for player in winners
    }
    for i in range(7):
        max_high_card = max(
            player_high_cards[player][i].rank.value for player in winners
        )
        winners = [
            player
            for player in winners
            if player_high_cards[player][i].rank.value == max_high_card
        ]
        if len(winners) == 1:
            return winners

    return winners


if __name__ == "__main__":
    from models import Suit

    player1 = Player(name="Alice", sid="1")
    player2 = Player(name="Bob", sid="2")

    player1._hand = [Card(Rank.ACE, Suit.HEARTS), Card(Rank.KING, Suit.HEARTS)]
    player2._hand = [Card(Rank.ACE, Suit.CLUBS), Card(Rank.KING, Suit.CLUBS)]
    table = [
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.TEN, Suit.HEARTS),
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.EIGHT, Suit.HEARTS),
    ]

    winners = find_winner(table, [player1, player2])
    print("Winners:", [winner.name for winner in winners])
