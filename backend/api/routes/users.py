"""
User management API routes for SoundWound platform.

This module handles user profile management, user lookup,
and user-related operations.
"""

from flask import Blueprint, request, jsonify
import logging

from ...database.database import get_db_session
from ...database.models import User, UserAchievement, Achievement

logger = logging.getLogger(__name__)
users_bp = Blueprint('users', __name__)


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile information."""
    try:
        with next(get_db_session()) as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            return jsonify({'user': user.to_dict()})

    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return jsonify({'error': 'Failed to get user'}), 500


@users_bp.route('/<int:user_id>/achievements', methods=['GET'])
def get_user_achievements(user_id):
    """Get user achievements."""
    try:
        with next(get_db_session()) as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            achievements = session.query(UserAchievement).join(Achievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.is_unlocked == True
            ).all()

            return jsonify({
                'user_id': user_id,
                'achievements': [achievement.to_dict() for achievement in achievements],
                'total_count': len(achievements)
            })

    except Exception as e:
        logger.error(f"Error getting achievements for user {user_id}: {e}")
        return jsonify({'error': 'Failed to get achievements'}), 500