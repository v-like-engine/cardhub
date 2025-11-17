"""
Game-related API routes for SoundWound platform.

This module handles all game-related endpoints including
game creation, moves, state management, and AI interactions.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from ...database.database import get_db_session
from ...database.models import User, GameSession, UserGameStatistics
from ...game_engine.blackjack import BlackjackGame
from ...game_engine.fool import FoolGame
from ...game_engine.one_hundred_one import OneHundredOneGame
from ...game_engine.uno import UnoGame
from ...ai.blackjack_ai import BlackjackAI
from ...ai.fool_ai import FoolAI
from ...ai.one_hundred_one_ai import OneHundredOneAI
from ...ai.uno_ai import UnoAI

logger = logging.getLogger(__name__)
games_bp = Blueprint('games', __name__)

# In-memory game storage (in production, use Redis or similar)
active_games = {}

# Game class mapping
GAME_CLASSES = {
    'blackjack': BlackjackGame,
    'fool': FoolGame,
    '101': OneHundredOneGame,
    'uno': UnoGame
}

# AI class mapping
AI_CLASSES = {
    'blackjack': BlackjackAI,
    'fool': FoolAI,
    '101': OneHundredOneAI,
    'uno': UnoAI
}


@games_bp.route('/create', methods=['POST'])
def create_game():
    """Create a new game session."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'error': 'No data provided or invalid JSON'}), 400

        game_type = data.get('game_type')
        user_id = data.get('user_id')
        ai_difficulty = data.get('ai_difficulty', 'medium')

        if not game_type or not user_id:
            return jsonify({'error': 'game_type and user_id are required'}), 400

        if game_type not in GAME_CLASSES:
            return jsonify({'error': f'Unsupported game type: {game_type}'}), 400

        # Create game instance
        game_class = GAME_CLASSES[game_type]
        game = game_class()

        # Add human player
        with next(get_db_session()) as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Add human player to game
            human_player = game.add_player(str(user_id), user.display_name, is_ai=False)

            # Add AI player
            ai_player = game.add_player("ai_1", f"AI ({ai_difficulty.title()})", is_ai=True)

            # Store game in memory
            active_games[game.game_id] = {
                'game': game,
                'ai_difficulty': ai_difficulty,
                'ai_instances': {
                    'ai_1': AI_CLASSES[game_type](ai_difficulty)
                }
            }

            # Create database record
            game_session = GameSession(
                game_id=game.game_id,
                game_type=game_type,
                user_id=user_id,
                ai_difficulty=ai_difficulty
            )
            game_session.set_initial_players([
                {'id': human_player.player_id, 'name': human_player.name, 'is_ai': False},
                {'id': ai_player.player_id, 'name': ai_player.name, 'is_ai': True}
            ])
            session.add(game_session)
            session.commit()

            logger.info(f"Created {game_type} game {game.game_id} for user {user_id}")

            return jsonify({
                'game_id': game.game_id,
                'game_type': game_type,
                'state': game.to_dict(player_perspective=str(user_id)),
                'message': f'{game_type.title()} game created successfully'
            })

    except Exception as e:
        logger.error(f"Error creating game: {e}")
        return jsonify({'error': 'Failed to create game'}), 500


@games_bp.route('/<game_id>/start', methods=['POST'])
def start_game(game_id):
    """Start an existing game."""
    try:
        if game_id not in active_games:
            return jsonify({'error': 'Game not found'}), 404

        game_data = active_games[game_id]
        game = game_data['game']

        if not game.can_start():
            return jsonify({'error': 'Game cannot be started'}), 400

        # Start the game
        game.start_game()

        # Update database
        with next(get_db_session()) as session:
            game_session = session.query(GameSession).filter(
                GameSession.game_id == game_id
            ).first()
            if game_session:
                game_session.started_at = datetime.utcnow()
                game_session.game_state = 'in_progress'
                session.commit()

        logger.info(f"Started game {game_id}")

        return jsonify({
            'game_id': game_id,
            'state': game.to_dict(),
            'message': 'Game started successfully'
        })

    except Exception as e:
        logger.error(f"Error starting game {game_id}: {e}")
        return jsonify({'error': 'Failed to start game'}), 500


