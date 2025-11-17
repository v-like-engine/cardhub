"""
Authentication API routes for SoundWound platform.

This module handles user authentication, registration,
and session management for guest and registered users.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import uuid

from ...database.database import get_db_session
from ...database.models import User

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/guest', methods=['POST'])
def create_guest_user():
    """Create a guest user account."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        display_name = data.get('display_name', 'Guest Player')

        # Generate unique username for guest
        guest_username = f"guest_{uuid.uuid4().hex[:8]}"

        with next(get_db_session()) as session:
            # Create guest user
            user = User(
                username=guest_username,
                display_name=display_name,
                is_guest=True,
                is_active=True,
                last_login=datetime.utcnow()
            )
            session.add(user)
            session.commit()

            logger.info(f"Created guest user {user.id} with username {guest_username}")

            return jsonify({
                'user': user.to_dict(),
                'message': 'Guest user created successfully'
            })

    except Exception as e:
        logger.error(f"Error creating guest user: {e}")
        return jsonify({'error': 'Failed to create guest user'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with username (simplified for demo)."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'error': 'No data provided or invalid JSON'}), 400

        username = data.get('username')
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        with next(get_db_session()) as session:
            user = session.query(User).filter(
                User.username == username,
                User.is_active == True
            ).first()

            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Update last login
            user.last_login = datetime.utcnow()
            session.commit()

            logger.info(f"User {user.id} logged in")

            return jsonify({
                'user': user.to_dict(),
                'message': 'Login successful'
            })

    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'error': 'No data provided or invalid JSON'}), 400

        username = data.get('username')
        display_name = data.get('display_name')
        email = data.get('email')

        if not username or not display_name:
            return jsonify({'error': 'Username and display_name are required'}), 400

        with next(get_db_session()) as session:
            # Check if username already exists
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 409

            # Check if email already exists (if provided)
            if email:
                existing_email = session.query(User).filter(User.email == email).first()
                if existing_email:
                    return jsonify({'error': 'Email already exists'}), 409

            # Create new user
            user = User(
                username=username,
                display_name=display_name,
                email=email,
                is_guest=False,
                is_active=True,
                last_login=datetime.utcnow()
            )
            session.add(user)
            session.commit()

            logger.info(f"Registered new user {user.id} with username {username}")

            return jsonify({
                'user': user.to_dict(),
                'message': 'User registered successfully'
            })

    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/validate/<int:user_id>', methods=['GET'])
def validate_user(user_id):
    """Validate that a user exists and is active."""
    try:
        with next(get_db_session()) as session:
            user = session.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()

            if not user:
                return jsonify({'valid': False, 'error': 'User not found'}), 404

            return jsonify({
                'valid': True,
                'user': user.to_dict()
            })

    except Exception as e:
        logger.error(f"Error validating user {user_id}: {e}")
        return jsonify({'error': 'Validation failed'}), 500


@auth_bp.route('/update-profile', methods=['PUT'])
def update_profile():
    """Update user profile information."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({'error': 'No data provided or invalid JSON'}), 400

        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        with next(get_db_session()) as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Update allowed fields
            if 'display_name' in data:
                user.display_name = data['display_name']
            if 'email' in data:
                user.email = data['email']
            if 'avatar_url' in data:
                user.avatar_url = data['avatar_url']
            if 'preferred_theme' in data:
                user.preferred_theme = data['preferred_theme']

            session.commit()

            logger.info(f"Updated profile for user {user_id}")

            return jsonify({
                'user': user.to_dict(),
                'message': 'Profile updated successfully'
            })

    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return jsonify({'error': 'Profile update failed'}), 500