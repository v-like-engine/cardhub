"""
BlackJack game implementation.

Classic BlackJack card game where players try to get as close to 21
as possible without going over, while beating the dealer's hand.
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from .base_game import BaseGame, Player
from ..models.card import Card, Rank


class BlackjackAction(Enum):
    """Enumeration of possible BlackJack actions."""
    HIT = "hit"
    STAND = "stand"
    DOUBLE_DOWN = "double_down"
    SPLIT = "split"  # Future enhancement
    SURRENDER = "surrender"  # Future enhancement


class BlackjackGame(BaseGame):
    """
    BlackJack game implementation.

    Players compete against the dealer to get as close to 21 as possible
    without busting. Aces can be worth 1 or 11, face cards are worth 10.
    """

    def __init__(self, game_id: str = None):
        """
        Initialize a new BlackJack game.

        Args:
            game_id: Unique identifier for the game
        """
        super().__init__(game_id)
        self.dealer = Player("dealer", "Dealer", is_ai=True)
        self.players.append(self.dealer)
        self.betting_amounts: Dict[str, int] = {}
        self.player_actions: Dict[str, List[str]] = {}
        self.min_bet = 10
        self.max_bet = 1000

    def can_start(self) -> bool:
        """
        Check if the game can be started.

        Returns:
            True if there's at least one non-dealer player
        """
        non_dealer_players = [p for p in self.players if p.player_id != "dealer"]
        return len(non_dealer_players) >= 1

    def setup_game(self) -> None:
        """
        Set up the BlackJack game.

        Deals initial cards and sets up betting.
        """
        self.deck.reset()

        # Initialize player actions tracking
        for player in self.players:
            self.player_actions[player.player_id] = []

        # Deal initial cards (2 cards to each player and dealer)
        for _ in range(2):
            for player in self.players:
                card = self.deck.deal_card()
                if card:
                    player.add_card(card)

        # Set initial betting amounts (default bet for non-AI players)
        for player in self.players:
            if not player.is_ai and player.player_id != "dealer":
                self.betting_amounts[player.player_id] = self.min_bet

    def make_move(self, player_id: str, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a BlackJack move.

        Args:
            player_id: ID of player making the move
            move_data: Dictionary containing 'action' and optional parameters

        Returns:
            Result of the move including any state changes

        Raises:
            ValueError: If move is invalid
        """
        if self.state.value != "in_progress":
            raise ValueError("Game is not in progress")

        player = self.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        if player_id == "dealer":
            return self._dealer_turn()

        action = move_data.get('action')
        if not action:
            raise ValueError("No action specified")

        try:
            action_enum = BlackjackAction(action)
        except ValueError:
            raise ValueError(f"Invalid action: {action}")

        valid_moves = self.get_valid_moves(player_id)
        if not any(move['action'] == action for move in valid_moves):
            raise ValueError(f"Action {action} is not valid for player {player_id}")

        result = self._execute_action(player, action_enum, move_data)

        # Check if all players have finished their turns
        if self._all_players_finished():
            dealer_result = self._dealer_turn()
            result['dealer_result'] = dealer_result
            self._determine_winners()

        return result

    def _execute_action(self, player: Player, action: BlackjackAction, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific BlackJack action.

        Args:
            player: Player performing the action
            action: Action to perform
            move_data: Additional move data

        Returns:
            Result of the action
        """
        self.player_actions[player.player_id].append(action.value)

        if action == BlackjackAction.HIT:
            card = self.deck.deal_card()
            if card:
                player.add_card(card)
                hand_value = self.calculate_hand_value(player.hand)

                result = {
                    'action': 'hit',
                    'card_dealt': card.to_dict(),
                    'new_hand_value': hand_value,
                    'busted': hand_value > 21
                }

                if hand_value > 21:
                    player.is_active = False
                    result['player_busted'] = True

                return result

        elif action == BlackjackAction.STAND:
            player.is_active = False
            return {
                'action': 'stand',
                'final_hand_value': self.calculate_hand_value(player.hand)
            }

        elif action == BlackjackAction.DOUBLE_DOWN:
            # Double the bet and hit once
            if player.player_id in self.betting_amounts:
                self.betting_amounts[player.player_id] *= 2

            card = self.deck.deal_card()
            if card:
                player.add_card(card)
                player.is_active = False
                hand_value = self.calculate_hand_value(player.hand)

                return {
                    'action': 'double_down',
                    'card_dealt': card.to_dict(),
                    'final_hand_value': hand_value,
                    'busted': hand_value > 21,
                    'new_bet': self.betting_amounts.get(player.player_id, 0)
                }

        return {'action': action.value}

    def _dealer_turn(self) -> Dict[str, Any]:
        """
        Execute the dealer's turn following BlackJack rules.

        Returns:
            Result of dealer's actions
        """
        dealer = self.get_player("dealer")
        if not dealer:
            return {}

        actions = []
        while self.calculate_hand_value(dealer.hand) < 17:
            card = self.deck.deal_card()
            if card:
                dealer.add_card(card)
                actions.append({
                    'action': 'hit',
                    'card': card.to_dict()
                })

        final_value = self.calculate_hand_value(dealer.hand)
        dealer.is_active = False

        return {
            'dealer_actions': actions,
            'final_hand_value': final_value,
            'busted': final_value > 21
        }

    def _all_players_finished(self) -> bool:
        """
        Check if all non-dealer players have finished their turns.

        Returns:
            True if all players are inactive, False otherwise
        """
        for player in self.players:
            if player.player_id != "dealer" and player.is_active:
                return False
        return True

    def _determine_winners(self) -> None:
        """Determine winners and update scores."""
        dealer = self.get_player("dealer")
        if not dealer:
            return

        dealer_value = self.calculate_hand_value(dealer.hand)
        dealer_busted = dealer_value > 21

        for player in self.players:
            if player.player_id == "dealer":
                continue

            player_value = self.calculate_hand_value(player.hand)
            player_busted = player_value > 21

            # Determine if player wins
            if player_busted:
                # Player loses
                player.score -= self.betting_amounts.get(player.player_id, 0)
            elif dealer_busted:
                # Player wins (dealer busted)
                player.score += self.betting_amounts.get(player.player_id, 0)
            elif player_value > dealer_value:
                # Player wins (higher value)
                player.score += self.betting_amounts.get(player.player_id, 0)
            elif player_value == dealer_value:
                # Push (tie) - no change in score
                pass
            else:
                # Player loses (lower value)
                player.score -= self.betting_amounts.get(player.player_id, 0)

            # Check for BlackJack (21 with 2 cards) - pays 3:2
            if len(player.hand) == 2 and player_value == 21:
                player.score += int(self.betting_amounts.get(player.player_id, 0) * 0.5)

        self.end_game()

    def get_valid_moves(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get valid moves for a player.

        Args:
            player_id: ID of player to get moves for

        Returns:
            List of valid move descriptions
        """
        player = self.get_player(player_id)
        if not player or not player.is_active or player_id == "dealer":
            return []

        moves = [
            {'action': 'hit', 'description': 'Take another card'},
            {'action': 'stand', 'description': 'Keep current hand'}
        ]

        # Double down only allowed on first move with 2 cards
        if (len(player.hand) == 2 and
            len(self.player_actions.get(player_id, [])) == 0):
            moves.append({
                'action': 'double_down',
                'description': 'Double bet and take exactly one more card'
            })

        return moves

    def check_win_condition(self) -> Optional[Player]:
        """
        Check win condition for BlackJack.

        Returns:
            None (BlackJack doesn't have a single winner in traditional sense)
        """
        return None

    def calculate_hand_value(self, hand: List[Card]) -> int:
        """
        Calculate the best possible value of a BlackJack hand.

        Args:
            hand: List of cards in the hand

        Returns:
            Best possible hand value
        """
        total = 0
        aces = 0

        for card in hand:
            if card.rank == Rank.ACE:
                aces += 1
                total += 11
            elif card.rank.value >= 10:  # Face cards
                total += 10
            else:
                total += card.rank.value

        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def is_blackjack(self, hand: List[Card]) -> bool:
        """
        Check if a hand is a BlackJack (21 with 2 cards).

        Args:
            hand: List of cards to check

        Returns:
            True if hand is BlackJack, False otherwise
        """
        return len(hand) == 2 and self.calculate_hand_value(hand) == 21

    def is_busted(self, hand: List[Card]) -> bool:
        """
        Check if a hand is busted (over 21).

        Args:
            hand: List of cards to check

        Returns:
            True if hand is busted, False otherwise
        """
        return self.calculate_hand_value(hand) > 21

    def get_game_rules(self) -> Dict[str, Any]:
        """
        Get BlackJack rules and configuration.

        Returns:
            Dictionary containing game rules
        """
        return {
            'name': 'BlackJack',
            'min_players': 1,
            'max_players': 7,
            'deck_type': 'standard_52',
            'objective': 'Get as close to 21 as possible without going over',
            'card_values': {
                'number_cards': 'Face value (2-10)',
                'face_cards': '10 points each',
                'ace': '1 or 11 (whichever is better)'
            },
            'rules': [
                'Players receive 2 cards initially',
                'Dealer must hit on 16 and stand on 17',
                'BlackJack (21 with 2 cards) pays 3:2',
                'Bust if total exceeds 21',
                'Beat dealer without busting to win'
            ],
            'betting': {
                'min_bet': self.min_bet,
                'max_bet': self.max_bet
            }
        }