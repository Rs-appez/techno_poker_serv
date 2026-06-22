from models.deck import Card, Rank, Suit
from models.player import Player
from utils.handRanking import find_winner


def _p(name, card1, card2):
    p = Player(name, 1000)
    p._hand = [card1, card2]
    return p


def test_high_card_wins():
    # Alice: A K, Bob: A Q, board irrelevant high cards
    table = [
        Card(rank=Rank.TWO, suit=Suit.CLUBS),
        Card(rank=Rank.THREE, suit=Suit.DIAMONDS),
        Card(rank=Rank.FOUR, suit=Suit.HEARTS),
        Card(rank=Rank.FIVE, suit=Suit.SPADES),
        Card(rank=Rank.SEVEN, suit=Suit.CLUBS),
    ]
    alice = _p(
        "Alice",
        Card(rank=Rank.ACE, suit=Suit.SPADES),
        Card(rank=Rank.KING, suit=Suit.SPADES),
    )
    bob = _p(
        "Bob",
        Card(rank=Rank.ACE, suit=Suit.HEARTS),
        Card(rank=Rank.QUEEN, suit=Suit.HEARTS),
    )
    winners = find_winner(table, [alice, bob])
    assert winners == [alice]


def test_pair_with_kicker():
    # Board has a pair of Kings; Alice has Ace kicker, Bob has Queen kicker
    table = [
        Card(rank=Rank.KING, suit=Suit.DIAMONDS),
        Card(rank=Rank.KING, suit=Suit.CLUBS),
        Card(rank=Rank.TWO, suit=Suit.HEARTS),
        Card(rank=Rank.THREE, suit=Suit.SPADES),
        Card(rank=Rank.FOUR, suit=Suit.CLUBS),
    ]
    alice = _p(
        "Alice",
        Card(rank=Rank.ACE, suit=Suit.SPADES),
        Card(rank=Rank.SEVEN, suit=Suit.SPADES),
    )
    bob = _p(
        "Bob",
        Card(rank=Rank.QUEEN, suit=Suit.HEARTS),
        Card(rank=Rank.JACK, suit=Suit.HEARTS),
    )
    winners = find_winner(table, [alice, bob])
    assert winners == [alice]


def test_two_pair_comparison():
    # Alice ends up with Aces and Twos, Bob has Kings and Twos -> Alice wins
    table = [
        Card(rank=Rank.TWO, suit=Suit.HEARTS),
        Card(rank=Rank.KING, suit=Suit.CLUBS),
        Card(rank=Rank.FOUR, suit=Suit.DIAMONDS),
        Card(rank=Rank.SEVEN, suit=Suit.SPADES),
        Card(rank=Rank.NINE, suit=Suit.CLUBS),
    ]
    alice = _p(
        "Alice",
        Card(rank=Rank.ACE, suit=Suit.SPADES),
        Card(rank=Rank.THREE, suit=Suit.SPADES),
    )
    bob = _p(
        "Bob",
        Card(rank=Rank.KING, suit=Suit.HEARTS),
        Card(rank=Rank.JACK, suit=Suit.HEARTS),
    )
    winners = find_winner(table, [alice, bob])
    assert winners == [alice]


def test_straight_wheel():
    # Wheel straight (A-2-3-4-5) detection
    table = [
        Card(rank=Rank.TWO, suit=Suit.CLUBS),
        Card(rank=Rank.THREE, suit=Suit.DIAMONDS),
        Card(rank=Rank.FOUR, suit=Suit.HEARTS),
        Card(rank=Rank.FIVE, suit=Suit.SPADES),
        Card(rank=Rank.NINE, suit=Suit.CLUBS),
    ]
    alice = _p(
        "Alice",
        Card(rank=Rank.ACE, suit=Suit.SPADES),
        Card(rank=Rank.TEN, suit=Suit.SPADES),
    )
    bob = _p(
        "Bob",
        Card(rank=Rank.SEVEN, suit=Suit.HEARTS),
        Card(rank=Rank.EIGHT, suit=Suit.HEARTS),
    )
    winners = find_winner(table, [alice, bob])
    assert winners == [alice]


def test_flush_beats_straight():
    # Alice makes a flush, Bob a straight; flush should win
    table = [
        Card(rank=Rank.TWO, suit=Suit.HEARTS),
        Card(rank=Rank.FOUR, suit=Suit.HEARTS),
        Card(rank=Rank.SIX, suit=Suit.HEARTS),
        Card(rank=Rank.EIGHT, suit=Suit.HEARTS),
        Card(rank=Rank.NINE, suit=Suit.CLUBS),
    ]
    alice = _p(
        "Alice",
        Card(rank=Rank.THREE, suit=Suit.HEARTS),
        Card(rank=Rank.KING, suit=Suit.HEARTS),
    )  # flush hearts
    bob = _p(
        "Bob",
        Card(rank=Rank.FIVE, suit=Suit.SPADES),
        Card(rank=Rank.SEVEN, suit=Suit.DIAMONDS),
    )  # straight 3-4-5-6-7 (not on board fully)
    winners = find_winner(table, [alice, bob])
    assert winners == [alice]


def test_full_house_vs_four_of_a_kind():
    # Bob has four of a kind on board + hole, beats Alice full house
    table = [
        Card(rank=Rank.KING, suit=Suit.HEARTS),
        Card(rank=Rank.KING, suit=Suit.DIAMONDS),
        Card(rank=Rank.KING, suit=Suit.CLUBS),
        Card(rank=Rank.TWO, suit=Suit.SPADES),
        Card(rank=Rank.THREE, suit=Suit.CLUBS),
    ]
    alice = _p(
        "Alice",
        Card(rank=Rank.TWO, suit=Suit.HEARTS),
        Card(rank=Rank.TWO, suit=Suit.DIAMONDS),
    )  # full house KKK22
    bob = _p(
        "Bob",
        Card(rank=Rank.KING, suit=Suit.SPADES),
        Card(rank=Rank.ACE, suit=Suit.HEARTS),
    )  # four kings
    winners = find_winner(table, [alice, bob])
    assert winners == [bob]


def test_split_pot_on_identical_best_hand():
    # Both players have identical best five-card hands -> split
    table = [
        Card(rank=Rank.TEN, suit=Suit.SPADES),
        Card(rank=Rank.JACK, suit=Suit.SPADES),
        Card(rank=Rank.QUEEN, suit=Suit.SPADES),
        Card(rank=Rank.KING, suit=Suit.SPADES),
        Card(rank=Rank.TWO, suit=Suit.CLUBS),
    ]
    alice = _p(
        "Alice",
        Card(rank=Rank.ACE, suit=Suit.SPADES),
        Card(rank=Rank.THREE, suit=Suit.DIAMONDS),
    )  # royal via A spades + table
    bob = _p(
        "Bob",
        Card(rank=Rank.ACE, suit=Suit.SPADES),
        Card(rank=Rank.FOUR, suit=Suit.HEARTS),
    )  # same royal possibility
    winners = find_winner(table, [alice, bob])
    # Both should be returned as winners (split pot)
    assert set(winners) == {alice, bob}
