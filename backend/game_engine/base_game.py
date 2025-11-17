"""
Base game engine providing common functionality for all card games.

This module defines the abstract base class that all specific card games
inherit from, providing consistent interface and common game mechanics.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
from datetime import datetime

from ..models.card import Card
from ..models.deck import Deck


class GameState(Enum):
    """Enumeration of possible game states."""
    WAITING_FOR_PLAYERS = "waiting_for_players"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class Player:
    """
    Represents a player in the game.

    Contains player information, hand, and game-specific data.
    """

    def __init__(self, player_id: str, name: str, is_ai: bool = False):
        """
        Initialize a new player.

        Args:
            player_id: Unique identifier for the player
            name: Display name of the player
            is_ai: Whether this player is AI-controlled
        """
        self.player_id = player_id
        self.name = name
        self.is_ai = is_ai
        self.hand: List[Card] = []
        self.score = 0
        self.is_active = True
        self.game_data: Dict[str, Any] = {}

    def add_card(self, card: Card) -> None:
        """
        Add a card to the player's hand.

        Args:
            card: Card to add to hand
        """
        self.hand.append(card)

    def remove_card(self, card: Card) -> bool:
        """
        Remove a card from the player's hand.

        Args:
            card: Card to remove

        Returns:
            True if card was removed, False if not found
        """
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False

    def has_card(self, card: Card) -> bool:
        """
        Check if player has a specific card.

        Args:
            card: Card to check for

        Returns:
            True if player has the card, False otherwise
        """
        return card in self.hand

    def hand_size(self) -> int:
        """
        Get the number of cards in hand.

        Returns:
            Number of cards in player's hand
        """
        return len(self.hand)

    def clear_hand(self) -> None:
        """Clear all cards from the player's hand."""
        self.hand.clear()

    def to_dict(self, hide_hand: bool = False) -> Dict[str, Any]:
        """
        Convert player to dictionary representation.

        Args:
            hide_hand: Whether to hide the hand cards (for opponents)

        Returns:
            Dictionary containing player data
        """
        return {
            'player_id': self.player_id,
            'name': self.name,
            'is_ai': self.is_ai,
            'hand': [] if hide_hand else [card.to_dict() for card in self.hand],
            'hand_size': len(self.hand),
            'score': self.score,
            'is_active': self.is_active,
            'game_data': self.game_data
        }


class BaseGame(ABC):
    """
    Abstract base class for all card games.

    Provides common functionality and interface that all games must implement.
    Handles basic game flow, player management, and state tracking.
    """

    def __init__(self, game_id: str = None):
        """
        Initialize a new game instance.

        Args:
            game_id: Unique identifier for the game (auto-generated if None)
        """
        self.game_id = game_id or str(uuid.uuid4())
        self.players: List[Player] = []
        self.deck = Deck()
        self.current_player_index = 0
        self.state = GameState.WAITING_FOR_PLAYERS
        self.winner: Optional[Player] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.finished_at: Optional[datetime] = None
        self.game_data: Dict[str, Any] = {}

    def add_player(self, player_id: str, name: str, is_ai: bool = False) -> Player:
        """
        Add a new player to the game.

        Args:
            player_id: Unique identifier for the player
            name: Display name of the player
            is_ai: Whether this player is AI-controlled

        Returns:
            The created Player object

        Raises:
            ValueError: If game is not waiting for players or player already exists
        """
        if self.state != GameState.WAITING_FOR_PLAYERS:
            raise ValueError("Cannot add players when game is not waiting for players")

        if any(p.player_id == player_id for p in self.players):
            raise ValueError(f"Player {player_id} already exists in game")

        player = Player(player_id, name, is_ai)
        self.players.append(player)
        return player

    def remove_player(self, player_id: str) -> bool:
        """
        Remove a player from the game.

        Args:
            player_id: ID of player to remove

        Returns:
            True if player was removed, False if not found
        """
        for i, player in enumerate(self.players):
            if player.player_id == player_id:
                self.players.pop(i)
                if self.current_player_index >= len(self.players) and self.players:
                    self.current_player_index = 0
                return True
        return False

    def get_player(self, player_id: str) -> Optional[Player]:
        """
        Get a player by ID.

        Args:
            player_id: ID of player to find

        Returns:
            Player object or None if not found
        """
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def get_current_player(self) -> Optional[Player]:
        """
        Get the current active player.

        Returns:
            Current player or None if no players
        """
        if not self.players:
            return None
        return self.players[self.current_player_index]

    def next_player(self) -> None:
        """Move to the next player in turn order."""
        if self.players:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def start_game(self) -> None:
        """
        Start the game.

        Raises:
            ValueError: If not enough players or game already started
        """
        if self.state != GameState.WAITING_FOR_PLAYERS:
            raise ValueError("Game is not in waiting state")

        if not self.can_start():
            raise ValueError("Cannot start game with current player count")

        self.state = GameState.STARTING
        self.started_at = datetime.now()
        self.setup_game()
        self.state = GameState.IN_PROGRESS

    def end_game(self, winner: Optional[Player] = None) -> None:
        """
        End the game.

        Args:
            winner: The winning player (if any)
        """
        self.state = GameState.FINISHED
        self.winner = winner
        self.finished_at = datetime.now()

    def pause_game(self) -> None:
        """Pause the game."""
        if self.state == GameState.IN_PROGRESS:
            self.state = GameState.PAUSED

    def resume_game(self) -> None:
        """Resume a paused game."""
        if self.state == GameState.PAUSED:
            self.state = GameState.IN_PROGRESS

    def cancel_game(self) -> None:
        """Cancel the game."""
        self.state = GameState.CANCELLED
        self.finished_at = datetime.now()

    def to_dict(self, player_perspective: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert game to dictionary representation.

        Args:
            player_perspective: Player ID to show full hand for (others hidden)

        Returns:
            Dictionary containing game state
        """
        return {
            'game_id': self.game_id,
            'state': self.state.value,
            'players': [
                player.to_dict(hide_hand=(player_perspective != player.player_id))
                for player in self.players
            ],
            'current_player': self.current_player_index,
            'winner': self.winner.to_dict() if self.winner else None,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'game_data': self.game_data
        }

    @abstractmethod
    def can_start(self) -> bool:
        """
        Check if the game can be started.

        Returns:
            True if game can start, False otherwise
        """
        pass

    @abstractmethod
    def setup_game(self) -> None:
        """
        Set up the game after players have joined.

        This method should initialize the deck, deal cards,
        and set up any game-specific state.
        """
        pass

    @abstractmethod
    def make_move(self, player_id: str, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a move by a player.

        Args:
            player_id: ID of player making the move
            move_data: Data describing the move

        Returns:
            Result of the move including any state changes

        Raises:
            ValueError: If move is invalid
        """
        pass

    @abstractmethod
    def get_valid_moves(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get all valid moves for a player.

        Args:
            player_id: ID of player to get moves for

        Returns:
            List of valid move descriptions
        """
        pass

    @abstractmethod
    def check_win_condition(self) -> Optional[Player]:
        """
        Check if any player has won the game.

        Returns:
            Winning player or None if no winner yet
        """
        pass

    @abstractmethod
    def get_game_rules(self) -> Dict[str, Any]:
        """
        Get the rules and configuration for this game type.

        Returns:
            Dictionary containing game rules and settings
        """
        pass