"""
Database models for SoundWound card game platform.

This module defines all database tables and relationships
using SQLAlchemy ORM for user data and game statistics.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()


class User(Base):
    """
    User model for player accounts and authentication.

    Stores user profile information, authentication data,
    and overall statistics across all games.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)  # For future authentication
    display_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_guest = Column(Boolean, default=True)  # Guest accounts don't require authentication

    # Overall statistics
    total_games_played = Column(Integer, default=0)
    total_games_won = Column(Integer, default=0)
    total_experience = Column(Integer, default=0)
    current_level = Column(Integer, default=1)

    # Profile customization
    avatar_url = Column(String(255), nullable=True)
    preferred_theme = Column(String(50), default='default')

    # Relationships
    game_sessions = relationship("GameSession", foreign_keys="[GameSession.user_id]", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    statistics = relationship("UserGameStatistics", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', display_name='{self.display_name}')>"

    @property
    def win_rate(self):
        """Calculate overall win rate percentage."""
        if self.total_games_played == 0:
            return 0.0
        return (self.total_games_won / self.total_games_played) * 100

    def to_dict(self):
        """Convert user to dictionary representation."""
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_games_played': self.total_games_played,
            'total_games_won': self.total_games_won,
            'win_rate': self.win_rate,
            'total_experience': self.total_experience,
            'current_level': self.current_level,
            'avatar_url': self.avatar_url,
            'preferred_theme': self.preferred_theme
        }


class GameSession(Base):
    """
    Game session model for individual game instances.

    Records complete game sessions including participants,
    results, duration, and game-specific data.
    """
    __tablename__ = 'game_sessions'

    id = Column(Integer, primary_key=True)
    game_id = Column(String(50), unique=True, nullable=False, index=True)
    game_type = Column(String(50), nullable=False, index=True)  # 'fool', '101', 'blackjack', 'uno'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Game timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # Game results
    game_state = Column(String(20), default='waiting')  # 'waiting', 'in_progress', 'finished', 'cancelled'
    winner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user_won = Column(Boolean, default=False)
    user_final_score = Column(Integer, default=0)
    experience_gained = Column(Integer, default=0)

    # Game data
    initial_players = Column(Text)  # JSON string of initial player data
    final_scores = Column(Text)  # JSON string of final scores
    game_data = Column(Text)  # JSON string of game-specific data
    ai_difficulty = Column(String(20), default='medium')

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="game_sessions")
    winner = relationship("User", foreign_keys=[winner_id])

    def __repr__(self):
        return f"<GameSession(id={self.id}, game_type='{self.game_type}', state='{self.game_state}')>"

    @property
    def duration_minutes(self):
        """Calculate game duration in minutes."""
        if self.started_at and self.finished_at:
            delta = self.finished_at - self.started_at
            return delta.total_seconds() / 60.0
        return None

    def set_initial_players(self, players_data):
        """Store initial players data as JSON."""
        self.initial_players = json.dumps(players_data)

    def get_initial_players(self):
        """Retrieve initial players data from JSON."""
        if self.initial_players:
            return json.loads(self.initial_players)
        return []

    def set_final_scores(self, scores_data):
        """Store final scores as JSON."""
        self.final_scores = json.dumps(scores_data)

    def get_final_scores(self):
        """Retrieve final scores from JSON."""
        if self.final_scores:
            return json.loads(self.final_scores)
        return {}

    def set_game_data(self, data):
        """Store game-specific data as JSON."""
        self.game_data = json.dumps(data)

    def get_game_data(self):
        """Retrieve game-specific data from JSON."""
        if self.game_data:
            return json.loads(self.game_data)
        return {}

    def to_dict(self):
        """Convert game session to dictionary representation."""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'game_type': self.game_type,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'game_state': self.game_state,
            'winner_id': self.winner_id,
            'user_won': self.user_won,
            'user_final_score': self.user_final_score,
            'experience_gained': self.experience_gained,
            'duration_minutes': self.duration_minutes,
            'ai_difficulty': self.ai_difficulty,
            'initial_players': self.get_initial_players(),
            'final_scores': self.get_final_scores(),
            'game_data': self.get_game_data()
        }


