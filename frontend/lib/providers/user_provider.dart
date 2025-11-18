import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Manages user data including statistics, achievements, and profile information.
///
/// This provider handles user authentication, statistics tracking,
/// and persistence of user-related data across sessions.
class UserProvider with ChangeNotifier {
  String _username = 'Player';
  int _totalGamesPlayed = 0;
  int _totalGamesWon = 0;
  Map<String, int> _gameSpecificWins = {};
  Map<String, int> _gameSpecificPlayed = {};
  List<String> _achievements = [];
  int _totalExperience = 0;
  int _currentLevel = 1;

  /// Current username
  String get username => _username;

  /// Total games played across all game types
  int get totalGamesPlayed => _totalGamesPlayed;

  /// Total games won across all game types
  int get totalGamesWon => _totalGamesWon;

  /// Win rate as percentage
  double get winRate => _totalGamesPlayed > 0 ? (_totalGamesWon / _totalGamesPlayed) * 100 : 0.0;

  /// Game-specific win counts
  Map<String, int> get gameSpecificWins => Map.from(_gameSpecificWins);

  /// Game-specific play counts
  Map<String, int> get gameSpecificPlayed => Map.from(_gameSpecificPlayed);

  /// List of unlocked achievements
  List<String> get achievements => List.from(_achievements);

  /// Total experience points
  int get totalExperience => _totalExperience;

  /// Current player level
  int get currentLevel => _currentLevel;

  /// Experience needed for next level
  int get experienceForNextLevel => (_currentLevel * 1000) - (_totalExperience % 1000);

  /// Initializes user data from persistent storage
  Future<void> loadUserData() async {
    final prefs = await SharedPreferences.getInstance();
    _username = prefs.getString('username') ?? 'Player';
    _totalGamesPlayed = prefs.getInt('totalGamesPlayed') ?? 0;
    _totalGamesWon = prefs.getInt('totalGamesWon') ?? 0;
    _totalExperience = prefs.getInt('totalExperience') ?? 0;
    _currentLevel = (_totalExperience ~/ 1000) + 1;

    // Load game-specific statistics
    final gameTypes = ['fool', '101', 'blackjack', 'uno'];
    for (String game in gameTypes) {
      _gameSpecificWins[game] = prefs.getInt('${game}_wins') ?? 0;
      _gameSpecificPlayed[game] = prefs.getInt('${game}_played') ?? 0;
    }

    // Load achievements
    _achievements = prefs.getStringList('achievements') ?? [];
    notifyListeners();
  }

  /// Updates username and saves to storage
  Future<void> setUsername(String name) async {
    _username = name;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('username', name);
    notifyListeners();
  }

  /// Records a game result and updates statistics
  Future<void> recordGameResult(String gameType, bool won, int experienceGained) async {
    _totalGamesPlayed++;
    _gameSpecificPlayed[gameType] = (_gameSpecificPlayed[gameType] ?? 0) + 1;

    if (won) {
      _totalGamesWon++;
      _gameSpecificWins[gameType] = (_gameSpecificWins[gameType] ?? 0) + 1;
    }

    _totalExperience += experienceGained;
    int newLevel = (_totalExperience ~/ 1000) + 1;
    if (newLevel > _currentLevel) {
      _currentLevel = newLevel;
      await _checkLevelAchievements();
    }

    await _saveStatistics();
    await _checkGameAchievements(gameType);
    notifyListeners();
  }

  /// Adds a new achievement
  Future<void> addAchievement(String achievement) async {
    if (!_achievements.contains(achievement)) {
      _achievements.add(achievement);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setStringList('achievements', _achievements);
      notifyListeners();
    }
  }

  /// Gets win rate for specific game
  double getGameWinRate(String gameType) {
    int played = _gameSpecificPlayed[gameType] ?? 0;
    int won = _gameSpecificWins[gameType] ?? 0;
    return played > 0 ? (won / played) * 100 : 0.0;
  }

  /// Saves statistics to persistent storage
  Future<void> _saveStatistics() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('totalGamesPlayed', _totalGamesPlayed);
    await prefs.setInt('totalGamesWon', _totalGamesWon);
    await prefs.setInt('totalExperience', _totalExperience);

    for (String game in _gameSpecificWins.keys) {
      await prefs.setInt('${game}_wins', _gameSpecificWins[game]!);
      await prefs.setInt('${game}_played', _gameSpecificPlayed[game]!);
    }
  }

  /// Checks and awards level-based achievements
  Future<void> _checkLevelAchievements() async {
    if (_currentLevel >= 5) await addAchievement('Novice Player');
    if (_currentLevel >= 10) await addAchievement('Experienced Player');
    if (_currentLevel >= 20) await addAchievement('Expert Player');
    if (_currentLevel >= 50) await addAchievement('Master Player');
  }

  /// Checks and awards game-specific achievements
  Future<void> _checkGameAchievements(String gameType) async {
    int wins = _gameSpecificWins[gameType] ?? 0;
    int played = _gameSpecificPlayed[gameType] ?? 0;

    if (wins >= 1) await addAchievement('First ${gameType.toUpperCase()} Win');
    if (wins >= 10) await addAchievement('${gameType.toUpperCase()} Enthusiast');
    if (wins >= 50) await addAchievement('${gameType.toUpperCase()} Master');
    if (played >= 100) await addAchievement('${gameType.toUpperCase()} Veteran');
  }
}