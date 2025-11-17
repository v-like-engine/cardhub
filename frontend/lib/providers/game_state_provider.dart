import 'package:flutter/material.dart';

/// Manages the overall game state including current game, players, and game flow.
///
/// This provider handles transitions between different game states,
/// manages player information, and coordinates with the backend game engine.
class GameStateProvider with ChangeNotifier {
  String _currentGame = '';
  List<String> _players = [];
  Map<String, dynamic> _gameData = {};
  bool _isGameActive = false;
  String _currentPlayer = '';

  /// Currently selected game type (fool, 101, blackjack, uno)
  String get currentGame => _currentGame;

  /// List of players in the current game
  List<String> get players => _players;

  /// Current game data including cards, scores, etc.
  Map<String, dynamic> get gameData => _gameData;

  /// Whether a game is currently active
  bool get isGameActive => _isGameActive;

  /// Current player's turn
  String get currentPlayer => _currentPlayer;

  /// Sets the current game type and initializes game state
  void setCurrentGame(String game) {
    _currentGame = game;
    _resetGameState();
    notifyListeners();
  }

  /// Adds a player to the current game
  void addPlayer(String playerName) {
    if (!_players.contains(playerName)) {
      _players.add(playerName);
      notifyListeners();
    }
  }

  /// Removes a player from the current game
  void removePlayer(String playerName) {
    _players.remove(playerName);
    notifyListeners();
  }

  /// Starts a new game with current players
  void startGame() {
    _isGameActive = true;
    _currentPlayer = _players.isNotEmpty ? _players[0] : '';
    notifyListeners();
  }

  /// Ends the current game and resets state
  void endGame() {
    _isGameActive = false;
    _resetGameState();
    notifyListeners();
  }

  /// Updates game data with new information from backend
  void updateGameData(Map<String, dynamic> newData) {
    _gameData = newData;
    notifyListeners();
  }

  /// Sets the current player's turn
  void setCurrentPlayer(String player) {
    _currentPlayer = player;
    notifyListeners();
  }

  /// Resets all game state to initial values
  void _resetGameState() {
    _players.clear();
    _gameData.clear();
    _isGameActive = false;
    _currentPlayer = '';
  }
}