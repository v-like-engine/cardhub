"""
Database connection and session management.

This module handles database initialization, connection pooling,
and provides session management for the SoundWound application.
"""

import os
from typing import Optional, Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging

from .models import Base, User, GameSession, UserGameStatistics, Achievement, UserAchievement

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database manager for SoundWound application.

    Handles database initialization, connection management,
    and provides convenient session access methods.
    """

    def __init__(self, database_url: Optional[str] = None, echo: bool = False):
        """
        Initialize database manager.

        Args:
            database_url: Database connection URL (defaults to SQLite)
            echo: Whether to echo SQL statements for debugging
        """
        if database_url is None:
            # Default to SQLite database in backend directory
            db_path = os.path.join(os.path.dirname(__file__), '..', 'soundwound.db')
            database_url = f"sqlite:///{db_path}"

        # Configure engine based on database type
        if database_url.startswith('sqlite'):
            # SQLite-specific configuration
            self.engine = create_engine(
                database_url,
                echo=echo,
                poolclass=StaticPool,
                connect_args={
                    'check_same_thread': False,
                    'timeout': 20
                }
            )
            # Enable foreign key constraints for SQLite
            event.listen(self.engine, "connect", self._set_sqlite_pragma)
        else:
            # PostgreSQL/MySQL configuration
            self.engine = create_engine(
                database_url,
                echo=echo,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True
            )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        self.database_url = database_url
        self._initialized = False

    def _set_sqlite_pragma(self, dbapi_connection, connection_record):
        """Enable foreign key constraints for SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def initialize_database(self, drop_existing: bool = False) -> None:
        """
        Initialize the database schema.

        Args:
            drop_existing: Whether to drop existing tables first
        """
        try:
            if drop_existing:
                logger.warning("Dropping existing database tables")
                Base.metadata.drop_all(bind=self.engine)

            # Create all tables
            Base.metadata.create_all(bind=self.engine)

            # Initialize default data
            self._initialize_default_data()

            self._initialized = True
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def _initialize_default_data(self) -> None:
        """Initialize default achievements and other reference data."""
        with self.get_session() as session:
            # Check if achievements already exist
            existing_achievements = session.query(Achievement).count()
            if existing_achievements > 0:
                logger.info("Default achievements already exist, skipping initialization")
                return

            # Create default achievements
            default_achievements = [
                # General achievements
                {
                    'code': 'first_game',
                    'name': 'First Steps',
                    'description': 'Play your first game',
                    'category': 'general',
                    'difficulty': 'easy',
                    'points': 50,
                    'requirements': {'games_played': 1}
                },
                {
                    'code': 'first_win',
                    'name': 'Victory!',
                    'description': 'Win your first game',
                    'category': 'general',
                    'difficulty': 'easy',
                    'points': 100,
                    'requirements': {'games_won': 1}
                },
                {
                    'code': 'ten_games',
                    'name': 'Getting Started',
                    'description': 'Play 10 games',
                    'category': 'general',
                    'difficulty': 'easy',
                    'points': 200,
                    'requirements': {'games_played': 10}
                },
                {
                    'code': 'hundred_games',
                    'name': 'Experienced Player',
                    'description': 'Play 100 games',
                    'category': 'general',
                    'difficulty': 'medium',
                    'points': 500,
                    'requirements': {'games_played': 100}
                },
                {
                    'code': 'win_streak_5',
                    'name': 'Hot Streak',
                    'description': 'Win 5 games in a row',
                    'category': 'general',
                    'difficulty': 'medium',
                    'points': 300,
                    'requirements': {'win_streak': 5}
                },

                # Fool achievements
                {
                    'code': 'fool_first_win',
                    'name': 'Not the Fool',
                    'description': 'Win your first Fool game',
                    'category': 'fool',
                    'difficulty': 'easy',
                    'points': 100,
                    'requirements': {'game_type': 'fool', 'games_won': 1}
                },
                {
                    'code': 'fool_master',
                    'name': 'Fool Master',
                    'description': 'Win 50 Fool games',
                    'category': 'fool',
                    'difficulty': 'hard',
                    'points': 800,
                    'requirements': {'game_type': 'fool', 'games_won': 50}
                },

                # 101 achievements
                {
                    'code': 'one_oh_one_first_win',
                    'name': 'Perfect Score',
                    'description': 'Win your first 101 game',
                    'category': '101',
                    'difficulty': 'easy',
                    'points': 100,
                    'requirements': {'game_type': '101', 'games_won': 1}
                },
                {
                    'code': 'one_oh_one_exact',
                    'name': 'Exactly 101',
                    'description': 'Win a 101 game with exactly 101 points',
                    'category': '101',
                    'difficulty': 'medium',
                    'points': 250,
                    'requirements': {'game_type': '101', 'exact_score': 101}
                },

                # BlackJack achievements
                {
                    'code': 'blackjack_first_win',
                    'name': 'Beat the House',
                    'description': 'Win your first BlackJack game',
                    'category': 'blackjack',
                    'difficulty': 'easy',
                    'points': 100,
                    'requirements': {'game_type': 'blackjack', 'games_won': 1}
                },
                {
                    'code': 'blackjack_natural',
                    'name': 'Natural 21',
                    'description': 'Get a BlackJack (21 with 2 cards)',
                    'category': 'blackjack',
                    'difficulty': 'medium',
                    'points': 200,
                    'requirements': {'game_type': 'blackjack', 'blackjack_count': 1}
                },

                # Uno achievements
                {
                    'code': 'uno_first_win',
                    'name': 'Uno Champion',
                    'description': 'Win your first Uno game',
                    'category': 'uno',
                    'difficulty': 'easy',
                    'points': 100,
                    'requirements': {'game_type': 'uno', 'games_won': 1}
                },
                {
                    'code': 'uno_perfect_hand',
                    'name': 'Perfect Hand',
                    'description': 'Win an Uno game without drawing any cards',
                    'category': 'uno',
                    'difficulty': 'hard',
                    'points': 500,
                    'requirements': {'game_type': 'uno', 'no_draws': True}
                },
            ]

            for achievement_data in default_achievements:
                achievement = Achievement(
                    code=achievement_data['code'],
                    name=achievement_data['name'],
                    description=achievement_data['description'],
                    category=achievement_data['category'],
                    difficulty=achievement_data['difficulty'],
                    points=achievement_data['points']
                )
                achievement.set_requirements(achievement_data['requirements'])
                session.add(achievement)

            session.commit()
            logger.info(f"Initialized {len(default_achievements)} default achievements")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session using context manager.

        Yields:
            Database session that will be automatically closed
        """
        session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_instance(self) -> Session:
        """
        Get a database session instance.

        Returns:
            Database session (must be closed manually)
        """
        return self.SessionLocal()

    def health_check(self) -> bool:
        """
        Perform a health check on the database connection.

        Returns:
            True if database is accessible, False otherwise
        """
        try:
            with self.get_session() as session:
                # Simple query to test connection
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get database statistics.

        Returns:
            Dictionary containing database statistics
        """
        try:
            with self.get_session() as session:
                stats = {
                    'total_users': session.query(User).count(),
                    'active_users': session.query(User).filter(User.is_active == True).count(),
                    'total_game_sessions': session.query(GameSession).count(),
                    'finished_games': session.query(GameSession).filter(GameSession.game_state == 'finished').count(),
                    'total_achievements': session.query(Achievement).count(),
                    'database_url': self.database_url,
                    'is_sqlite': self.database_url.startswith('sqlite')
                }
                return stats
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the database (SQLite only).

        Args:
            backup_path: Path where backup should be saved

        Returns:
            True if backup was successful, False otherwise
        """
        if not self.database_url.startswith('sqlite'):
            logger.warning("Database backup only supported for SQLite")
            return False

        try:
            import shutil
            # Extract database path from URL
            db_path = self.database_url.replace('sqlite:///', '')
            shutil.copy2(db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False

    def close(self) -> None:
        """Close database connections and cleanup."""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        Database manager instance
    """
    global db_manager
    if db_manager is None:
        # Initialize with default settings
        db_manager = DatabaseManager()
        db_manager.initialize_database()
    return db_manager


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency function for getting database sessions.

    Yields:
        Database session
    """
    manager = get_database_manager()
    with manager.get_session() as session:
        yield session