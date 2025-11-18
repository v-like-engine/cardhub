"""
Uno deck model representing a complete Uno card deck.

This module provides Uno-specific deck functionality with
proper card distribution and Uno rules.
"""

import random
from typing import List, Optional
from .uno_card import UnoCard, UnoColor, UnoType


class UnoDeck:
    """
    Represents a complete Uno deck with proper card distribution.

    Standard Uno deck contains 108 cards:
    - 76 Number cards (19 each of Red, Blue, Green, Yellow)
    - 24 Action cards (Skip, Reverse, Draw Two in each color)
    - 8 Wild cards (4 Wild, 4 Wild Draw Four)
    """

    def __init__(self):
        """Initialize a new Uno deck."""
        self.cards: List[UnoCard] = []
        self.discarded: List[UnoCard] = []
        self.reset()

    def reset(self) -> None:
        """
        Reset the deck to a full standard Uno deck and shuffle.

        Creates a new 108-card Uno deck according to official rules.
        """
        self.cards.clear()
        self.discarded.clear()

        # Create number cards for each color
        for color in [UnoColor.RED, UnoColor.BLUE, UnoColor.GREEN, UnoColor.YELLOW]:
            # One 0 card per color
            self.cards.append(UnoCard(color, UnoType.NUMBER, 0))

            # Two of each number 1-9 per color
            for number in range(1, 10):
                self.cards.append(UnoCard(color, UnoType.NUMBER, number))
                self.cards.append(UnoCard(color, UnoType.NUMBER, number))

            # Two of each action card per color
            for action_type in [UnoType.SKIP, UnoType.REVERSE, UnoType.DRAW_TWO]:
                self.cards.append(UnoCard(color, action_type))
                self.cards.append(UnoCard(color, action_type))

        # Add wild cards
        for _ in range(4):
            self.cards.append(UnoCard(UnoColor.WILD, UnoType.WILD))
            self.cards.append(UnoCard(UnoColor.WILD, UnoType.WILD_DRAW_FOUR))

        self.shuffle()

    def shuffle(self) -> None:
        """Shuffle the cards in the deck."""
        random.shuffle(self.cards)

    def deal_card(self) -> Optional[UnoCard]:
        """
        Deal one card from the top of the deck.

        Returns:
            The card dealt, or None if deck is empty
        """
        if self.is_empty():
            return None
        return self.cards.pop()

    def deal_hand(self, num_cards: int) -> List[UnoCard]:
        """
        Deal a hand of cards from the deck.

        Args:
            num_cards: Number of cards to deal

        Returns:
            List of cards dealt
        """
        hand = []
        for _ in range(num_cards):
            card = self.deal_card()
            if card is None:
                break
            hand.append(card)
        return hand

    def peek_top_card(self) -> Optional[UnoCard]:
        """
        Look at the top card without removing it.

        Returns:
            The top card, or None if deck is empty
        """
        if self.is_empty():
            return None
        return self.cards[-1]

    def add_card(self, card: UnoCard) -> None:
        """
        Add a card to the bottom of the deck.

        Args:
            card: Card to add to the deck
        """
        self.cards.insert(0, card)

    def add_cards(self, cards: List[UnoCard]) -> None:
        """
        Add multiple cards to the bottom of the deck.

        Args:
            cards: List of cards to add
        """
        for card in cards:
            self.add_card(card)

    def discard_card(self, card: UnoCard) -> None:
        """
        Move a card to the discard pile.

        Args:
            card: Card to discard
        """
        if card in self.cards:
            self.cards.remove(card)
        self.discarded.append(card)

    def reshuffle_discarded(self, keep_top_card: bool = True) -> None:
        """
        Shuffle discarded cards back into the deck.

        Args:
            keep_top_card: Whether to keep the top discard card separate
        """
        if keep_top_card and self.discarded:
            top_card = self.discarded.pop()
            self.cards.extend(self.discarded)
            self.discarded = [top_card]
        else:
            self.cards.extend(self.discarded)
            self.discarded.clear()

        self.shuffle()

    def is_empty(self) -> bool:
        """
        Check if the deck is empty.

        Returns:
            True if no cards remain in deck, False otherwise
        """
        return len(self.cards) == 0

    def cards_remaining(self) -> int:
        """
        Get the number of cards remaining in the deck.

        Returns:
            Number of cards left in the deck
        """
        return len(self.cards)

    def get_cards_by_color(self, color: UnoColor) -> List[UnoCard]:
        """
        Get all cards of a specific color from the deck.

        Args:
            color: The color to filter by

        Returns:
            List of cards matching the color
        """
        return [card for card in self.cards if card.color == color]

    def get_cards_by_type(self, card_type: UnoType) -> List[UnoCard]:
        """
        Get all cards of a specific type from the deck.

        Args:
            card_type: The type to filter by

        Returns:
            List of cards matching the type
        """
        return [card for card in self.cards if card.card_type == card_type]

    def get_wild_cards(self) -> List[UnoCard]:
        """
        Get all wild cards from the deck.

        Returns:
            List of wild cards
        """
        return [card for card in self.cards if card.is_wild()]

    def get_action_cards(self) -> List[UnoCard]:
        """
        Get all action cards from the deck.

        Returns:
            List of action cards
        """
        return [card for card in self.cards if card.is_action_card()]

    def to_dict(self) -> dict:
        """
        Convert deck to dictionary representation.

        Returns:
            Dictionary containing deck state
        """
        return {
            'cards': [card.to_dict() for card in self.cards],
            'discarded': [card.to_dict() for card in self.discarded],
            'cards_remaining': self.cards_remaining(),
            'total_cards': 108
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'UnoDeck':
        """
        Create deck from dictionary representation.

        Args:
            data: Dictionary containing deck data

        Returns:
            UnoDeck object created from the dictionary
        """
        deck = cls()
        deck.cards = [UnoCard.from_dict(card_data) for card_data in data['cards']]
        deck.discarded = [UnoCard.from_dict(card_data) for card_data in data['discarded']]
        return deck

    def __len__(self) -> int:
        """
        Get the number of cards in the deck.

        Returns:
            Number of cards in the deck
        """
        return len(self.cards)

    def __str__(self) -> str:
        """
        String representation of the deck.

        Returns:
            String showing deck size and composition
        """
        if self.is_empty():
            return "Empty Uno deck"
        else:
            color_counts = {}
            for color in UnoColor:
                color_counts[color.value] = len(self.get_cards_by_color(color))

            return f"Uno deck with {len(self.cards)} cards: {color_counts}"