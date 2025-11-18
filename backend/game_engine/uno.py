"""
Uno game implementation.

Classic Uno card game where players match colors and numbers,
use action cards strategically, and try to be first to empty their hand.
"""

from typing import List, Dict, Any, Optional
from enum import Enum

from .base_game import BaseGame, Player
from ..models.uno_card import UnoCard, UnoColor, UnoType
from ..models.uno_deck import UnoDeck


class UnoAction(Enum):
    """Enumeration of possible Uno actions."""
    PLAY_CARD = "play_card"
    DRAW_CARD = "draw_card"
    CALL_UNO = "call_uno"
    CHALLENGE_UNO = "challenge_uno"


class UnoPlayer(Player):
    """
    Extended Player class for Uno-specific functionality.
    """

    def __init__(self, player_id: str, name: str, is_ai: bool = False):
        """
        Initialize an Uno player.

        Args:
            player_id: Unique identifier for the player
            name: Display name of the player
            is_ai: Whether this player is AI-controlled
        """
        super().__init__(player_id, name, is_ai)
        self.uno_cards: List[UnoCard] = []
        self.called_uno = False
        self.penalty_cards = 0

    def add_uno_card(self, card: UnoCard) -> None:
        """Add an Uno card to the player's hand."""
        self.uno_cards.append(card)

    def remove_uno_card(self, card: UnoCard) -> bool:
        """Remove an Uno card from the player's hand."""
        if card in self.uno_cards:
            self.uno_cards.remove(card)
            return True
        return False

    def has_uno_card(self, card: UnoCard) -> bool:
        """Check if player has a specific Uno card."""
        return card in self.uno_cards

    def hand_size(self) -> int:
        """Get the number of Uno cards in hand."""
        return len(self.uno_cards)

    def clear_uno_hand(self) -> None:
        """Clear all Uno cards from the player's hand."""
        self.uno_cards.clear()
        self.called_uno = False

    def to_dict(self, hide_hand: bool = False) -> Dict[str, Any]:
        """Convert Uno player to dictionary representation."""
        base_dict = super().to_dict(hide_hand)
        base_dict.update({
            'uno_cards': [] if hide_hand else [card.to_dict() for card in self.uno_cards],
            'uno_hand_size': len(self.uno_cards),
            'called_uno': self.called_uno,
            'penalty_cards': self.penalty_cards
        })
        return base_dict


