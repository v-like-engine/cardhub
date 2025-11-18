"""
Fool (Durak) AI implementation using strategic play.

This module implements an AI player for Fool that considers
trump cards, hand management, and defensive strategies.
"""

from typing import Dict, Any, List, Optional, Tuple
import random

from .base_ai import AIPlayer
from ..game_engine.base_game import BaseGame, Player
from ..game_engine.fool import FoolGame
from ..models.card import Card, Suit, Rank


class FoolAI(AIPlayer):
    """
    AI player for Fool using strategic analysis.

    Implements strategic Fool play including trump management,
    defensive tactics, and endgame optimization.
    """

    def __init__(self, difficulty: str = "medium"):
        """
        Initialize Fool AI.

        Args:
            difficulty: AI difficulty level
        """
        super().__init__(difficulty)

    def make_move(self, game: FoolGame, player: Player) -> Dict[str, Any]:
        """
        Make a Fool move using strategic analysis.

        Args:
            game: Current Fool game state
            player: The AI player making the move

        Returns:
            Dictionary containing the move to make
        """
        valid_moves = self._filter_valid_moves(game, player)
        if not valid_moves:
            return {'action': 'pass_turn'}

        # Determine player's role in current turn
        player_index = next((i for i, p in enumerate(game.players) if p.player_id == player.player_id), -1)

        if player_index == game.current_attacker_index and game.attacking_phase:
            return self._make_attack_move(game, player, valid_moves)
        elif player_index == game.current_defender_index and not game.attacking_phase:
            return self._make_defense_move(game, player, valid_moves)
        else:
            return {'action': 'pass_turn'}

    def evaluate_position(self, game: FoolGame, player: Player) -> float:
        """
        Evaluate the current Fool position.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            Position evaluation score
        """
        score = 0.0

        # Hand size factor (fewer cards is better)
        hand_size_factor = 1.0 - (len(player.hand) / 20.0)  # Normalize to 0-1
        score += hand_size_factor * 0.4

        # Trump card evaluation
        trump_score = self._evaluate_trump_cards(player.hand, game.trump_suit)
        score += trump_score * 0.3

        # High card strength
        high_card_score = self._evaluate_high_cards(player.hand, game.trump_suit)
        score += high_card_score * 0.2

        # Defensive capability
        defensive_score = self._evaluate_defensive_capability(player.hand, game.trump_suit)
        score += defensive_score * 0.1

        return min(max(score, 0.0), 1.0)

    def _make_attack_move(self, game: FoolGame, player: Player,
                         valid_moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Make an attacking move.

        Args:
            game: Current game state
            player: The AI player
            valid_moves: List of valid moves

        Returns:
            Selected attack move
        """
        attack_moves = [move for move in valid_moves if move['action'] == 'attack']
        if not attack_moves:
            return {'action': 'pass_turn'}

        # Score each attack option
        move_scores = []
        for move in attack_moves:
            card = Card.from_dict(move['card'])
            score = self._score_attack_card(card, game, player)
            move_scores.append(score)

        # Choose best attack with some randomness
        best_move = self._choose_best_move(attack_moves, move_scores)
        return best_move

    def _make_defense_move(self, game: FoolGame, player: Player,
                          valid_moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Make a defensive move.

        Args:
            game: Current game state
            player: The AI player
            valid_moves: List of valid moves

        Returns:
            Selected defense move
        """
        defend_moves = [move for move in valid_moves if move['action'] == 'defend']
        pickup_moves = [move for move in valid_moves if move['action'] == 'pick_up']

        # If no defense options, must pick up
        if not defend_moves:
            return pickup_moves[0] if pickup_moves else {'action': 'pick_up'}

        # Evaluate whether to defend or pick up
        defense_value = self._evaluate_defense_options(defend_moves, game, player)
        pickup_cost = self._evaluate_pickup_cost(game, player)

        # Decision threshold based on difficulty
        decision_threshold = {
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.7
        }.get(self.difficulty, 0.5)

        if defense_value > pickup_cost and defense_value > decision_threshold:
            # Choose best defense
            move_scores = []
            for move in defend_moves:
                card = Card.from_dict(move['card'])
                score = self._score_defense_card(card, game, player)
                move_scores.append(score)

            best_move = self._choose_best_move(defend_moves, move_scores)
            return best_move
        else:
            # Pick up cards
            return pickup_moves[0] if pickup_moves else {'action': 'pick_up'}

    def _score_attack_card(self, card: Card, game: FoolGame, player: Player) -> float:
        """
        Score an attack card option.

        Args:
            card: Card being considered for attack
            game: Current game state
            player: The AI player

        Returns:
            Score for using this card to attack
        """
        score = 0.0

        # Prefer lower value cards for attack
        base_value = card.rank.value
        if card.suit == game.trump_suit:
            base_value += 13  # Trump cards are more valuable

        score += (20 - base_value) / 20.0  # Invert so lower is better

        # Avoid wasting high trump cards early
        if card.suit == game.trump_suit and card.rank.value >= 12:
            score -= 0.3

        # Prefer cards that give defender fewer options
        defender_trump_count = self._estimate_defender_trumps(game)
        if card.suit != game.trump_suit and defender_trump_count > 2:
            score += 0.2  # Non-trump attacks when defender has many trumps

        # Consider hand size - be more aggressive when hand is small
        if len(player.hand) <= 3:
            score += 0.2

        return score

    def _score_defense_card(self, card: Card, game: FoolGame, player: Player) -> float:
        """
        Score a defense card option.

        Args:
            card: Card being considered for defense
            game: Current game state
            player: The AI player

        Returns:
            Score for using this card to defend
        """
        score = 0.0

        # Find the attack card being defended against
        attack_card = None
        for attack, defense in game.table_cards:
            if defense is None:
                attack_card = attack
                break

        if not attack_card:
            return 0.0

        # Prefer minimal defense (just enough to beat attack)
        if card.suit == attack_card.suit:
            # Same suit - prefer lowest card that beats attack
            if card.rank.value > attack_card.rank.value:
                rank_diff = card.rank.value - attack_card.rank.value
                score += (15 - rank_diff) / 15.0  # Prefer smaller differences
        elif card.suit == game.trump_suit and attack_card.suit != game.trump_suit:
            # Trump vs non-trump - prefer lowest trump
            score += (15 - card.rank.value) / 15.0

        # Avoid wasting high trumps
        if card.suit == game.trump_suit and card.rank.value >= 12:
            score -= 0.4

        # Consider hand composition
        trump_count = sum(1 for c in player.hand if c.suit == game.trump_suit)
        if trump_count > 4 and card.suit == game.trump_suit:
            score += 0.1  # More willing to use trumps if have many

        return score

    def _evaluate_defense_options(self, defend_moves: List[Dict[str, Any]],
                                 game: FoolGame, player: Player) -> float:
        """
        Evaluate the value of defending vs picking up.

        Args:
            defend_moves: Available defense moves
            game: Current game state
            player: The AI player

        Returns:
            Defense value score
        """
        if not defend_moves:
            return 0.0

        # Find best defense option
        best_score = 0.0
        for move in defend_moves:
            card = Card.from_dict(move['card'])
            score = self._score_defense_card(card, game, player)
            best_score = max(best_score, score)

        return best_score

    def _evaluate_pickup_cost(self, game: FoolGame, player: Player) -> float:
        """
        Evaluate the cost of picking up cards.

        Args:
            game: Current game state
            player: The AI player

        Returns:
            Pickup cost score (lower is better)
        """
        # Count cards that would be picked up
        cards_to_pickup = len(game.table_cards) * 2  # Each pair has 2 cards max

        # Base cost increases with number of cards
        cost = cards_to_pickup / 10.0

        # Higher cost if hand is already large
        if len(player.hand) > 8:
            cost += 0.3

        # Lower cost if cards might be useful
        useful_cards = 0
        for attack_card, defense_card in game.table_cards:
            if attack_card.suit == game.trump_suit:
                useful_cards += 1
            if defense_card and defense_card.suit == game.trump_suit:
                useful_cards += 1

        cost -= useful_cards * 0.05

        return max(cost, 0.0)

    def _evaluate_trump_cards(self, hand: List[Card], trump_suit: Optional[Suit]) -> float:
        """
        Evaluate the strength of trump cards in hand.

        Args:
            hand: Player's hand
            trump_suit: Current trump suit

        Returns:
            Trump strength score
        """
        if not trump_suit:
            return 0.0

        trump_cards = [card for card in hand if card.suit == trump_suit]
        if not trump_cards:
            return 0.0

        # Score based on number and quality of trumps
        trump_count = len(trump_cards)
        avg_trump_value = sum(card.rank.value for card in trump_cards) / trump_count

        count_score = min(trump_count / 6.0, 1.0)  # Normalize to 0-1
        quality_score = avg_trump_value / 14.0     # Normalize to 0-1

        return (count_score + quality_score) / 2.0

    def _evaluate_high_cards(self, hand: List[Card], trump_suit: Optional[Suit]) -> float:
        """
        Evaluate the strength of high non-trump cards.

        Args:
            hand: Player's hand
            trump_suit: Current trump suit

        Returns:
            High card strength score
        """
        high_cards = [card for card in hand
                     if card.rank.value >= 11 and card.suit != trump_suit]

        if not high_cards:
            return 0.0

        # Score based on number and value of high cards
        high_count = len(high_cards)
        avg_value = sum(card.rank.value for card in high_cards) / high_count

        count_score = min(high_count / 4.0, 1.0)  # Normalize
        value_score = (avg_value - 11) / 3.0      # Kings/Queens/Jacks

        return (count_score + value_score) / 2.0

    def _evaluate_defensive_capability(self, hand: List[Card],
                                     trump_suit: Optional[Suit]) -> float:
        """
        Evaluate the hand's defensive capability.

        Args:
            hand: Player's hand
            trump_suit: Current trump suit

        Returns:
            Defensive capability score
        """
        # Count cards that can defend common attacks
        defensive_cards = 0

        # Trump cards are good for defense
        trump_count = sum(1 for card in hand if card.suit == trump_suit)
        defensive_cards += trump_count

        # High cards in each suit
        suits = {}
        for card in hand:
            if card.suit != trump_suit:
                if card.suit not in suits:
                    suits[card.suit] = []
                suits[card.suit].append(card.rank.value)

        for suit_cards in suits.values():
            # Count high cards in each suit
            high_in_suit = sum(1 for value in suit_cards if value >= 10)
            defensive_cards += high_in_suit

        return min(defensive_cards / 8.0, 1.0)  # Normalize

    def _estimate_defender_trumps(self, game: FoolGame) -> int:
        """
        Estimate how many trump cards the defender has.

        Args:
            game: Current game state

        Returns:
            Estimated trump count
        """
        defender = game.players[game.current_defender_index]
        hand_size = len(defender.hand)

        # Simple estimation based on hand size and cards seen
        # This is a rough heuristic for AI decision making
        estimated_trumps = max(1, hand_size // 4)

        # Adjust based on difficulty (higher difficulty = better estimation)
        if self.difficulty == "easy":
            estimated_trumps = random.randint(1, 4)
        elif self.difficulty == "medium":
            estimated_trumps = max(1, estimated_trumps + random.randint(-1, 1))

        return estimated_trumps