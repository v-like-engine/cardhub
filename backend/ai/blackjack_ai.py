"""
BlackJack AI implementation using basic strategy.

This module implements an AI player for BlackJack that follows
basic strategy charts with difficulty-based variations.
"""

from typing import Dict, Any, List, Optional
import random

from .base_ai import AIPlayer
from ..game_engine.base_game import BaseGame, Player
from ..game_engine.blackjack import BlackjackGame


class BlackjackAI(AIPlayer):
    """
    AI player for BlackJack using basic strategy.

    Implements optimal BlackJack strategy with variations based on
    difficulty level and situational awareness.
    """

    def __init__(self, difficulty: str = "medium"):
        """
        Initialize BlackJack AI.

        Args:
            difficulty: AI difficulty level
        """
        super().__init__(difficulty)
        self.basic_strategy = self._load_basic_strategy()

    def make_move(self, game: BlackjackGame, player: Player) -> Dict[str, Any]:
        """
        Make a BlackJack move using basic strategy.

        Args:
            game: Current BlackJack game state
            player: The AI player making the move

        Returns:
            Dictionary containing the move to make
        """
        valid_moves = self._filter_valid_moves(game, player)
        if not valid_moves:
            return {'action': 'stand'}

        # Get dealer's upcard
        dealer = game.get_player("dealer")
        if not dealer or len(dealer.hand) == 0:
            # Fallback to conservative play
            return {'action': 'stand'}

        dealer_upcard = dealer.hand[0]
        player_hand_value = game.calculate_hand_value(player.hand)

        # Check for soft hand (has Ace counted as 11)
        has_ace = any(card.rank.name == 'ACE' for card in player.hand)
        is_soft = has_ace and player_hand_value <= 21

        # Apply basic strategy
        action = self._get_basic_strategy_action(
            player_hand_value,
            dealer_upcard.rank.value,
            is_soft,
            len(player.hand) == 2
        )

        # Apply difficulty-based variations
        action = self._apply_difficulty_variation(action, player_hand_value, dealer_upcard.rank.value)

        return {'action': action}

    def evaluate_position(self, game: BlackjackGame, player: Player) -> float:
        """
        Evaluate the current BlackJack position.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            Position evaluation score
        """
        if not player.hand:
            return 0.0

        hand_value = game.calculate_hand_value(player.hand)

        # Busted hands are worst
        if hand_value > 21:
            return -1.0

        # BlackJack is best
        if len(player.hand) == 2 and hand_value == 21:
            return 1.0

        # Evaluate based on hand strength
        if hand_value >= 17:
            return 0.8
        elif hand_value >= 15:
            return 0.6
        elif hand_value >= 12:
            return 0.4
        else:
            return 0.2

    def _load_basic_strategy(self) -> Dict[str, Dict[int, str]]:
        """
        Load basic BlackJack strategy charts.

        Returns:
            Dictionary containing strategy decisions
        """
        # Hard totals strategy (no Ace or Ace counted as 1)
        hard_strategy = {
            # Player total: {dealer_upcard: action}
            21: {i: 'stand' for i in range(2, 12)},
            20: {i: 'stand' for i in range(2, 12)},
            19: {i: 'stand' for i in range(2, 12)},
            18: {i: 'stand' for i in range(2, 12)},
            17: {i: 'stand' for i in range(2, 12)},
            16: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand',
                 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            15: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand',
                 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            14: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand',
                 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            13: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand',
                 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            12: {2: 'hit', 3: 'hit', 4: 'stand', 5: 'stand', 6: 'stand',
                 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            11: {i: 'double_down' for i in range(2, 12)},
            10: {2: 'double_down', 3: 'double_down', 4: 'double_down', 5: 'double_down',
                 6: 'double_down', 7: 'double_down', 8: 'double_down', 9: 'double_down',
                 10: 'hit', 11: 'hit'},
            9: {3: 'double_down', 4: 'double_down', 5: 'double_down', 6: 'double_down',
                2: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
        }

        # Add default hit for lower totals
        for total in range(5, 9):
            hard_strategy[total] = {i: 'hit' for i in range(2, 12)}

        # Soft totals strategy (Ace counted as 11)
        soft_strategy = {
            # Soft 19 (A,8) and Soft 20 (A,9)
            20: {i: 'stand' for i in range(2, 12)},
            19: {i: 'stand' for i in range(2, 12)},
            # Soft 18 (A,7)
            18: {2: 'stand', 3: 'double_down', 4: 'double_down', 5: 'double_down',
                 6: 'double_down', 7: 'stand', 8: 'stand', 9: 'hit', 10: 'hit', 11: 'hit'},
            # Soft 17 (A,6)
            17: {3: 'double_down', 4: 'double_down', 5: 'double_down', 6: 'double_down',
                 2: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # Soft 16 (A,5)
            16: {4: 'double_down', 5: 'double_down', 6: 'double_down',
                 2: 'hit', 3: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # Soft 15 (A,4)
            15: {4: 'double_down', 5: 'double_down', 6: 'double_down',
                 2: 'hit', 3: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # Soft 14 (A,3)
            14: {5: 'double_down', 6: 'double_down',
                 2: 'hit', 3: 'hit', 4: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # Soft 13 (A,2)
            13: {5: 'double_down', 6: 'double_down',
                 2: 'hit', 3: 'hit', 4: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
        }

        return {
            'hard': hard_strategy,
            'soft': soft_strategy
        }

    def _get_basic_strategy_action(self, player_total: int, dealer_upcard: int,
                                   is_soft: bool, can_double: bool) -> str:
        """
        Get the basic strategy action for given situation.

        Args:
            player_total: Player's hand total
            dealer_upcard: Dealer's upcard value
            is_soft: Whether player hand is soft
            can_double: Whether doubling down is allowed

        Returns:
            Recommended action
        """
        # Convert face cards to 10 for strategy lookup
        if dealer_upcard > 10:
            dealer_upcard = 10

        strategy_type = 'soft' if is_soft else 'hard'
        strategy = self.basic_strategy.get(strategy_type, {})

        # Get action from strategy chart
        if player_total in strategy and dealer_upcard in strategy[player_total]:
            action = strategy[player_total][dealer_upcard]

            # If can't double down, convert to hit
            if action == 'double_down' and not can_double:
                action = 'hit'

            return action

        # Default fallback
        if player_total >= 17:
            return 'stand'
        else:
            return 'hit'

    def _apply_difficulty_variation(self, optimal_action: str, player_total: int,
                                    dealer_upcard: int) -> str:
        """
        Apply difficulty-based variations to the optimal action.

        Args:
            optimal_action: The optimal basic strategy action
            player_total: Player's hand total
            dealer_upcard: Dealer's upcard value

        Returns:
            Modified action based on difficulty
        """
        if self.difficulty == "hard":
            # Hard AI plays perfectly
            return optimal_action

        # Calculate mistake probability based on difficulty
        mistake_probability = {
            "easy": 0.25,
            "medium": 0.10
        }.get(self.difficulty, 0.0)

        if random.random() < mistake_probability:
            return self._make_suboptimal_move(optimal_action, player_total, dealer_upcard)

        return optimal_action

    def _make_suboptimal_move(self, optimal_action: str, player_total: int,
                             dealer_upcard: int) -> str:
        """
        Make a suboptimal move for lower difficulty levels.

        Args:
            optimal_action: The optimal action
            player_total: Player's hand total
            dealer_upcard: Dealer's upcard value

        Returns:
            Suboptimal action
        """
        # Common beginner mistakes
        if self.difficulty == "easy":
            # Easy AI makes more obvious mistakes
            if player_total == 16 and dealer_upcard >= 7:
                # Sometimes stands on 16 vs dealer's high card (mistake)
                if random.random() < 0.3:
                    return 'stand'

            if player_total == 12 and dealer_upcard in [2, 3]:
                # Sometimes hits 12 vs dealer's low card (mistake)
                if random.random() < 0.4:
                    return 'hit'

            if player_total == 11:
                # Sometimes doesn't double on 11 (conservative mistake)
                if random.random() < 0.2:
                    return 'hit'

        elif self.difficulty == "medium":
            # Medium AI makes subtle mistakes
            if player_total in [15, 16] and dealer_upcard in [7, 8, 9]:
                # Occasionally makes wrong borderline decisions
                if random.random() < 0.15:
                    return 'stand' if optimal_action == 'hit' else 'hit'

        return optimal_action

    def _count_cards(self, visible_cards: List) -> int:
        """
        Simple card counting for advanced difficulty.

        Args:
            visible_cards: List of visible cards

        Returns:
            Running count
        """
        if self.difficulty != "hard":
            return 0

        count = 0
        for card in visible_cards:
            value = card.rank.value
            if value <= 6:
                count += 1
            elif value >= 10:
                count -= 1

        return count

    def _adjust_for_count(self, action: str, count: int, player_total: int) -> str:
        """
        Adjust action based on card count (for hard difficulty).

        Args:
            action: Basic strategy action
            count: Current card count
            player_total: Player's hand total

        Returns:
            Adjusted action
        """
        if self.difficulty != "hard" or count == 0:
            return action

        # High positive count favors aggressive play
        if count >= 3:
            if action == 'hit' and player_total == 16:
                return 'stand'  # Stand on 16 with high count
            if action == 'stand' and player_total == 12:
                return 'hit'    # Hit 12 with high count

        # High negative count favors conservative play
        elif count <= -3:
            if action == 'double_down':
                return 'hit'    # Don't double with negative count
            if action == 'stand' and player_total == 13:
                return 'hit'    # Hit 13 with negative count

        return action