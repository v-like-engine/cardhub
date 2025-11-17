"""
Uno card model with special Uno-specific properties.

This module extends the basic card model to support Uno's
unique card types and color system.
"""

from enum import Enum
from typing import Optional


class UnoColor(Enum):
    """Enumeration of Uno card colors."""
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    WILD = "wild"


class UnoType(Enum):
    """Enumeration of Uno card types."""
    NUMBER = "number"
    SKIP = "skip"
    REVERSE = "reverse"
    DRAW_TWO = "draw_two"
    WILD = "wild"
    WILD_DRAW_FOUR = "wild_draw_four"


class UnoCard:
    """
    Represents an Uno card with color, type, and value.

    Uno cards have colors (Red, Blue, Green, Yellow, Wild) and types
    (Number, Skip, Reverse, Draw Two, Wild, Wild Draw Four).
    """

    def __init__(self, color: UnoColor, card_type: UnoType, value: Optional[int] = None):
        """
        Initialize a new Uno card.

        Args:
            color: The color of the card
            card_type: The type of the card
            value: The numeric value (0-9 for number cards, None for action cards)
        """
        self.color = color
        self.card_type = card_type
        self.value = value

    def __str__(self) -> str:
        """
        Return string representation of the Uno card.

        Returns:
            Human-readable string representation
        """
        if self.card_type == UnoType.NUMBER:
            return f"{self.color.value.title()} {self.value}"
        elif self.card_type == UnoType.WILD:
            return "Wild"
        elif self.card_type == UnoType.WILD_DRAW_FOUR:
            return "Wild Draw Four"
        else:
            return f"{self.color.value.title()} {self.card_type.value.replace('_', ' ').title()}"

    def __repr__(self) -> str:
        """
        Return official string representation of the card.

        Returns:
            String that can recreate the card object
        """
        return f"UnoCard({self.color}, {self.card_type}, {self.value})"

    def __eq__(self, other) -> bool:
        """
        Check if two Uno cards are equal.

        Args:
            other: Another card to compare with

        Returns:
            True if cards are identical, False otherwise
        """
        if not isinstance(other, UnoCard):
            return False
        return (self.color == other.color and
                self.card_type == other.card_type and
                self.value == other.value)

    def __hash__(self) -> int:
        """
        Return hash value for the card.

        Returns:
            Hash value based on color, type, and value
        """
        return hash((self.color, self.card_type, self.value))

    def is_wild(self) -> bool:
        """
        Check if the card is a wild card.

        Returns:
            True if card is wild, False otherwise
        """
        return self.card_type in [UnoType.WILD, UnoType.WILD_DRAW_FOUR]

    def is_action_card(self) -> bool:
        """
        Check if the card is an action card.

        Returns:
            True if card has special action, False otherwise
        """
        return self.card_type != UnoType.NUMBER

    def can_be_played_on(self, other: 'UnoCard', current_color: Optional[UnoColor] = None) -> bool:
        """
        Check if this card can be played on top of another card.

        Args:
            other: The card this would be played on
            current_color: Current active color (for wild cards)

        Returns:
            True if this card can be played, False otherwise
        """
        # Wild cards can always be played
        if self.is_wild():
            return True

        # Must match color or type/value
        effective_color = current_color if other.is_wild() else other.color

        return (self.color == effective_color or
                self.card_type == other.card_type or
                (self.card_type == UnoType.NUMBER and
                 other.card_type == UnoType.NUMBER and
                 self.value == other.value))

    def get_points(self) -> int:
        """
        Get the point value of the card for scoring.

        Returns:
            Point value of the card
        """
        if self.card_type == UnoType.NUMBER:
            return self.value or 0
        elif self.card_type in [UnoType.SKIP, UnoType.REVERSE, UnoType.DRAW_TWO]:
            return 20
        elif self.card_type in [UnoType.WILD, UnoType.WILD_DRAW_FOUR]:
            return 50
        else:
            return 0

    def to_dict(self) -> dict:
        """
        Convert card to dictionary representation.

        Returns:
            Dictionary with card information
        """
        return {
            'color': self.color.value,
            'type': self.card_type.value,
            'value': self.value,
            'display': str(self),
            'points': self.get_points(),
            'is_wild': self.is_wild(),
            'is_action': self.is_action_card()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'UnoCard':
        """
        Create card from dictionary representation.

        Args:
            data: Dictionary containing card data

        Returns:
            UnoCard object created from the dictionary
        """
        color = UnoColor(data['color'])
        card_type = UnoType(data['type'])
        value = data.get('value')
        return cls(color, card_type, value)