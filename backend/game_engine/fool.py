"""
Fool (Durak) game implementation.

Classic Russian card game where players try to get rid of all their cards.
The last player with cards becomes the "Fool" (Durak).
"""

from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from .base_game import BaseGame, Player
from ..models.card import Card, Suit, Rank


class FoolAction(Enum):
    """Enumeration of possible Fool game actions."""
    ATTACK = "attack"
    DEFEND = "defend"
    PICK_UP = "pick_up"
    PASS_TURN = "pass_turn"


class FoolGame(BaseGame):
    """
    Fool (Durak) game implementation.

    Players take turns attacking and defending. Attackers play cards,
    defenders must beat them with higher cards or trump cards.
    First player to empty their hand wins.
    """

    def __init__(self, game_id: str = None):
        """
        Initialize a new Fool game.

        Args:
            game_id: Unique identifier for the game
        """
        super().__init__(game_id)
        self.trump_suit: Optional[Suit] = None
        self.trump_card: Optional[Card] = None
        self.table_cards: List[Tuple[Card, Optional[Card]]] = []  # (attack_card, defense_card)
        self.current_attacker_index = 0
        self.current_defender_index = 1
        self.attacking_phase = True
        self.cards_per_hand = 6

    def can_start(self) -> bool:
        """
        Check if the game can be started.

        Returns:
            True if there are 2-6 players
        """
        return 2 <= len(self.players) <= 6

    def setup_game(self) -> None:
        """
        Set up the Fool game.

        Deals cards, determines trump suit, and sets up initial state.
        """
        self.deck.reset()

        # Deal initial hands
        for _ in range(self.cards_per_hand):
            for player in self.players:
                card = self.deck.deal_card()
                if card:
                    player.add_card(card)

        # Set trump card and suit
        self.trump_card = self.deck.deal_card()
        if self.trump_card:
            self.trump_suit = self.trump_card.suit
            # Put trump card at bottom of deck
            self.deck.add_card(self.trump_card)

        # Find player with lowest trump card to start
        self._determine_first_attacker()

        # Initialize game state
        self.table_cards = []
        self.attacking_phase = True

    def _determine_first_attacker(self) -> None:
        """Determine which player attacks first (lowest trump card)."""
        lowest_trump_player = None
        lowest_trump_rank = None

        for i, player in enumerate(self.players):
            for card in player.hand:
                if card.suit == self.trump_suit:
                    if lowest_trump_rank is None or card.rank.value < lowest_trump_rank:
                        lowest_trump_rank = card.rank.value
                        lowest_trump_player = i

        if lowest_trump_player is not None:
            self.current_attacker_index = lowest_trump_player
            self.current_defender_index = (lowest_trump_player + 1) % len(self.players)

    def make_move(self, player_id: str, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Fool game move.

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

        player = self.get_player(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")

        action = move_data.get('action')
        if not action:
            raise ValueError("No action specified")

        try:
            action_enum = FoolAction(action)
        except ValueError:
            raise ValueError(f"Invalid action: {action}")

        # Validate it's the correct player's turn
        if not self._is_player_turn(player_id, action_enum):
            raise ValueError(f"Not {player.name}'s turn for action {action}")

        return self._execute_action(player, action_enum, move_data)

    def _is_player_turn(self, player_id: str, action: FoolAction) -> bool:
        """
        Check if it's the correct player's turn for the given action.

        Args:
            player_id: Player attempting to act
            action: Action they want to perform

        Returns:
            True if it's their turn, False otherwise
        """
        player_index = next((i for i, p in enumerate(self.players) if p.player_id == player_id), -1)
        if player_index == -1:
            return False

        if action in [FoolAction.ATTACK, FoolAction.PASS_TURN]:
            return player_index == self.current_attacker_index and self.attacking_phase
        elif action in [FoolAction.DEFEND, FoolAction.PICK_UP]:
            return player_index == self.current_defender_index and not self.attacking_phase

        return False

    def _execute_action(self, player: Player, action: FoolAction, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific Fool action.

        Args:
            player: Player performing the action
            action: Action to perform
            move_data: Additional move data

        Returns:
            Result of the action
        """
        if action == FoolAction.ATTACK:
            return self._execute_attack(player, move_data)
        elif action == FoolAction.DEFEND:
            return self._execute_defend(player, move_data)
        elif action == FoolAction.PICK_UP:
            return self._execute_pick_up(player)
        elif action == FoolAction.PASS_TURN:
            return self._execute_pass_turn(player)

        return {'action': action.value}

    def _execute_attack(self, player: Player, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an attack action."""
        card_data = move_data.get('card')
        if not card_data:
            raise ValueError("No card specified for attack")

        card = Card.from_dict(card_data)
        if not player.has_card(card):
            raise ValueError("Player doesn't have this card")

        # Validate attack card
        if not self._is_valid_attack_card(card):
            raise ValueError("Invalid attack card")

        # Remove card from player's hand and add to table
        player.remove_card(card)
        self.table_cards.append((card, None))

        result = {
            'action': 'attack',
            'card': card.to_dict(),
            'attacker': player.name,
            'table_cards': len(self.table_cards)
        }

        # Switch to defending phase
        self.attacking_phase = False

        # Check if player won by emptying hand
        if len(player.hand) == 0:
            winner = self.check_win_condition()
            if winner:
                self.end_game(winner)
                result['game_ended'] = True
                result['winner'] = winner.name

        return result

    def _execute_defend(self, player: Player, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a defend action."""
        card_data = move_data.get('card')
        if not card_data:
            raise ValueError("No card specified for defense")

        card = Card.from_dict(card_data)
        if not player.has_card(card):
            raise ValueError("Player doesn't have this card")

        # Find undefended attack card
        undefended_index = None
        for i, (attack_card, defense_card) in enumerate(self.table_cards):
            if defense_card is None:
                undefended_index = i
                break

        if undefended_index is None:
            raise ValueError("No attack card to defend against")

        attack_card = self.table_cards[undefended_index][0]

        # Validate defense card can beat attack card
        if not self._can_beat_card(attack_card, card):
            raise ValueError("Defense card cannot beat attack card")

        # Remove card from player's hand and add to table
        player.remove_card(card)
        self.table_cards[undefended_index] = (attack_card, card)

        result = {
            'action': 'defend',
            'defense_card': card.to_dict(),
            'attack_card': attack_card.to_dict(),
            'defender': player.name
        }

        # Check if all attacks are defended
        all_defended = all(defense_card is not None for _, defense_card in self.table_cards)
        if all_defended:
            # All attacks defended, clear table and continue
            self._clear_table()
            self._next_round()
            result['round_completed'] = True
            result['all_defended'] = True

        return result

    def _execute_pick_up(self, player: Player) -> Dict[str, Any]:
        """Execute pick up action (defender takes all cards)."""
        # Add all table cards to defender's hand
        cards_picked_up = []
        for attack_card, defense_card in self.table_cards:
            player.add_card(attack_card)
            cards_picked_up.append(attack_card)
            if defense_card:
                player.add_card(defense_card)
                cards_picked_up.append(defense_card)

        result = {
            'action': 'pick_up',
            'cards_picked_up': [card.to_dict() for card in cards_picked_up],
            'player': player.name,
            'new_hand_size': len(player.hand)
        }

        self._clear_table()
        self._next_round_after_pickup()

        return result

    def _execute_pass_turn(self, player: Player) -> Dict[str, Any]:
        """Execute pass turn action."""
        # Attacker passes, switch to next attacker or end attack phase
        self._next_attacker()

        return {
            'action': 'pass_turn',
            'player': player.name,
            'new_attacker_index': self.current_attacker_index
        }

    def _is_valid_attack_card(self, card: Card) -> bool:
        """
        Check if a card can be used for attack.

        Args:
            card: Card to validate

        Returns:
            True if card can be used for attack
        """
        if not self.table_cards:
            return True  # Any card can start an attack

        # Can only attack with cards matching ranks on the table
        table_ranks = set()
        for attack_card, defense_card in self.table_cards:
            table_ranks.add(attack_card.rank)
            if defense_card:
                table_ranks.add(defense_card.rank)

        return card.rank in table_ranks

    def _can_beat_card(self, attack_card: Card, defense_card: Card) -> bool:
        """
        Check if defense card can beat attack card.

        Args:
            attack_card: Card being attacked with
            defense_card: Card being used for defense

        Returns:
            True if defense card beats attack card
        """
        # Same suit: higher rank wins
        if attack_card.suit == defense_card.suit:
            return defense_card.rank.value > attack_card.rank.value

        # Trump beats non-trump
        if defense_card.suit == self.trump_suit and attack_card.suit != self.trump_suit:
            return True

        return False

    def _clear_table(self) -> None:
        """Clear all cards from the table."""
        self.table_cards = []

    def _next_round(self) -> None:
        """Start next round after successful defense."""
        # Defender becomes attacker
        self.current_attacker_index = self.current_defender_index
        self.current_defender_index = (self.current_defender_index + 1) % len(self.players)
        self.attacking_phase = True
        self._refill_hands()

    def _next_round_after_pickup(self) -> None:
        """Start next round after defender picked up cards."""
        # Same attacker, new defender
        self.current_defender_index = (self.current_defender_index + 1) % len(self.players)
        self.attacking_phase = True
        self._refill_hands()

    def _next_attacker(self) -> None:
        """Move to next potential attacker."""
        next_attacker = (self.current_attacker_index + 1) % len(self.players)
        if next_attacker == self.current_defender_index:
            next_attacker = (next_attacker + 1) % len(self.players)

        self.current_attacker_index = next_attacker

    def _refill_hands(self) -> None:
        """Refill all players' hands to 6 cards from the deck."""
        for player in self.players:
            while len(player.hand) < self.cards_per_hand and not self.deck.is_empty():
                card = self.deck.deal_card()
                if card:
                    player.add_card(card)

    def get_valid_moves(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get valid moves for a player.

        Args:
            player_id: ID of player to get moves for

        Returns:
            List of valid move descriptions
        """
        player = self.get_player(player_id)
        if not player:
            return []

        player_index = next((i for i, p in enumerate(self.players) if p.player_id == player_id), -1)
        moves = []

        if player_index == self.current_attacker_index and self.attacking_phase:
            # Attacker can attack or pass
            valid_attack_cards = [card for card in player.hand if self._is_valid_attack_card(card)]
            for card in valid_attack_cards:
                moves.append({
                    'action': 'attack',
                    'card': card.to_dict(),
                    'description': f'Attack with {card}'
                })

            moves.append({
                'action': 'pass_turn',
                'description': 'Pass turn to next attacker'
            })

        elif player_index == self.current_defender_index and not self.attacking_phase:
            # Defender can defend or pick up
            # Find undefended attack card
            undefended_attack = None
            for attack_card, defense_card in self.table_cards:
                if defense_card is None:
                    undefended_attack = attack_card
                    break

            if undefended_attack:
                valid_defense_cards = [
                    card for card in player.hand
                    if self._can_beat_card(undefended_attack, card)
                ]
                for card in valid_defense_cards:
                    moves.append({
                        'action': 'defend',
                        'card': card.to_dict(),
                        'description': f'Defend with {card}'
                    })

            moves.append({
                'action': 'pick_up',
                'description': 'Pick up all table cards'
            })

        return moves

    def check_win_condition(self) -> Optional[Player]:
        """
        Check if any player has won (emptied their hand).

        Returns:
            Winning player or None if no winner yet
        """
        for player in self.players:
            if len(player.hand) == 0 and self.deck.is_empty():
                return player
        return None

    def get_game_rules(self) -> Dict[str, Any]:
        """
        Get Fool game rules and configuration.

        Returns:
            Dictionary containing game rules
        """
        return {
            'name': 'Fool (Durak)',
            'min_players': 2,
            'max_players': 6,
            'deck_type': 'standard_52',
            'objective': 'Be first to empty your hand, avoid being the "Fool"',
            'setup': {
                'cards_per_hand': self.cards_per_hand,
                'trump_determination': 'Bottom card of deck after dealing'
            },
            'rules': [
                'Players take turns attacking and defending',
                'Attacker plays a card, defender must beat it',
                'Higher card of same suit or trump card beats attack',
                'Successful defender becomes next attacker',
                'Failed defender picks up all table cards',
                'First to empty hand wins'
            ],
            'card_ranking': 'Ace (high), King, Queen, Jack, 10, 9, 8, 7, 6 (low)',
            'trump_suit': self.trump_suit.name if self.trump_suit else None
        }