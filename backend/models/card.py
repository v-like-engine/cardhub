"""
Card model representing a playing card with suit and rank.

This module provides the basic Card class that forms the foundation
of all card games in the SoundWound platform.
"""

from enum import Enum
from typing import Union


class Suit(Enum):
    """Enumeration of card suits."""
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(Enum):
    """Enumeration of card ranks with their numeric values."""
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


class Card:
    """
    Represents a playing card with suit and rank.

    A card is the fundamental unit in all card games. Each card has
    a suit (Hearts, Diamonds, Clubs, Spades) and a rank (2-10, J, Q, K, A).
    """

    def __init__(self, suit: Suit, rank: Rank):
        """
        Initialize a new card.

        Args:
            suit: The suit of the card (Hearts, Diamonds, Clubs, Spades)
            rank: The rank of the card (2-10, Jack, Queen, King, Ace)
        """
        self.suit = suit
        self.rank = rank

    def __str__(self) -> str:
        """
        Return string representation of the card.

        Returns:
            Human-readable string representation (e.g., "A♠", "K♥")
        """
        rank_str = {
            Rank.ACE: "A",
            Rank.KING: "K",
            Rank.QUEEN: "Q",
            Rank.JACK: "J"
        }.get(self.rank, str(self.rank.value))

        return f"{rank_str}{self.suit.value}"

    def __repr__(self) -> str:
        """
        Return official string representation of the card.

        Returns:
            String that can recreate the card object
        """
        return f"Card({self.suit}, {self.rank})"

    def __eq__(self, other) -> bool:
        """
        Check if two cards are equal.

        Args:
            other: Another card to compare with

        Returns:
            True if cards have same suit and rank, False otherwise
        """
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        """
        Return hash value for the card.

        Returns:
            Hash value based on suit and rank
        """
        return hash((self.suit, self.rank))

    def __lt__(self, other) -> bool:
        """
        Compare cards for sorting purposes.

        Args:
            other: Another card to compare with

        Returns:
            True if this card ranks lower than the other
        """
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank.value < other.rank.value

    def get_value(self, ace_value: int = 14) -> int:
        """
        Get the numeric value of the card.

        Args:
            ace_value: Value to assign to Ace (default 14, can be 1 or 11)

        Returns:
            Numeric value of the card
        """
        if self.rank == Rank.ACE:
            return ace_value
        return self.rank.value

    def get_blackjack_value(self) -> Union[int, tuple]:
        """
        Get the value of the card in BlackJack.

        Returns:
            Integer value for non-Ace cards, tuple (1, 11) for Ace
        """
        if self.rank == Rank.ACE:
            return (1, 11)
        elif self.rank.value >= 11:  # Face cards
            return 10
        else:
            return self.rank.value

    def is_red(self) -> bool:
        """
        Check if the card is red (Hearts or Diamonds).

        Returns:
            True if card is red, False otherwise
        """
        return self.suit in [Suit.HEARTS, Suit.DIAMONDS]

    def is_black(self) -> bool:
        """
        Check if the card is black (Clubs or Spades).

        Returns:
            True if card is black, False otherwise
        """
        return self.suit in [Suit.CLUBS, Suit.SPADES]

    def is_face_card(self) -> bool:
        """
        Check if the card is a face card (Jack, Queen, King).

        Returns:
            True if card is a face card, False otherwise
        """
        return self.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]

    def to_dict(self) -> dict:
        """
        Convert card to dictionary representation.

        Returns:
            Dictionary with suit and rank information
        """
        return {
            'suit': self.suit.name.lower(),
            'rank': self.rank.name.lower(),
            'value': self.rank.value,
            'display': str(self)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Card':
        """
        Create card from dictionary representation.

        Args:
            data: Dictionary containing card data

        Returns:
            Card object created from the dictionary
        """
        suit = Suit[data['suit'].upper()]
        rank = Rank[data['rank'].upper()]
        return cls(suit, rank)