from models.deck import Card, Rank, Suit
from models.player import Player
from utils.handRanking import (
    HandValue,
    determine_high_card,
    evaluate_hand,
    find_winner,
)


def test_royal_flush_and_winner():
    player1 = Player(name="Alice", sid="1")
    player2 = Player(name="Bob", sid="2")

    # Give Alice a royal flush in hearts (A K in hand + Q J 10 on table)
    player1._hand = [Card(Rank.ACE, Suit.HEARTS), Card(Rank.KING, Suit.HEARTS)]
    # Bob has high hearts of other suits -> won't make royal flush
    player2._hand = [Card(Rank.ACE, Suit.CLUBS), Card(Rank.KING, Suit.CLUBS)]

    table = [
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.TEN, Suit.HEARTS),
        Card(Rank.TWO, Suit.CLUBS),
        Card(Rank.THREE, Suit.SPADES),
    ]

    assert evaluate_hand(table, player1._hand) == HandValue.ROYAL_FLUSH.value
    winners = find_winner(table, [player1, player2])
    assert len(winners) == 1 and winners[0].name == "Alice"


def test_four_of_a_kind_detection():
    player = Player(name="Quads", sid="q")
    # Player holds one queen, table has the other three -> four of a kind
    player._hand = [Card(Rank.QUEEN, Suit.SPADES), Card(Rank.TWO, Suit.CLUBS)]

    table = [
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.HEARTS),
    ]

    assert evaluate_hand(table, player._hand) == HandValue.FOUR_OF_A_KIND.value


def test_full_house_detection():
    player = Player(name="FH", sid="fh")
    # Player holds two tens and table contains the third ten and two kings -> full house
    player._hand = [Card(Rank.TEN, Suit.SPADES), Card(Rank.TEN, Suit.HEARTS)]

    table = [
        Card(Rank.TEN, Suit.CLUBS),
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.HEARTS),
    ]

    assert evaluate_hand(table, player._hand) == HandValue.FULL_HOUSE.value


def test_high_card_tiebreaker_and_determine_high_card():
    p1 = Player(name="P1", sid="1")
    p2 = Player(name="P2", sid="2")

    # Board that gives no pairs; winner decided by highest card among combined 7 cards
    table = [
        Card(Rank.TWO, Suit.CLUBS),
        Card(Rank.THREE, Suit.DIAMONDS),
        Card(Rank.FOUR, Suit.SPADES),
        Card(Rank.FIVE, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.CLUBS),
    ]

    p1._hand = [Card(Rank.ACE, Suit.HEARTS), Card(Rank.NINE, Suit.DIAMONDS)]
    p2._hand = [Card(Rank.KING, Suit.HEARTS), Card(Rank.JACK, Suit.DIAMONDS)]

    # Both should evaluate to HIGH_CARD
    assert evaluate_hand(table, p1._hand) == HandValue.HIGH_CARD.value
    assert evaluate_hand(table, p2._hand) == HandValue.HIGH_CARD.value

    # Winner should be p1 because of the Ace
    winners = find_winner(table, [p1, p2])
    assert len(winners) == 1 and winners[0].name == "P1"

    # determine_high_card should return cards sorted descending by rank
    sorted_cards = determine_high_card(table, p1._hand)
    ranks = [c.rank.value for c in sorted_cards]
    assert ranks == sorted(ranks, reverse=True)


def test_straight_and_straight_flush_detection():
    p = Player(name="S", sid="s")
    # Straight: 6-7-8-9-10 (mix of suits)
    p._hand = [Card(Rank.SIX, Suit.HEARTS), Card(Rank.SEVEN, Suit.SPADES)]
    table = [
        Card(Rank.EIGHT, Suit.CLUBS),
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.TEN, Suit.DIAMONDS),
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.SPADES),
    ]
    assert evaluate_hand(table, p._hand) == HandValue.STRAIGHT.value

    # Straight flush: 5-6-7-8-9 of spades
    p_sf = Player(name="SF", sid="sf")
    p_sf._hand = [Card(Rank.SEVEN, Suit.SPADES), Card(Rank.SIX, Suit.SPADES)]
    table_sf = [
        Card(Rank.FIVE, Suit.SPADES),
        Card(Rank.EIGHT, Suit.SPADES),
        Card(Rank.NINE, Suit.SPADES),
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.CLUBS),
    ]
    assert evaluate_hand(table_sf, p_sf._hand) == HandValue.STRAIGHT_FLUSH.value


def test_two_pair_and_one_pair_detection():
    p = Player(name="TP", sid="tp")
    # Two pair: 4s and 9s
    p._hand = [Card(Rank.FOUR, Suit.HEARTS), Card(Rank.NINE, Suit.SPADES)]
    table = [
        Card(Rank.FOUR, Suit.CLUBS),
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.TWO, Suit.DIAMONDS),
        Card(Rank.THREE, Suit.CLUBS),
        Card(Rank.SEVEN, Suit.HEARTS),
    ]
    assert evaluate_hand(table, p._hand) == HandValue.TWO_PAIR.value

    p_op = Player(name="OP", sid="op")
    # One pair: 5s
    p_op._hand = [Card(Rank.FIVE, Suit.HEARTS), Card(Rank.EIGHT, Suit.SPADES)]
    table_op = [
        Card(Rank.FIVE, Suit.CLUBS),
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.DIAMONDS),
        Card(Rank.SIX, Suit.CLUBS),
        Card(Rank.KING, Suit.HEARTS),
    ]
    assert evaluate_hand(table_op, p_op._hand) == HandValue.ONE_PAIR.value


if __name__ == "__main__":
    test_royal_flush_and_winner()
    test_four_of_a_kind_detection()
    test_full_house_detection()
    test_high_card_tiebreaker_and_determine_high_card()
    test_straight_and_straight_flush_detection()
    test_two_pair_and_one_pair_detection()
    print("All tests passed!")