class UnoGame(BaseGame):
    """
    Uno game implementation.

    Players match colors, numbers, or use action cards to empty their hands.
    Special rules include calling "Uno" and various action card effects.
    """

    def __init__(self, game_id: str = None):
        """
        Initialize a new Uno game.

        Args:
            game_id: Unique identifier for the game
        """
        super().__init__(game_id)
        self.uno_deck = UnoDeck()
        self.discard_pile: List[UnoCard] = []
        self.current_color: Optional[UnoColor] = None
        self.direction = 1  # 1 for clockwise, -1 for counter-clockwise
        self.skip_next_player = False
        self.draw_penalty = 0  # Accumulated draw penalty
        self.cards_per_hand = 7
        self.uno_players: List[UnoPlayer] = []

    def add_player(self, player_id: str, name: str, is_ai: bool = False) -> UnoPlayer:
        """
        Add a new Uno player to the game.

        Args:
            player_id: Unique identifier for the player
            name: Display name of the player
            is_ai: Whether this player is AI-controlled

        Returns:
            The created UnoPlayer object
        """
        if self.state.value != "waiting_for_players":
            raise ValueError("Cannot add players when game is not waiting for players")

        if any(p.player_id == player_id for p in self.uno_players):
            raise ValueError(f"Player {player_id} already exists in game")

        uno_player = UnoPlayer(player_id, name, is_ai)
        self.uno_players.append(uno_player)
        self.players.append(uno_player)  # Keep base class list in sync
        return uno_player

    def can_start(self) -> bool:
        """
        Check if the game can be started.

        Returns:
            True if there are 2-10 players
        """
        return 2 <= len(self.uno_players) <= 10

    def setup_game(self) -> None:
        """
        Set up the Uno game.

        Deals initial hands and sets up the discard pile.
        """
        self.uno_deck.reset()

        # Deal initial hands
        for _ in range(self.cards_per_hand):
            for player in self.uno_players:
                card = self.uno_deck.deal_card()
                if card:
                    player.add_uno_card(card)

        # Start discard pile with a non-action card if possible
        starter_card = None
        while starter_card is None or starter_card.is_wild():
            starter_card = self.uno_deck.deal_card()
            if starter_card and starter_card.is_wild():
                # Put wild card back and shuffle
                self.uno_deck.add_card(starter_card)
                self.uno_deck.shuffle()
                starter_card = None

        if starter_card:
            self.discard_pile.append(starter_card)
            self.current_color = starter_card.color

            # Handle special starter cards
            if starter_card.card_type == UnoType.SKIP:
                self.skip_next_player = True
            elif starter_card.card_type == UnoType.REVERSE:
                self.direction *= -1
            elif starter_card.card_type == UnoType.DRAW_TWO:
                self.draw_penalty = 2

    def make_move(self, player_id: str, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an Uno game move.

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

        current_player = self.get_current_uno_player()
        if not current_player or current_player.player_id != player_id:
            raise ValueError("Not your turn")

        action = move_data.get('action')
        if not action:
            raise ValueError("No action specified")

        try:
            action_enum = UnoAction(action)
        except ValueError:
            raise ValueError(f"Invalid action: {action}")

        return self._execute_action(current_player, action_enum, move_data)

    def get_current_uno_player(self) -> Optional[UnoPlayer]:
        """Get the current active Uno player."""
        if not self.uno_players:
            return None
        return self.uno_players[self.current_player_index]

    def _execute_action(self, player: UnoPlayer, action: UnoAction, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific Uno action.

        Args:
            player: Player performing the action
            action: Action to perform
            move_data: Additional move data

        Returns:
            Result of the action
        """
        if action == UnoAction.PLAY_CARD:
            return self._execute_play_card(player, move_data)
        elif action == UnoAction.DRAW_CARD:
            return self._execute_draw_card(player)
        elif action == UnoAction.CALL_UNO:
            return self._execute_call_uno(player)
        elif action == UnoAction.CHALLENGE_UNO:
            return self._execute_challenge_uno(player, move_data)

        return {'action': action.value}

    def _execute_play_card(self, player: UnoPlayer, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute play card action."""
        card_data = move_data.get('card')
        if not card_data:
            raise ValueError("No card specified")

        card = UnoCard.from_dict(card_data)
        if not player.has_uno_card(card):
            raise ValueError("Player doesn't have this card")

        # Validate card can be played
        if not self._can_play_card(card):
            raise ValueError("Card cannot be played")

        # Handle draw penalty first
        if self.draw_penalty > 0 and card.card_type != UnoType.DRAW_TWO:
            # Must play Draw Two to avoid penalty
            raise ValueError("Must play Draw Two card or draw penalty cards")

        # Remove card from hand and add to discard pile
        player.remove_uno_card(card)
        self.discard_pile.append(card)

        result = {
            'action': 'play_card',
            'card': card.to_dict(),
            'player': player.name,
            'new_hand_size': player.hand_size()
        }

        # Handle special card effects
        special_effect = self._handle_special_card(card, move_data)
        if special_effect:
            result.update(special_effect)

        # Update current color
        if card.is_wild():
            new_color = move_data.get('new_color')
            if new_color:
                try:
                    self.current_color = UnoColor(new_color.lower())
                    result['color_changed'] = self.current_color.value
                except ValueError:
                    raise ValueError(f"Invalid color: {new_color}")
            else:
                raise ValueError("Must specify color for wild card")
        else:
            self.current_color = card.color

        # Check for Uno (one card left)
        if player.hand_size() == 1 and not player.called_uno:
            # Player should have called Uno
            result['should_call_uno'] = True

        # Check for win condition
        if player.hand_size() == 0:
            self._calculate_scores()
            self.end_game(player)
            result['game_won'] = True
            result['final_scores'] = {p.name: p.score for p in self.uno_players}

        # Move to next player
        if not result.get('game_won'):
            self._next_turn()
            next_player = self.get_current_uno_player()
            result['next_player'] = next_player.name if next_player else None

        return result

    def _execute_draw_card(self, player: UnoPlayer) -> Dict[str, Any]:
        """Execute draw card action."""
        cards_drawn = []

        # Handle draw penalty
        cards_to_draw = max(1, self.draw_penalty)
        self.draw_penalty = 0

        for _ in range(cards_to_draw):
            # Check if deck is empty
            if self.uno_deck.is_empty():
                self._reshuffle_deck()

            card = self.uno_deck.deal_card()
            if card:
                player.add_uno_card(card)
                cards_drawn.append(card)

        result = {
            'action': 'draw_card',
            'cards_drawn': [card.to_dict() for card in cards_drawn],
            'cards_count': len(cards_drawn),
            'new_hand_size': player.hand_size()
        }

        # If player drew due to penalty, automatically end turn
        if len(cards_drawn) > 1:
            self._next_turn()
            next_player = self.get_current_uno_player()
            result['next_player'] = next_player.name if next_player else None
            result['penalty_draw'] = True
        else:
            # Regular draw - player can choose to play drawn card or end turn
            drawn_card = cards_drawn[0] if cards_drawn else None
            if drawn_card and self._can_play_card(drawn_card):
                result['can_play_drawn_card'] = True
                result['drawn_card_playable'] = drawn_card.to_dict()

        return result

    def _execute_call_uno(self, player: UnoPlayer) -> Dict[str, Any]:
        """Execute call Uno action."""
        if player.hand_size() != 1:
            # Penalty for false Uno call
            penalty_cards = 2
            for _ in range(penalty_cards):
                if self.uno_deck.is_empty():
                    self._reshuffle_deck()
                card = self.uno_deck.deal_card()
                if card:
                    player.add_uno_card(card)

            return {
                'action': 'call_uno',
                'false_call': True,
                'penalty_cards': penalty_cards,
                'new_hand_size': player.hand_size()
            }

        player.called_uno = True
        return {
            'action': 'call_uno',
            'success': True,
            'player': player.name
        }

    def _execute_challenge_uno(self, player: UnoPlayer, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute challenge Uno action (challenge another player who didn't call Uno)."""
        target_player_id = move_data.get('target_player')
        if not target_player_id:
            raise ValueError("Must specify target player for Uno challenge")

        target_player = next((p for p in self.uno_players if p.player_id == target_player_id), None)
        if not target_player:
            raise ValueError("Target player not found")

        if target_player.hand_size() == 1 and not target_player.called_uno:
            # Valid challenge - target player draws penalty
            penalty_cards = 2
            for _ in range(penalty_cards):
                if self.uno_deck.is_empty():
                    self._reshuffle_deck()
                card = self.uno_deck.deal_card()
                if card:
                    target_player.add_uno_card(card)

            return {
                'action': 'challenge_uno',
                'success': True,
                'target_player': target_player.name,
                'penalty_cards': penalty_cards,
                'target_new_hand_size': target_player.hand_size()
            }
        else:
            # Invalid challenge - challenging player draws penalty
            penalty_cards = 2
            for _ in range(penalty_cards):
                if self.uno_deck.is_empty():
                    self._reshuffle_deck()
                card = self.uno_deck.deal_card()
                if card:
                    player.add_uno_card(card)

            return {
                'action': 'challenge_uno',
                'success': False,
                'penalty_cards': penalty_cards,
                'challenger_new_hand_size': player.hand_size()
            }

    def _can_play_card(self, card: UnoCard) -> bool:
        """
        Check if a card can be played.

        Args:
            card: Card to check

        Returns:
            True if card can be played
        """
        if not self.discard_pile:
            return True

        top_card = self.discard_pile[-1]

        # Handle draw penalty - only Draw Two or Wild Draw Four can be played
        if self.draw_penalty > 0:
            return card.card_type in [UnoType.DRAW_TWO, UnoType.WILD_DRAW_FOUR]

        return card.can_be_played_on(top_card, self.current_color)

    def _handle_special_card(self, card: UnoCard, move_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle special card effects.

        Args:
            card: Card that was played
            move_data: Additional move data

        Returns:
            Dictionary with special effect results or None
        """
        if card.card_type == UnoType.SKIP:
            self.skip_next_player = True
            return {'special_effect': 'skip_next_player'}

        elif card.card_type == UnoType.REVERSE:
            self.direction *= -1
            return {
                'special_effect': 'reverse_direction',
                'new_direction': 'clockwise' if self.direction == 1 else 'counter_clockwise'
            }

        elif card.card_type == UnoType.DRAW_TWO:
            self.draw_penalty += 2
            return {
                'special_effect': 'draw_two',
                'total_penalty': self.draw_penalty
            }

        elif card.card_type == UnoType.WILD_DRAW_FOUR:
            self.draw_penalty += 4
            return {
                'special_effect': 'wild_draw_four',
                'total_penalty': self.draw_penalty
            }

        elif card.card_type == UnoType.WILD:
            return {'special_effect': 'wild_color_change'}

        return None

    def _next_turn(self) -> None:
        """Move to the next player's turn."""
        if self.skip_next_player:
            self.skip_next_player = False
            self.current_player_index = self._get_next_player_index()

        self.current_player_index = self._get_next_player_index()

        # Reset Uno call for next player
        current_player = self.get_current_uno_player()
        if current_player and current_player.hand_size() != 1:
            current_player.called_uno = False

    def _get_next_player_index(self) -> int:
        """Get the index of the next player based on direction."""
        next_index = self.current_player_index + self.direction
        if next_index >= len(self.uno_players):
            next_index = 0
        elif next_index < 0:
            next_index = len(self.uno_players) - 1
        return next_index

    def _reshuffle_deck(self) -> None:
        """Reshuffle the discard pile back into the deck."""
        if len(self.discard_pile) > 1:
            # Keep top card, shuffle rest back into deck
            top_card = self.discard_pile.pop()
            self.uno_deck.add_cards(self.discard_pile)
            self.uno_deck.shuffle()
            self.discard_pile = [top_card]

    def _calculate_scores(self) -> None:
        """Calculate scores at end of round."""
        for player in self.uno_players:
            if player.hand_size() == 0:
                # Winner gets points from all other players' hands
                for other_player in self.uno_players:
                    if other_player != player:
                        for card in other_player.uno_cards:
                            player.score += card.get_points()

    def get_valid_moves(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get valid moves for a player.

        Args:
            player_id: ID of player to get moves for

        Returns:
            List of valid move descriptions
        """
        player = next((p for p in self.uno_players if p.player_id == player_id), None)
        current_player = self.get_current_uno_player()

        if not player or not current_player or player.player_id != current_player.player_id:
            return []

        moves = []

        # Check playable cards
        for card in player.uno_cards:
            if self._can_play_card(card):
                move = {
                    'action': 'play_card',
                    'card': card.to_dict(),
                    'description': f'Play {card}'
                }

                # Add color options for wild cards
                if card.is_wild():
                    move['color_options'] = [color.value for color in UnoColor if color != UnoColor.WILD]

                moves.append(move)

        # Always can draw cards
        moves.append({
            'action': 'draw_card',
            'description': f'Draw {max(1, self.draw_penalty)} card(s)'
        })

        # Can call Uno if has exactly one card
        if player.hand_size() == 1 and not player.called_uno:
            moves.append({
                'action': 'call_uno',
                'description': 'Call Uno!'
            })

        # Can challenge other players who should have called Uno
        for other_player in self.uno_players:
            if (other_player != player and
                other_player.hand_size() == 1 and
                not other_player.called_uno):
                moves.append({
                    'action': 'challenge_uno',
                    'target_player': other_player.player_id,
                    'description': f'Challenge {other_player.name} for not calling Uno'
                })

        return moves

    def check_win_condition(self) -> Optional[UnoPlayer]:
        """
        Check if any player has won.

        Returns:
            Winning player or None if no winner yet
        """
        for player in self.uno_players:
            if player.hand_size() == 0:
                return player
        return None

    def get_game_rules(self) -> Dict[str, Any]:
        """
        Get Uno game rules and configuration.

        Returns:
            Dictionary containing game rules
        """
        return {
            'name': 'Uno',
            'min_players': 2,
            'max_players': 10,
            'deck_type': 'uno_108',
            'objective': 'Be first to empty your hand',
            'setup': {
                'cards_per_hand': self.cards_per_hand,
                'colors': ['Red', 'Blue', 'Green', 'Yellow'],
                'wild_cards': 8
            },
            'special_cards': {
                'Skip': 'Next player loses turn',
                'Reverse': 'Reverse play direction',
                'Draw Two': 'Next player draws 2 cards',
                'Wild': 'Change color',
                'Wild Draw Four': 'Change color, next player draws 4'
            },
            'rules': [
                'Match color, number, or symbol',
                'Wild cards can be played anytime',
                'Call "Uno" when you have one card left',
                'Action cards have special effects',
                'First to empty hand wins round'
            ],
            'current_color': self.current_color.value if self.current_color else None,
            'direction': 'clockwise' if self.direction == 1 else 'counter_clockwise',
            'draw_penalty': self.draw_penalty
        }