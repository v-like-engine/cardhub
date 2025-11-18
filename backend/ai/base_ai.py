"""
Base AI class for card game artificial intelligence.

This module provides the abstract base class that all game-specific
AI implementations inherit from, ensuring consistent interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import random

from ..game_engine.base_game import BaseGame, Player


class AIPlayer(ABC):
    """
    Abstract base class for AI players in card games.

    Provides common functionality and interface that all AI implementations
    must follow for consistent behavior across different games.
    """

    def __init__(self, difficulty: str = "medium"):
        """
        Initialize AI player.

        Args:
            difficulty: AI difficulty level ("easy", "medium", "hard")
        """
        self.difficulty = difficulty
        self.decision_time_base = self._get_decision_time()
        self.randomness_factor = self._get_randomness_factor()

    def _get_decision_time(self) -> float:
        """
        Get base decision time based on difficulty.

        Returns:
            Decision time in seconds
        """
        return {
            "easy": 1.5,
            "medium": 1.0,
            "hard": 0.5
        }.get(self.difficulty, 1.0)

    def _get_randomness_factor(self) -> float:
        """
        Get randomness factor for decision making.

        Returns:
            Randomness factor (0.0 = deterministic, 1.0 = very random)
        """
        return {
            "easy": 0.3,
            "medium": 0.15,
            "hard": 0.05
        }.get(self.difficulty, 0.15)

    @abstractmethod
    def make_move(self, game: BaseGame, player: Player) -> Dict[str, Any]:
        """
        Make a move in the game.

        Args:
            game: Current game state
            player: The AI player making the move

        Returns:
            Dictionary containing the move to make
        """
        pass

    @abstractmethod
    def evaluate_position(self, game: BaseGame, player: Player) -> float:
        """
        Evaluate the current game position for the AI player.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            Position evaluation score (higher = better for AI)
        """
        pass

    def add_randomness(self, choices: List[Any], scores: List[float]) -> Any:
        """
        Add randomness to decision making based on difficulty.

        Args:
            choices: List of possible choices
            scores: Corresponding scores for each choice

        Returns:
            Selected choice with applied randomness
        """
        if not choices or not scores:
            return None

        if len(choices) == 1:
            return choices[0]

        # Apply randomness based on difficulty
        if random.random() < self.randomness_factor:
            # Make a random choice
            return random.choice(choices)

        # Choose best option with some noise
        if self.randomness_factor > 0:
            # Add noise to scores
            noisy_scores = [
                score + random.uniform(-self.randomness_factor, self.randomness_factor)
                for score in scores
            ]
            best_index = noisy_scores.index(max(noisy_scores))
        else:
            # Pure best choice
            best_index = scores.index(max(scores))

        return choices[best_index]

    def simulate_delay(self) -> float:
        """
        Simulate thinking time for more realistic AI behavior.

        Returns:
            Delay time in seconds
        """
        base_time = self.decision_time_base
        variation = random.uniform(0.5, 1.5)
        return base_time * variation

    def _filter_valid_moves(self, game: BaseGame, player: Player) -> List[Dict[str, Any]]:
        """
        Get and filter valid moves for the player.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            List of valid moves
        """
        return game.get_valid_moves(player.player_id)

    def _choose_best_move(self, moves: List[Dict[str, Any]], scores: List[float]) -> Dict[str, Any]:
        """
        Choose the best move from available options.

        Args:
            moves: List of possible moves
            scores: Corresponding scores for each move

        Returns:
            Selected move
        """
        if not moves:
            raise ValueError("No moves available")

        return self.add_randomness(moves, scores)

    def get_difficulty_modifier(self, base_value: float) -> float:
        """
        Apply difficulty modifier to a base value.

        Args:
            base_value: Base value to modify

        Returns:
            Modified value based on AI difficulty
        """
        modifiers = {
            "easy": 0.7,
            "medium": 1.0,
            "hard": 1.3
        }
        return base_value * modifiers.get(self.difficulty, 1.0)

    def should_make_aggressive_move(self) -> bool:
        """
        Determine if AI should make an aggressive move.

        Returns:
            True if should be aggressive, False otherwise
        """
        aggression_levels = {
            "easy": 0.2,
            "medium": 0.4,
            "hard": 0.6
        }
        threshold = aggression_levels.get(self.difficulty, 0.4)
        return random.random() < threshold

    def calculate_risk_reward(self, risk: float, reward: float) -> float:
        """
        Calculate risk-reward score for a potential move.

        Args:
            risk: Risk factor (0.0 = no risk, 1.0 = high risk)
            reward: Reward factor (0.0 = no reward, 1.0 = high reward)

        Returns:
            Risk-reward score
        """
        risk_tolerance = {
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.7
        }.get(self.difficulty, 0.5)

        # Calculate weighted score
        risk_weight = 1.0 - risk_tolerance
        reward_weight = risk_tolerance

        return (reward * reward_weight) - (risk * risk_weight)

    def __str__(self) -> str:
        """String representation of the AI player."""
        return f"AI Player (Difficulty: {self.difficulty})"