from dataclasses import dataclass
from enum import Enum
import random


class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"


class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"


@dataclass
class Deck:
    cards: list[Card]

    @classmethod
    def create_standard_deck(cls, shuffled=True) -> "Deck":
        deck = Deck(
            cards=[Card(rank=rank, suit=suit) for suit in Suit for rank in Rank]
        )
        if shuffled:
            deck.shuffle()
        return deck

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self) -> Card:
        if not self.cards:
            raise ValueError("Deck is empty")
        return self.cards.pop()
