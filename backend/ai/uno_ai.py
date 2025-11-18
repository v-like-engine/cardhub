"""
Uno AI implementation using strategic card management.

This module implements an AI player for Uno that considers
color strategy, action card timing, and hand optimization.
"""

from typing import Dict, Any, List, Optional
import random

from .base_ai import AIPlayer
from ..game_engine.base_game import BaseGame
from ..game_engine.uno import UnoGame, UnoPlayer
from ..models.uno_card import UnoCard, UnoColor, UnoType


class UnoAI(AIPlayer):
    """
    AI player for Uno using strategic analysis.

    Implements strategic Uno play including color management,
    action card timing, and endgame optimization.
    """

    def __init__(self, difficulty: str = "medium"):
        """
        Initialize Uno AI.

        Args:
            difficulty: AI difficulty level
        """
        super().__init__(difficulty)

    def make_move(self, game: UnoGame, player: UnoPlayer) -> Dict[str, Any]:
        """
        Make a Uno move using strategic analysis.

        Args:
            game: Current Uno game state
            player: The AI player making the move

        Returns:
            Dictionary containing the move to make
        """
        valid_moves = self._filter_valid_moves(game, player)
        if not valid_moves:
            return {'action': 'draw_card'}

        # Handle Uno call
        uno_moves = [move for move in valid_moves if move['action'] == 'call_uno']
        if uno_moves and player.hand_size() == 1:
            return uno_moves[0]

        # Handle Uno challenges
        challenge_moves = [move for move in valid_moves if move['action'] == 'challenge_uno']
        if challenge_moves and self._should_challenge_uno(game, player):
            return random.choice(challenge_moves)

        # Separate play and draw moves
        play_moves = [move for move in valid_moves if move['action'] == 'play_card']
        draw_moves = [move for move in valid_moves if move['action'] == 'draw_card']

        if not play_moves:
            return draw_moves[0] if draw_moves else {'action': 'draw_card'}

        # Evaluate play options
        move_scores = []
        for move in play_moves:
            card = UnoCard.from_dict(move['card'])
            score = self._score_play_move(card, game, player, move)
            move_scores.append(score)

        # Choose best play with some randomness
        best_move = self._choose_best_move(play_moves, move_scores)

        # Add color choice for wild cards
        if best_move and 'color_options' in best_move:
            best_color = self._choose_wild_card_color(player, game)
            best_move['new_color'] = best_color

        return best_move

    def evaluate_position(self, game: UnoGame, player: UnoPlayer) -> float:
        """
        Evaluate the current Uno position.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            Position evaluation score
        """
        score = 0.0

        # Hand size factor (fewer cards is better)
        hand_size_factor = 1.0 - min(player.hand_size() / 15.0, 1.0)
        score += hand_size_factor * 0.4

        # Color distribution
        color_score = self._evaluate_color_distribution(player.uno_cards)
        score += color_score * 0.2

        # Action card strength
        action_score = self._evaluate_action_cards(player.uno_cards)
        score += action_score * 0.2

        # Playability of current hand
        playable_score = self._evaluate_playability(player.uno_cards, game)
        score += playable_score * 0.2

        return min(max(score, 0.0), 1.0)

    def _score_play_move(self, card: UnoCard, game: UnoGame,
                        player: UnoPlayer, move: Dict[str, Any]) -> float:
        """
        Score a card play move.

        Args:
            card: Card being played
            game: Current game state
            player: The AI player
            move: Move data

        Returns:
            Score for playing this card
        """
        score = 0.0

        # Basic playability score
        score += 0.3

        # Prefer getting rid of high-point cards
        points = card.get_points()
        if points >= 20:
            score += 0.3  # High value action cards
        elif points >= 10:
            score += 0.2  # Medium value cards
        else:
            score += 0.1  # Low value number cards

        # Action card strategic value
        if card.is_action_card():
            action_score = self._evaluate_action_card_play(card, game, player)
            score += action_score * 0.4

        # Color strategy
        color_score = self._evaluate_color_play(card, game, player)
        score += color_score * 0.2

        # Hand reduction benefit
        remaining_cards = player.hand_size() - 1
        if remaining_cards == 0:
            score += 1.0  # Winning move!
        elif remaining_cards == 1:
            score += 0.5  # Down to last card
        elif remaining_cards <= 3:
            score += 0.3  # Close to winning

        # Endgame considerations
        if remaining_cards <= 2:
            endgame_score = self._evaluate_endgame_play(card, game, player)
            score += endgame_score * 0.3

        return score

    def _evaluate_action_card_play(self, card: UnoCard, game: UnoGame,
                                  player: UnoPlayer) -> float:
        """
        Evaluate the strategic value of playing an action card.

        Args:
            card: Action card being evaluated
            game: Current game state
            player: The AI player

        Returns:
            Action card play value
        """
        if not card.is_action_card():
            return 0.0

        score = 0.0

        if card.card_type == UnoType.SKIP:
            # Skip next player
            next_player = self._get_next_player(game, player)
            if next_player and next_player.hand_size() <= 2:
                score += 0.8  # High value to skip player close to winning
            else:
                score += 0.4  # Moderate value for disruption

        elif card.card_type == UnoType.REVERSE:
            # Reverse direction
            if len(game.uno_players) == 2:
                # In 2-player game, reverse acts like skip
                score += 0.5
            else:
                # Evaluate based on player positions
                score += 0.3

        elif card.card_type == UnoType.DRAW_TWO:
            # Force next player to draw
            next_player = self._get_next_player(game, player)
            if next_player and next_player.hand_size() <= 3:
                score += 0.9  # Very high value against low-hand players
            else:
                score += 0.6  # Good disruption value

        elif card.card_type == UnoType.WILD_DRAW_FOUR:
            # Powerful disruption + color change
            score += 0.8  # Always valuable

        elif card.card_type == UnoType.WILD:
            # Color change utility
            color_control_value = self._evaluate_color_control_need(player, game)
            score += color_control_value

        return score

    def _evaluate_color_play(self, card: UnoCard, game: UnoGame,
                           player: UnoPlayer) -> float:
        """
        Evaluate color strategy aspects of playing a card.

        Args:
            card: Card being evaluated
            game: Current game state
            player: The AI player

        Returns:
            Color strategy score
        """
        if card.is_wild():
            return 0.3  # Wild cards are always good for color control

        # Count remaining cards of this color
        same_color_count = sum(1 for c in player.uno_cards
                              if c.color == card.color and c != card)

        # Prefer colors we have more of
        if same_color_count >= 3:
            return 0.4
        elif same_color_count >= 2:
            return 0.3
        elif same_color_count >= 1:
            return 0.2
        else:
            return 0.1  # Getting rid of singleton colors

    def _evaluate_endgame_play(self, card: UnoCard, game: UnoGame,
                              player: UnoPlayer) -> float:
        """
        Evaluate endgame considerations for card play.

        Args:
            card: Card being evaluated
            game: Current game state
            player: The AI player

        Returns:
            Endgame strategy score
        """
        remaining_cards = player.hand_size() - 1

        if remaining_cards == 0:
            # This would be the winning play
            return 1.0

        if remaining_cards == 1:
            # Down to last card - consider what's left
            remaining_card = None
            for c in player.uno_cards:
                if c != card:
                    remaining_card = c
                    break

            if remaining_card:
                if remaining_card.is_wild():
                    return 0.8  # Wild card is great as last card
                elif remaining_card.is_action_card():
                    return 0.6  # Action cards can be powerful
                else:
                    return 0.4  # Number cards are okay

        return 0.2

    def _evaluate_color_distribution(self, hand: List[UnoCard]) -> float:
        """
        Evaluate the color distribution in hand.

        Args:
            hand: Player's Uno cards

        Returns:
            Color distribution score
        """
        if not hand:
            return 0.0

        # Count cards by color
        color_counts = {}
        for card in hand:
            if not card.is_wild():
                color = card.color
                color_counts[color] = color_counts.get(color, 0) + 1

        if not color_counts:
            return 0.5  # All wild cards

        # Prefer balanced distribution
        total_colored_cards = sum(color_counts.values())
        if total_colored_cards == 0:
            return 0.5

        # Calculate distribution evenness
        avg_per_color = total_colored_cards / len(color_counts)
        variance = sum((count - avg_per_color) ** 2 for count in color_counts.values())
        variance /= len(color_counts)

        # Lower variance is better (more even distribution)
        return max(0.0, 1.0 - (variance / (avg_per_color + 1)))

    def _evaluate_action_cards(self, hand: List[UnoCard]) -> float:
        """
        Evaluate the strength of action cards in hand.

        Args:
            hand: Player's Uno cards

        Returns:
            Action card strength score
        """
        if not hand:
            return 0.0

        action_cards = [card for card in hand if card.is_action_card()]
        action_count = len(action_cards)

        # Score based on number and type of action cards
        base_score = min(action_count / 5.0, 1.0)  # Normalize

        # Bonus for powerful action cards
        power_bonus = 0.0
        for card in action_cards:
            if card.card_type == UnoType.WILD_DRAW_FOUR:
                power_bonus += 0.3
            elif card.card_type in [UnoType.WILD, UnoType.DRAW_TWO]:
                power_bonus += 0.2
            else:
                power_bonus += 0.1

        return min(base_score + power_bonus, 1.0)

    def _evaluate_playability(self, hand: List[UnoCard], game: UnoGame) -> float:
        """
        Evaluate how many cards in hand are currently playable.

        Args:
            hand: Player's Uno cards
            game: Current game state

        Returns:
            Playability score
        """
        if not hand or not game.discard_pile:
            return 0.5

        top_card = game.discard_pile[-1]
        current_color = game.current_color

        playable_count = 0
        for card in hand:
            if card.can_be_played_on(top_card, current_color):
                playable_count += 1

        return playable_count / len(hand)

    def _evaluate_color_control_need(self, player: UnoPlayer, game: UnoGame) -> float:
        """
        Evaluate how much the player needs color control.

        Args:
            player: The AI player
            game: Current game state

        Returns:
            Color control need score
        """
        if not game.current_color:
            return 0.5

        # Count cards matching current color
        matching_cards = sum(1 for card in player.uno_cards
                           if not card.is_wild() and card.color == game.current_color)

        # If few matching cards, color control is valuable
        if matching_cards == 0:
            return 0.8
        elif matching_cards == 1:
            return 0.6
        elif matching_cards == 2:
            return 0.4
        else:
            return 0.2

    def _choose_wild_card_color(self, player: UnoPlayer, game: UnoGame) -> str:
        """
        Choose the best color when playing a wild card.

        Args:
            player: The AI player
            game: Current game state

        Returns:
            Chosen color name
        """
        # Count cards in each color
        color_counts = {}
        for color in [UnoColor.RED, UnoColor.BLUE, UnoColor.GREEN, UnoColor.YELLOW]:
            color_counts[color] = sum(1 for card in player.uno_cards
                                    if card.color == color)

        # Choose color with most cards
        if color_counts:
            best_color = max(color_counts.keys(), key=lambda c: color_counts[c])

            # Add some randomness for lower difficulties
            if self.difficulty == "easy" and random.random() < 0.3:
                return random.choice([c.value for c in color_counts.keys()])
            elif self.difficulty == "medium" and random.random() < 0.15:
                return random.choice([c.value for c in color_counts.keys()])

            return best_color.value

        # Fallback to random color
        return random.choice(['red', 'blue', 'green', 'yellow'])

    def _should_challenge_uno(self, game: UnoGame, player: UnoPlayer) -> bool:
        """
        Decide whether to challenge another player's Uno call.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            True if should challenge, False otherwise
        """
        # Only challenge if fairly confident and difficulty allows
        challenge_probability = {
            "easy": 0.2,
            "medium": 0.4,
            "hard": 0.6
        }.get(self.difficulty, 0.4)

        return random.random() < challenge_probability

    def _get_next_player(self, game: UnoGame, current_player: UnoPlayer) -> Optional[UnoPlayer]:
        """
        Get the next player in turn order.

        Args:
            game: Current game state
            current_player: Current player

        Returns:
            Next player or None
        """
        try:
            current_index = game.uno_players.index(current_player)
            next_index = (current_index + game.direction) % len(game.uno_players)
            if next_index < 0:
                next_index = len(game.uno_players) - 1
            return game.uno_players[next_index]
        except (ValueError, IndexError):
            return None

    def _filter_valid_moves(self, game: UnoGame, player: UnoPlayer) -> List[Dict[str, Any]]:
        """
        Get and filter valid moves for the Uno player.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            List of valid moves
        """
        return game.get_valid_moves(player.player_id)