class UserGameStatistics(Base):
    """
    User statistics for specific game types.

    Tracks detailed statistics for each user per game type
    including wins, losses, best scores, and streaks.
    """
    __tablename__ = 'user_game_statistics'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    game_type = Column(String(50), nullable=False, index=True)

    # Basic statistics
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    games_lost = Column(Integer, default=0)

    # Scoring statistics
    best_score = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    total_score = Column(Integer, default=0)

    # Streak statistics
    current_win_streak = Column(Integer, default=0)
    best_win_streak = Column(Integer, default=0)
    current_loss_streak = Column(Integer, default=0)

    # Time statistics
    fastest_win_minutes = Column(Float, nullable=True)
    average_game_duration = Column(Float, default=0.0)
    total_play_time = Column(Float, default=0.0)

    # Experience and progression
    experience_earned = Column(Integer, default=0)
    achievements_count = Column(Integer, default=0)

    # Last updated
    last_played = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="statistics")

    # Unique constraint on user_id + game_type
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    def __repr__(self):
        return f"<UserGameStatistics(user_id={self.user_id}, game_type='{self.game_type}', wins={self.games_won})>"

    @property
    def win_rate(self):
        """Calculate win rate percentage for this game type."""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

    def update_with_game_result(self, won: bool, score: int, duration_minutes: float, experience: int):
        """
        Update statistics with a new game result.

        Args:
            won: Whether the user won the game
            score: Final score achieved
            duration_minutes: Game duration in minutes
            experience: Experience points gained
        """
        self.games_played += 1
        self.total_score += score
        self.average_score = self.total_score / self.games_played
        self.total_play_time += duration_minutes
        self.average_game_duration = self.total_play_time / self.games_played
        self.experience_earned += experience
        self.last_played = datetime.utcnow()

        if won:
            self.games_won += 1
            self.current_win_streak += 1
            self.current_loss_streak = 0
            self.best_win_streak = max(self.best_win_streak, self.current_win_streak)

            # Update best score (game-dependent logic)
            if self.best_score == 0 or self._is_better_score(score, self.best_score):
                self.best_score = score

            # Update fastest win
            if self.fastest_win_minutes is None or duration_minutes < self.fastest_win_minutes:
                self.fastest_win_minutes = duration_minutes
        else:
            self.games_lost += 1
            self.current_win_streak = 0
            self.current_loss_streak += 1

    def _is_better_score(self, new_score: int, current_best: int) -> bool:
        """
        Determine if new score is better than current best.

        Args:
            new_score: New score to compare
            current_best: Current best score

        Returns:
            True if new score is better
        """
        # This logic might need to be game-specific
        # For most games, higher scores are better
        return new_score > current_best

    def to_dict(self):
        """Convert statistics to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'game_type': self.game_type,
            'games_played': self.games_played,
            'games_won': self.games_won,
            'games_lost': self.games_lost,
            'win_rate': self.win_rate,
            'best_score': self.best_score,
            'average_score': self.average_score,
            'current_win_streak': self.current_win_streak,
            'best_win_streak': self.best_win_streak,
            'fastest_win_minutes': self.fastest_win_minutes,
            'average_game_duration': self.average_game_duration,
            'total_play_time': self.total_play_time,
            'experience_earned': self.experience_earned,
            'achievements_count': self.achievements_count,
            'last_played': self.last_played.isoformat() if self.last_played else None
        }


class Achievement(Base):
    """
    Achievement definitions and metadata.

    Defines all available achievements in the system
    with their requirements and reward information.
    """
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # 'general', 'fool', '101', 'blackjack', 'uno'
    difficulty = Column(String(20), default='medium')  # 'easy', 'medium', 'hard', 'legendary'
    points = Column(Integer, default=100)  # Experience points awarded
    icon_url = Column(String(255), nullable=True)

    # Requirements (stored as JSON)
    requirements = Column(Text, nullable=False)  # JSON string of requirements

    # Metadata
    is_hidden = Column(Boolean, default=False)  # Hidden until unlocked
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")

    def __repr__(self):
        return f"<Achievement(id={self.id}, code='{self.code}', name='{self.name}')>"

    def set_requirements(self, requirements_data):
        """Store requirements as JSON."""
        self.requirements = json.dumps(requirements_data)

    def get_requirements(self):
        """Retrieve requirements from JSON."""
        if self.requirements:
            return json.loads(self.requirements)
        return {}

    def to_dict(self):
        """Convert achievement to dictionary representation."""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'points': self.points,
            'icon_url': self.icon_url,
            'requirements': self.get_requirements(),
            'is_hidden': self.is_hidden,
            'is_active': self.is_active
        }


class UserAchievement(Base):
    """
    User achievement unlocks and progress.

    Tracks which achievements users have unlocked
    and their progress toward locked achievements.
    """
    __tablename__ = 'user_achievements'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), nullable=False)

    # Progress tracking
    is_unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)
    progress_data = Column(Text, nullable=True)  # JSON string for progress tracking

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    # Unique constraint on user_id + achievement_id
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id}, unlocked={self.is_unlocked})>"

    def set_progress_data(self, progress_data):
        """Store progress data as JSON."""
        self.progress_data = json.dumps(progress_data)

    def get_progress_data(self):
        """Retrieve progress data from JSON."""
        if self.progress_data:
            return json.loads(self.progress_data)
        return {}

    def unlock(self):
        """Mark achievement as unlocked."""
        self.is_unlocked = True
        self.unlocked_at = datetime.utcnow()

    def to_dict(self):
        """Convert user achievement to dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'is_unlocked': self.is_unlocked,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'progress_data': self.get_progress_data(),
            'achievement': self.achievement.to_dict() if self.achievement else None
        }