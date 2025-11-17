"""
Statistics API routes for SoundWound platform.

This module handles game statistics, leaderboards,
and performance analytics for users.
"""

from flask import Blueprint, request, jsonify
import logging

from ...database.database import get_db_session
from ...database.models import User, UserGameStatistics, GameSession

logger = logging.getLogger(__name__)
statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_statistics(user_id):
    """Get comprehensive statistics for a user."""
    try:
        game_type = request.args.get('game_type')

        with next(get_db_session()) as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Get game-specific statistics
            query = session.query(UserGameStatistics).filter(
                UserGameStatistics.user_id == user_id
            )

            if game_type:
                query = query.filter(UserGameStatistics.game_type == game_type)

            stats = query.all()

            return jsonify({
                'user_id': user_id,
                'overall_stats': {
                    'total_games_played': user.total_games_played,
                    'total_games_won': user.total_games_won,
                    'win_rate': user.win_rate,
                    'total_experience': user.total_experience,
                    'current_level': user.current_level
                },
                'game_statistics': [stat.to_dict() for stat in stats]
            })

    except Exception as e:
        logger.error(f"Error getting statistics for user {user_id}: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500


@statistics_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard for specified criteria."""
    try:
        game_type = request.args.get('game_type')
        metric = request.args.get('metric', 'win_rate')
        limit = int(request.args.get('limit', 10))

        with next(get_db_session()) as session:
            if game_type:
                # Game-specific leaderboard
                query = session.query(UserGameStatistics).join(User).filter(
                    UserGameStatistics.game_type == game_type,
                    UserGameStatistics.games_played >= 5  # Minimum games for ranking
                )

                if metric == 'win_rate':
                    query = query.order_by(UserGameStatistics.games_won.desc())
                elif metric == 'games_won':
                    query = query.order_by(UserGameStatistics.games_won.desc())
                elif metric == 'best_score':
                    query = query.order_by(UserGameStatistics.best_score.desc())

                stats = query.limit(limit).all()
                leaderboard = []

                for i, stat in enumerate(stats):
                    leaderboard.append({
                        'rank': i + 1,
                        'user': stat.user.to_dict(),
                        'metric_value': getattr(stat, metric),
                        'games_played': stat.games_played,
                        'win_rate': stat.win_rate
                    })

            else:
                # Overall leaderboard
                query = session.query(User).filter(
                    User.total_games_played >= 5
                ).order_by(User.total_games_won.desc())

                users = query.limit(limit).all()
                leaderboard = []

                for i, user in enumerate(users):
                    leaderboard.append({
                        'rank': i + 1,
                        'user': user.to_dict(),
                        'metric_value': user.total_games_won,
                        'games_played': user.total_games_played,
                        'win_rate': user.win_rate
                    })

            return jsonify({
                'leaderboard': leaderboard,
                'game_type': game_type,
                'metric': metric,
                'total_entries': len(leaderboard)
            })

    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        return jsonify({'error': 'Failed to get leaderboard'}), 500