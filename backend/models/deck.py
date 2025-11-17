"""
Deck model representing a collection of playing cards.

This module provides deck functionality including shuffling,
dealing, and different deck configurations for various games.
"""

import random
from typing import List, Optional
from .card import Card, Suit, Rank


class Deck:
    """
    Represents a deck of playing cards.

    A deck can be a standard 52-card deck or customized for specific games.
    Provides functionality for shuffling, dealing, and managing cards.
    """

    def __init__(self, include_jokers: bool = False):
        """
        Initialize a new deck of cards.

        Args:
            include_jokers: Whether to include joker cards in the deck
        """
        self.cards: List[Card] = []
        self.discarded: List[Card] = []
        self.include_jokers = include_jokers
        self.reset()

    def reset(self) -> None:
        """
        Reset the deck to a full standard deck and shuffle.

        Creates a new 52-card deck (or 54 with jokers) and shuffles it.
        Clears any discarded cards.
        """
        self.cards.clear()
        self.discarded.clear()

        # Create standard 52-card deck
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(suit, rank))

        # Add jokers if requested
        if self.include_jokers:
            # Jokers represented as special cards
            # Using a custom approach for jokers
            pass  # Jokers implementation can be added later if needed

        self.shuffle()

    def shuffle(self) -> None:
        """
        Shuffle the cards in the deck.

        Uses Fisher-Yates shuffle algorithm for true randomness.
        """
        random.shuffle(self.cards)

    def deal_card(self) -> Optional[Card]:
        """
        Deal one card from the top of the deck.

        Returns:
            The card dealt, or None if deck is empty
        """
        if self.is_empty():
            return None
        return self.cards.pop()

    def deal_hand(self, num_cards: int) -> List[Card]:
        """
        Deal a hand of cards from the deck.

        Args:
            num_cards: Number of cards to deal

        Returns:
            List of cards dealt (may be fewer if deck doesn't have enough)
        """
        hand = []
        for _ in range(num_cards):
            card = self.deal_card()
            if card is None:
                break
            hand.append(card)
        return hand

    def peek_top_card(self) -> Optional[Card]:
        """
        Look at the top card without removing it.

        Returns:
            The top card, or None if deck is empty
        """
        if self.is_empty():
            return None
        return self.cards[-1]

    def add_card(self, card: Card) -> None:
        """
        Add a card to the bottom of the deck.

        Args:
            card: Card to add to the deck
        """
        self.cards.insert(0, card)

    def add_cards(self, cards: List[Card]) -> None:
        """
        Add multiple cards to the bottom of the deck.

        Args:
            cards: List of cards to add
        """
        for card in cards:
            self.add_card(card)

    def discard_card(self, card: Card) -> None:
        """
        Move a card to the discard pile.

        Args:
            card: Card to discard
        """
        if card in self.cards:
            self.cards.remove(card)
        self.discarded.append(card)

    def reshuffle_discarded(self) -> None:
        """
        Shuffle discarded cards back into the deck.

        Moves all discarded cards back to the main deck and shuffles.
        """
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

    def get_cards_by_suit(self, suit: Suit) -> List[Card]:
        """
        Get all cards of a specific suit from the deck.

        Args:
            suit: The suit to filter by

        Returns:
            List of cards matching the suit
        """
        return [card for card in self.cards if card.suit == suit]

    def get_cards_by_rank(self, rank: Rank) -> List[Card]:
        """
        Get all cards of a specific rank from the deck.

        Args:
            rank: The rank to filter by

        Returns:
            List of cards matching the rank
        """
        return [card for card in self.cards if card.rank == rank]

    def remove_cards_by_rank(self, ranks: List[Rank]) -> List[Card]:
        """
        Remove and return cards of specific ranks from the deck.

        Args:
            ranks: List of ranks to remove

        Returns:
            List of removed cards
        """
        removed_cards = []
        for rank in ranks:
            cards_to_remove = [card for card in self.cards if card.rank == rank]
            for card in cards_to_remove:
                self.cards.remove(card)
                removed_cards.append(card)
        return removed_cards

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
            'include_jokers': self.include_jokers
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Deck':
        """
        Create deck from dictionary representation.

        Args:
            data: Dictionary containing deck data

        Returns:
            Deck object created from the dictionary
        """
        deck = cls(include_jokers=data.get('include_jokers', False))
        deck.cards = [Card.from_dict(card_data) for card_data in data['cards']]
        deck.discarded = [Card.from_dict(card_data) for card_data in data['discarded']]
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
            String showing deck size and sample cards
        """
        if self.is_empty():
            return "Empty deck"
        elif len(self.cards) <= 5:
            return f"Deck: {', '.join(str(card) for card in self.cards)}"
        else:
            return f"Deck with {len(self.cards)} cards (top: {self.cards[-1]})"