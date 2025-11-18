"""
101 AI implementation using strategic scoring and risk management.

This module implements an AI player for 101 that manages
point accumulation, special card effects, and endgame timing.
"""

from typing import Dict, Any, List, Optional
import random

from .base_ai import AIPlayer
from ..game_engine.base_game import BaseGame, Player
from ..game_engine.one_hundred_one import OneHundredOneGame
from ..models.card import Card, Rank, Suit


class OneHundredOneAI(AIPlayer):
    """
    AI player for 101 using strategic point management.

    Implements strategic 101 play including point optimization,
    special card timing, and risk assessment.
    """

    def __init__(self, difficulty: str = "medium"):
        """
        Initialize 101 AI.

        Args:
            difficulty: AI difficulty level
        """
        super().__init__(difficulty)

    def make_move(self, game: OneHundredOneGame, player: Player) -> Dict[str, Any]:
        """
        Make a 101 move using strategic analysis.

        Args:
            game: Current 101 game state
            player: The AI player making the move

        Returns:
            Dictionary containing the move to make
        """
        valid_moves = self._filter_valid_moves(game, player)
        if not valid_moves:
            return {'action': 'draw_card'}

        # Check if can declare 101
        declare_moves = [move for move in valid_moves if move['action'] == 'declare_101']
        if declare_moves:
            return declare_moves[0]

        # Separate play and draw moves
        play_moves = [move for move in valid_moves if move['action'] == 'play_card']
        draw_moves = [move for move in valid_moves if move['action'] == 'draw_card']

        if not play_moves:
            return draw_moves[0] if draw_moves else {'action': 'draw_card'}

        # Evaluate play options
        move_scores = []
        for move in play_moves:
            card = Card.from_dict(move['card'])
            score = self._score_play_move(card, game, player, move)
            move_scores.append(score)

        # Evaluate draw option
        draw_score = self._score_draw_move(game, player)

        # Compare best play vs draw
        best_play_score = max(move_scores) if move_scores else 0.0
        best_play_index = move_scores.index(best_play_score) if move_scores else 0

        # Decision threshold based on difficulty
        play_threshold = {
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.7
        }.get(self.difficulty, 0.5)

        if best_play_score > draw_score and best_play_score > play_threshold:
            return play_moves[best_play_index]
        else:
            return draw_moves[0] if draw_moves else {'action': 'draw_card'}

    def evaluate_position(self, game: OneHundredOneGame, player: Player) -> float:
        """
        Evaluate the current 101 position.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            Position evaluation score
        """
        score = 0.0

        # Score based on distance to 101
        target_distance = abs(101 - player.score)
        if target_distance == 0:
            return 1.0  # Perfect score

        # Closer to 101 is better, but over 101 is worst
        if player.score > 101:
            return 0.0  # Busted

        distance_score = max(0, 1.0 - (target_distance / 101.0))
        score += distance_score * 0.5

        # Hand quality evaluation
        hand_score = self._evaluate_hand_quality(player.hand, game)
        score += hand_score * 0.3

        # Strategic position (special cards, timing)
        strategic_score = self._evaluate_strategic_position(player, game)
        score += strategic_score * 0.2

        return min(max(score, 0.0), 1.0)

    def _score_play_move(self, card: Card, game: OneHundredOneGame,
                        player: Player, move: Dict[str, Any]) -> float:
        """
        Score a card play move.

        Args:
            card: Card being played
            game: Current game state
            player: The AI player
            move: Move data including points

        Returns:
            Score for playing this card
        """
        score = 0.0
        points = move.get('points', 0)
        new_score = player.score + points

        # Evaluate target achievement
        if new_score == 101:
            return 1.0  # Perfect score!

        if new_score > 101:
            return 0.0  # Bust - avoid at all costs

        # Score based on how close we get to 101
        distance_to_target = 101 - new_score
        if distance_to_target <= 10:
            # Close to target - evaluate carefully
            score += (10 - distance_to_target) / 10.0 * 0.6
        else:
            # Far from target - steady progress
            score += min(points / 20.0, 0.4)  # Normalize points contribution

        # Special card evaluation
        special_score = self._evaluate_special_card_play(card, game, player)
        score += special_score * 0.3

        # Risk assessment
        risk_score = self._assess_play_risk(card, new_score, game, player)
        score += risk_score * 0.1

        return score

    def _score_draw_move(self, game: OneHundredOneGame, player: Player) -> float:
        """
        Score the draw card move.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            Score for drawing a card
        """
        # Base score for drawing (getting more options)
        base_score = 0.3

        # Higher score if no good plays available
        if len(player.hand) <= 2:
            base_score += 0.2

        # Lower score if close to winning
        if player.score >= 90:
            base_score -= 0.1

        # Consider hand quality
        if self._evaluate_hand_quality(player.hand, game) < 0.3:
            base_score += 0.2

        return base_score

    def _evaluate_hand_quality(self, hand: List[Card], game: OneHundredOneGame) -> float:
        """
        Evaluate the quality of cards in hand.

        Args:
            hand: Player's hand
            game: Current game state

        Returns:
            Hand quality score
        """
        if not hand:
            return 0.0

        total_score = 0.0

        for card in hand:
            card_score = 0.0

            # Point value consideration
            points = self._get_card_points(card)
            if points <= 5:
                card_score += 0.8  # Low point cards are flexible
            elif points <= 10:
                card_score += 0.6  # Medium point cards are decent
            else:
                card_score += 0.4  # High point cards are risky but powerful

            # Special card bonus
            if self._is_special_card(card):
                card_score += 0.3

            # Playability (can it be played now?)
            if self._can_play_on_current_pile(card, game):
                card_score += 0.2

            total_score += card_score

        return total_score / len(hand)

    def _evaluate_strategic_position(self, player: Player,
                                   game: OneHundredOneGame) -> float:
        """
        Evaluate strategic position factors.

        Args:
            player: The AI player
            game: Current game state

        Returns:
            Strategic position score
        """
        score = 0.0

        # Count special cards
        special_cards = sum(1 for card in player.hand if self._is_special_card(card))
        score += min(special_cards / 3.0, 1.0) * 0.4

        # Evaluate timing relative to opponents
        opponents_close = 0
        for opponent in game.players:
            if opponent != player and opponent.score >= 90:
                opponents_close += 1

        if opponents_close > 0:
            # Need to be more aggressive
            if player.score >= 85:
                score += 0.3
            else:
                score -= 0.2

        # Hand size consideration
        ideal_hand_size = 4
        hand_size_diff = abs(len(player.hand) - ideal_hand_size)
        score += max(0, 1.0 - (hand_size_diff / 3.0)) * 0.3

        return score

    def _evaluate_special_card_play(self, card: Card, game: OneHundredOneGame,
                                   player: Player) -> float:
        """
        Evaluate the strategic value of playing a special card.

        Args:
            card: Card being evaluated
            game: Current game state
            player: The AI player

        Returns:
            Special card play value
        """
        if not self._is_special_card(card):
            return 0.0

        score = 0.0

        if card.rank == Rank.EIGHT:
            # Skip card - evaluate based on opponent positions
            next_player_index = (game.current_player_index + 1) % len(game.players)
            next_player = game.players[next_player_index]

            if next_player.score >= 90:
                score += 0.7  # High value to skip player close to winning
            else:
                score += 0.3  # Moderate value for disruption

        elif card.rank == Rank.KING:
            # Reverse card - evaluate based on player positions
            if len(game.players) > 2:
                # More effective with more players
                score += 0.4
            else:
                score += 0.2

        elif card.rank == Rank.JACK:
            # Wild card - evaluate based on color change needs
            current_color = game.current_suit
            if current_color:
                # Value depends on hand composition
                same_suit_cards = sum(1 for c in player.hand if c.suit == current_color)
                if same_suit_cards <= 1:
                    score += 0.6  # High value if can't match current suit
                else:
                    score += 0.3  # Moderate value for flexibility

        return score

    def _assess_play_risk(self, card: Card, new_score: int,
                         game: OneHundredOneGame, player: Player) -> float:
        """
        Assess the risk of playing a specific card.

        Args:
            card: Card being played
            new_score: Score after playing the card
            game: Current game state
            player: The AI player

        Returns:
            Risk assessment score (higher = less risky)
        """
        risk_score = 0.5  # Neutral baseline

        # Distance from bust
        distance_from_bust = 101 - new_score
        if distance_from_bust >= 20:
            risk_score += 0.3  # Safe distance
        elif distance_from_bust >= 10:
            risk_score += 0.1  # Moderate safety
        else:
            risk_score -= 0.2  # Risky territory

        # Consider remaining cards in hand
        remaining_cards = len(player.hand) - 1  # After playing this card
        if remaining_cards >= 3:
            risk_score += 0.1  # More options remaining
        elif remaining_cards <= 1:
            risk_score -= 0.1  # Few options left

        # Special card considerations
        if self._is_special_card(card):
            risk_score += 0.1  # Special cards often worth the risk

        return max(0.0, min(1.0, risk_score))

    def _get_card_points(self, card: Card) -> int:
        """Get point value of a card."""
        if card.rank == Rank.ACE:
            return 11
        elif card.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
            return 10
        else:
            return card.rank.value

    def _is_special_card(self, card: Card) -> bool:
        """Check if card has special effects."""
        return card.rank in [Rank.EIGHT, Rank.JACK, Rank.KING]

    def _can_play_on_current_pile(self, card: Card, game: OneHundredOneGame) -> bool:
        """
        Check if card can be played on current discard pile.

        Args:
            card: Card to check
            game: Current game state

        Returns:
            True if card can be played
        """
        if not game.discard_pile:
            return True

        top_card = game.discard_pile[-1]

        # Jack can always be played
        if card.rank == Rank.JACK:
            return True

        # Must match suit or rank
        return (card.suit == game.current_suit or
                card.rank == top_card.rank)

    def _choose_wild_card_suit(self, player: Player, game: OneHundredOneGame) -> str:
        """
        Choose the best suit when playing a Jack (wild card).

        Args:
            player: The AI player
            game: Current game state

        Returns:
            Chosen suit name
        """
        # Count cards in each suit
        suit_counts = {}
        for suit in Suit:
            suit_counts[suit] = sum(1 for card in player.hand
                                  if card.suit == suit and card.rank != Rank.JACK)

        # Choose suit with most cards
        if suit_counts:
            best_suit = max(suit_counts.keys(), key=lambda s: suit_counts[s])
            return best_suit.name.lower()

        # Fallback to random suit
        return random.choice([suit.name.lower() for suit in Suit])