@games_bp.route('/<game_id>/move', methods=['POST'])
def make_move(game_id):
    """Make a move in the game."""
    try:
        if game_id not in active_games:
            return jsonify({'error': 'Game not found'}), 404

        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'error': 'No move data provided or invalid JSON'}), 400

        player_id = data.get('player_id')
        move_data = data.get('move_data', {})

        if not player_id:
            return jsonify({'error': 'player_id is required'}), 400

        game_data = active_games[game_id]
        game = game_data['game']

        # Make the move
        move_result = game.make_move(player_id, move_data)

        # Check if AI should make a move
        ai_moves = []
        current_player = game.get_current_player()
        while current_player and current_player.is_ai and game.state.value == 'in_progress':
            ai_id = current_player.player_id
            if ai_id in game_data['ai_instances']:
                ai = game_data['ai_instances'][ai_id]
                ai_move_data = ai.make_move(game, current_player)
                ai_result = game.make_move(ai_id, ai_move_data)
                ai_moves.append({
                    'player_id': ai_id,
                    'move': ai_move_data,
                    'result': ai_result
                })
                current_player = game.get_current_player()
            else:
                break

        # Check if game is finished
        if game.state.value == 'finished':
            _handle_game_completion(game_id, game)

        return jsonify({
            'game_id': game_id,
            'move_result': move_result,
            'ai_moves': ai_moves,
            'state': game.to_dict(player_perspective=player_id),
            'game_finished': game.state.value == 'finished'
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error making move in game {game_id}: {e}")
        return jsonify({'error': 'Failed to make move'}), 500


@games_bp.route('/<game_id>/state', methods=['GET'])
def get_game_state(game_id):
    """Get current game state."""
    try:
        if game_id not in active_games:
            return jsonify({'error': 'Game not found'}), 404

        player_id = request.args.get('player_id')
        game = active_games[game_id]['game']

        return jsonify({
            'game_id': game_id,
            'state': game.to_dict(player_perspective=player_id)
        })

    except Exception as e:
        logger.error(f"Error getting game state {game_id}: {e}")
        return jsonify({'error': 'Failed to get game state'}), 500


@games_bp.route('/<game_id>/rules', methods=['GET'])
def get_game_rules(game_id):
    """Get game rules and configuration."""
    try:
        if game_id not in active_games:
            return jsonify({'error': 'Game not found'}), 404

        game = active_games[game_id]['game']
        rules = game.get_game_rules()

        return jsonify({
            'game_id': game_id,
            'rules': rules
        })

    except Exception as e:
        logger.error(f"Error getting game rules {game_id}: {e}")
        return jsonify({'error': 'Failed to get game rules'}), 500


@games_bp.route('/<game_id>/valid-moves', methods=['GET'])
def get_valid_moves(game_id):
    """Get valid moves for a player."""
    try:
        if game_id not in active_games:
            return jsonify({'error': 'Game not found'}), 404

        player_id = request.args.get('player_id')
        if not player_id:
            return jsonify({'error': 'player_id is required'}), 400

        game = active_games[game_id]['game']
        valid_moves = game.get_valid_moves(player_id)

        return jsonify({
            'game_id': game_id,
            'player_id': player_id,
            'valid_moves': valid_moves
        })

    except Exception as e:
        logger.error(f"Error getting valid moves for game {game_id}: {e}")
        return jsonify({'error': 'Failed to get valid moves'}), 500


@games_bp.route('/<game_id>/abandon', methods=['POST'])
def abandon_game(game_id):
    """Abandon/quit a game."""
    try:
        if game_id not in active_games:
            return jsonify({'error': 'Game not found'}), 404

        data = request.get_json(force=True, silent=True)
        player_id = data.get('player_id') if data else None

        game = active_games[game_id]['game']
        game.cancel_game()

        # Update database
        with next(get_db_session()) as session:
            game_session = session.query(GameSession).filter(
                GameSession.game_id == game_id
            ).first()
            if game_session:
                game_session.finished_at = datetime.utcnow()
                game_session.game_state = 'cancelled'
                session.commit()

        # Remove from active games
        del active_games[game_id]

        logger.info(f"Game {game_id} abandoned by player {player_id}")

        return jsonify({
            'game_id': game_id,
            'message': 'Game abandoned successfully'
        })

    except Exception as e:
        logger.error(f"Error abandoning game {game_id}: {e}")
        return jsonify({'error': 'Failed to abandon game'}), 500


@games_bp.route('/active', methods=['GET'])
def list_active_games():
    """List all active games."""
    try:
        user_id = request.args.get('user_id')
        games_list = []

        for game_id, game_data in active_games.items():
            game = game_data['game']

            # Filter by user if specified
            if user_id:
                user_in_game = any(p.player_id == user_id for p in game.players)
                if not user_in_game:
                    continue

            games_list.append({
                'game_id': game_id,
                'game_type': type(game).__name__.lower().replace('game', ''),
                'state': game.state.value,
                'players': len(game.players),
                'created_at': game.created_at.isoformat()
            })

        return jsonify({
            'active_games': games_list,
            'total_count': len(games_list)
        })

    except Exception as e:
        logger.error(f"Error listing active games: {e}")
        return jsonify({'error': 'Failed to list active games'}), 500


def _handle_game_completion(game_id: str, game) -> None:
    """Handle game completion logic."""
    try:
        with next(get_db_session()) as session:
            game_session = session.query(GameSession).filter(
                GameSession.game_id == game_id
            ).first()

            if not game_session:
                return

            # Update game session
            game_session.finished_at = datetime.utcnow()
            game_session.game_state = 'finished'

            # Determine winner and user result
            winner = game.winner
            if winner:
                game_session.winner_id = int(winner.player_id) if winner.player_id.isdigit() else None
                game_session.user_won = (winner.player_id == str(game_session.user_id))

            # Set final scores
            final_scores = {p.player_id: p.score for p in game.players}
            game_session.set_final_scores(final_scores)
            game_session.user_final_score = final_scores.get(str(game_session.user_id), 0)

            # Calculate experience gained
            base_experience = 50
            if game_session.user_won:
                base_experience += 100

            game_session.experience_gained = base_experience

            # Update user statistics
            user = session.query(User).filter(User.id == game_session.user_id).first()
            if user:
                user.total_games_played += 1
                if game_session.user_won:
                    user.total_games_won += 1
                user.total_experience += base_experience
                user.current_level = (user.total_experience // 1000) + 1

                # Update game-specific statistics
                stats = session.query(UserGameStatistics).filter(
                    UserGameStatistics.user_id == game_session.user_id,
                    UserGameStatistics.game_type == game_session.game_type
                ).first()

                if not stats:
                    stats = UserGameStatistics(
                        user_id=game_session.user_id,
                        game_type=game_session.game_type
                    )
                    session.add(stats)

                duration = game_session.duration_minutes or 0
                stats.update_with_game_result(
                    won=game_session.user_won,
                    score=game_session.user_final_score,
                    duration_minutes=duration,
                    experience=base_experience
                )

            session.commit()
            logger.info(f"Game {game_id} completion handled successfully")

    except Exception as e:
        logger.error(f"Error handling game completion for {game_id}: {e}")


# Clean up completed games periodically (simple implementation)
@games_bp.route('/cleanup', methods=['POST'])
def cleanup_games():
    """Clean up completed/cancelled games from memory."""
    try:
        completed_games = []
        for game_id, game_data in list(active_games.items()):
            game = game_data['game']
            if game.state.value in ['finished', 'cancelled']:
                completed_games.append(game_id)
                del active_games[game_id]

        return jsonify({
            'cleaned_games': completed_games,
            'count': len(completed_games),
            'remaining_active': len(active_games)
        })

    except Exception as e:
        logger.error(f"Error cleaning up games: {e}")
        return jsonify({'error': 'Failed to cleanup games'}), 500