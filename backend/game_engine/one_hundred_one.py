"""
101 game implementation.

Fast-paced card game where players aim to reach exactly 101 points
without going over, using special card effects and strategy.
"""

from typing import List, Dict, Any, Optional
from enum import Enum

from .base_game import BaseGame, Player
from ..models.card import Card, Rank, Suit


class OneHundredOneAction(Enum):
    """Enumeration of possible 101 game actions."""
    PLAY_CARD = "play_card"
    DRAW_CARD = "draw_card"
    DECLARE_101 = "declare_101"


class OneHundredOneGame(BaseGame):
    """
    101 game implementation.

    Players play cards to accumulate points toward 101. Special cards
    have unique effects. First to reach exactly 101 wins.
    """

    def __init__(self, game_id: str = None):
        """
        Initialize a new 101 game.

        Args:
            game_id: Unique identifier for the game
        """
        super().__init__(game_id)
        self.target_score = 101
        self.discard_pile: List[Card] = []
        self.current_suit: Optional[Suit] = None
        self.direction = 1  # 1 for clockwise, -1 for counter-clockwise
        self.cards_per_hand = 4
        self.skip_next_player = False

    def can_start(self) -> bool:
        """
        Check if the game can be started.

        Returns:
            True if there are 2-6 players
        """
        return 2 <= len(self.players) <= 6

    def setup_game(self) -> None:
        """
        Set up the 101 game.

        Deals initial hands and sets up the discard pile.
        """
        self.deck.reset()

        # Deal initial hands
        for _ in range(self.cards_per_hand):
            for player in self.players:
                card = self.deck.deal_card()
                if card:
                    player.add_card(card)

        # Start discard pile
        starter_card = self.deck.deal_card()
        if starter_card:
            self.discard_pile.append(starter_card)
            self.current_suit = starter_card.suit

            # Handle special starter cards
            if starter_card.rank == Rank.EIGHT:
                # 8 skips first player
                self.skip_next_player = True
            elif starter_card.rank == Rank.KING:
                # King reverses direction
                self.direction *= -1

        # Initialize all player scores to 0
        for player in self.players:
            player.score = 0

    def make_move(self, player_id: str, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a 101 game move.

        Args:
            player_id: ID of player making the move
            move_data: Dictionary containing move details

        Returns:
            Result of the move

        Raises:
            ValueError: If move is invalid
        """
        if self.state.value != "in_progress":
            raise ValueError("Game is not in progress")

        current_player = self.get_current_player()
        if not current_player or current_player.player_id != player_id:
            raise ValueError("Not your turn")

        action = move_data.get('action')
        if not action:
            raise ValueError("No action specified")

        try:
            action_enum = OneHundredOneAction(action)
        except ValueError:
            raise ValueError(f"Invalid action: {action}")

        return self._execute_action(current_player, action_enum, move_data)

    def _execute_action(self, player: Player, action: OneHundredOneAction, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific 101 action.

        Args:
            player: Player performing the action
            action: Action to perform
            move_data: Additional move data

        Returns:
            Result of the action
        """
        if action == OneHundredOneAction.PLAY_CARD:
            return self._execute_play_card(player, move_data)
        elif action == OneHundredOneAction.DRAW_CARD:
            return self._execute_draw_card(player)
        elif action == OneHundredOneAction.DECLARE_101:
            return self._execute_declare_101(player)

        return {'action': action.value}

    def _execute_play_card(self, player: Player, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute play card action."""
        card_data = move_data.get('card')
        if not card_data:
            raise ValueError("No card specified")

        card = Card.from_dict(card_data)
        if not player.has_card(card):
            raise ValueError("Player doesn't have this card")

        # Validate card can be played
        if not self._can_play_card(card, move_data):
            raise ValueError("Card cannot be played")

        # Remove card from hand and add to discard pile
        player.remove_card(card)
        self.discard_pile.append(card)

        # Calculate points for the card
        points = self._get_card_points(card)
        player.score += points

        result = {
            'action': 'play_card',
            'card': card.to_dict(),
            'points_gained': points,
            'new_score': player.score,
            'player': player.name
        }

        # Handle special card effects
        special_effect = self._handle_special_card(card, move_data)
        if special_effect:
            result.update(special_effect)

        # Update current suit
        if card.rank == Rank.JACK:
            # Jack allows suit change
            new_suit = move_data.get('new_suit')
            if new_suit:
                try:
                    self.current_suit = Suit[new_suit.upper()]
                    result['suit_changed'] = self.current_suit.name
                except (KeyError, AttributeError):
                    self.current_suit = card.suit
            else:
                self.current_suit = card.suit
        else:
            self.current_suit = card.suit

        # Check for win condition
        if player.score == self.target_score:
            self.end_game(player)
            result['game_won'] = True
        elif player.score > self.target_score:
            # Player busted
            player.is_active = False
            result['player_busted'] = True
            # Check if only one player remains
            active_players = [p for p in self.players if p.is_active]
            if len(active_players) == 1:
                self.end_game(active_players[0])
                result['game_won'] = True
                result['winner'] = active_players[0].name

        # Move to next player
        if not result.get('game_won'):
            self._next_turn()
            result['next_player'] = self.get_current_player().name if self.get_current_player() else None

        return result

    def _execute_draw_card(self, player: Player) -> Dict[str, Any]:
        """Execute draw card action."""
        # Check if deck is empty
        if self.deck.is_empty():
            # Reshuffle discard pile (except top card)
            if len(self.discard_pile) > 1:
                top_card = self.discard_pile.pop()
                self.deck.add_cards(self.discard_pile)
                self.deck.shuffle()
                self.discard_pile = [top_card]

        card = self.deck.deal_card()
        if card:
            player.add_card(card)

        result = {
            'action': 'draw_card',
            'card': card.to_dict() if card else None,
            'new_hand_size': len(player.hand)
        }

        # Move to next player after drawing
        self._next_turn()
        result['next_player'] = self.get_current_player().name if self.get_current_player() else None

        return result

    def _execute_declare_101(self, player: Player) -> Dict[str, Any]:
        """Execute declare 101 action (early win claim)."""
        if player.score == self.target_score:
            self.end_game(player)
            return {
                'action': 'declare_101',
                'winner': player.name,
                'final_score': player.score
            }
        else:
            # False declaration penalty
            player.score = 0
            return {
                'action': 'declare_101',
                'false_declaration': True,
                'score_reset': True,
                'new_score': 0
            }

    def _can_play_card(self, card: Card, move_data: Dict[str, Any]) -> bool:
        """
        Check if a card can be played.

        Args:
            card: Card to check
            move_data: Additional move data

        Returns:
            True if card can be played
        """
        if not self.discard_pile:
            return True

        top_card = self.discard_pile[-1]

        # Jack can always be played (wild card)
        if card.rank == Rank.JACK:
            return True

        # Must match suit or rank of top card
        return (card.suit == self.current_suit or
                card.rank == top_card.rank)

    def _get_card_points(self, card: Card) -> int:
        """
        Get points value for a card.

        Args:
            card: Card to get points for

        Returns:
            Point value of the card
        """
        if card.rank == Rank.ACE:
            return 11
        elif card.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
            return 10
        else:
            return card.rank.value

    def _handle_special_card(self, card: Card, move_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle special card effects.

        Args:
            card: Card that was played
            move_data: Additional move data

        Returns:
            Dictionary with special effect results or None
        """
        if card.rank == Rank.EIGHT:
            # Skip next player
            self.skip_next_player = True
            return {'special_effect': 'skip_next_player'}

        elif card.rank == Rank.KING:
            # Reverse direction
            self.direction *= -1
            return {
                'special_effect': 'reverse_direction',
                'new_direction': 'clockwise' if self.direction == 1 else 'counter_clockwise'
            }

        elif card.rank == Rank.JACK:
            # Wild card - suit change handled in main method
            return {'special_effect': 'suit_change'}

        return None

    def _next_turn(self) -> None:
        """Move to the next player's turn."""
        if self.skip_next_player:
            # Skip one additional player
            self.skip_next_player = False
            self.current_player_index = self._get_next_player_index()

        self.current_player_index = self._get_next_player_index()

        # Skip inactive players
        attempts = 0
        while (not self.get_current_player().is_active and
               attempts < len(self.players)):
            self.current_player_index = self._get_next_player_index()
            attempts += 1

    def _get_next_player_index(self) -> int:
        """Get the index of the next player based on direction."""
        next_index = self.current_player_index + self.direction
        if next_index >= len(self.players):
            next_index = 0
        elif next_index < 0:
            next_index = len(self.players) - 1
        return next_index

    def get_valid_moves(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get valid moves for a player.

        Args:
            player_id: ID of player to get moves for

        Returns:
            List of valid move descriptions
        """
        player = self.get_player(player_id)
        current_player = self.get_current_player()

        if not player or not current_player or player.player_id != current_player.player_id:
            return []

        moves = []

        # Check playable cards
        for card in player.hand:
            if self._can_play_card(card, {}):
                move = {
                    'action': 'play_card',
                    'card': card.to_dict(),
                    'points': self._get_card_points(card),
                    'description': f'Play {card} ({self._get_card_points(card)} points)'
                }

                # Add suit change options for Jacks
                if card.rank == Rank.JACK:
                    move['suit_options'] = [suit.name.lower() for suit in Suit]

                moves.append(move)

        # Always can draw if no playable cards or choose to draw
        moves.append({
            'action': 'draw_card',
            'description': 'Draw a card from deck'
        })

        # Can declare 101 if at exactly 101 points
        if player.score == self.target_score:
            moves.append({
                'action': 'declare_101',
                'description': 'Declare 101 and win!'
            })

        return moves

    def check_win_condition(self) -> Optional[Player]:
        """
        Check if any player has won.

        Returns:
            Winning player or None if no winner yet
        """
        for player in self.players:
            if player.score == self.target_score:
                return player

        # Check if only one player remains active
        active_players = [p for p in self.players if p.is_active]
        if len(active_players) == 1:
            return active_players[0]

        return None

    def get_game_rules(self) -> Dict[str, Any]:
        """
        Get 101 game rules and configuration.

        Returns:
            Dictionary containing game rules
        """
        return {
            'name': '101',
            'min_players': 2,
            'max_players': 6,
            'deck_type': 'standard_52',
            'objective': 'Be first to reach exactly 101 points',
            'setup': {
                'cards_per_hand': self.cards_per_hand,
                'target_score': self.target_score
            },
            'card_values': {
                'ace': '11 points',
                'face_cards': '10 points each',
                'number_cards': 'Face value'
            },
            'special_cards': {
                '8': 'Skip next player',
                'Jack': 'Wild card - change suit',
                'King': 'Reverse play direction'
            },
            'rules': [
                'Play cards matching suit or rank',
                'Accumulate points toward 101',
                'Special cards have unique effects',
                'Going over 101 eliminates you',
                'First to exactly 101 wins'
            ],
            'current_suit': self.current_suit.name if self.current_suit else None,
            'direction': 'clockwise' if self.direction == 1 else 'counter_clockwise'
        }