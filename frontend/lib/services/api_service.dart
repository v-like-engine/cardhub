import 'dart:convert';
import 'package:http/http.dart' as http;

/// Service for communicating with the Python backend API.
///
/// Handles all HTTP requests to the Flask backend server and
/// provides methods for authentication, game operations, and statistics.
class ApiService {
  // Base URL for the backend API
  // For Windows desktop: use 127.0.0.1
  // For Android emulator: use 10.0.2.2
  // For physical device on same network: use actual IP address
  static const String _baseUrl = 'http://127.0.0.1:5000';

  /// Alternative base URLs for different platforms
  /// Use this if running on Android emulator
  static const String _androidEmulatorUrl = 'http://10.0.2.2:5000';

  final http.Client _client;
  String _currentBaseUrl = _baseUrl;

  ApiService({http.Client? client}) : _client = client ?? http.Client();

  /// Switch to Android emulator URL
  void useAndroidEmulator() {
    _currentBaseUrl = _androidEmulatorUrl;
  }

  /// Set custom base URL (for local network testing)
  void setBaseUrl(String url) {
    _currentBaseUrl = url;
  }

  /// Get current base URL
  String get baseUrl => _currentBaseUrl;

  /// Checks if the backend server is running and healthy
  Future<bool> healthCheck() async {
    try {
      final response = await _client
          .get(Uri.parse('$_currentBaseUrl/api/health'))
          .timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['status'] == 'healthy';
      }
      return false;
    } catch (e) {
      print('Health check failed: $e');
      return false;
    }
  }

  /// Gets API information
  Future<Map<String, dynamic>?> getApiInfo() async {
    try {
      final response = await _client.get(Uri.parse('$_currentBaseUrl/api/info'));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Failed to get API info: $e');
      return null;
    }
  }

  /// Creates a new game session
  Future<Map<String, dynamic>?> createGame({
    required String gameType,
    required int numPlayers,
    required int numAiPlayers,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_currentBaseUrl/api/games/create'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'game_type': gameType,
          'num_players': numPlayers,
          'num_ai_players': numAiPlayers,
        }),
      );

      if (response.statusCode == 201) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Failed to create game: $e');
      return null;
    }
  }

  /// Gets current game state
  Future<Map<String, dynamic>?> getGameState(String gameId) async {
    try {
      final response = await _client.get(
        Uri.parse('$_currentBaseUrl/api/games/$gameId/state'),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Failed to get game state: $e');
      return null;
    }
  }

  /// Makes a move in a game
  Future<Map<String, dynamic>?> makeMove({
    required String gameId,
    required int playerId,
    required Map<String, dynamic> moveData,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_currentBaseUrl/api/games/$gameId/move'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'player_id': playerId,
          'move': moveData,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Failed to make move: $e');
      return null;
    }
  }

  /// Registers a new user
  Future<Map<String, dynamic>?> register({
    required String username,
    required String email,
    required String password,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_currentBaseUrl/api/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 201) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Failed to register: $e');
      return null;
    }
  }

  /// Logs in a user
  Future<Map<String, dynamic>?> login({
    required String username,
    required String password,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_currentBaseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Failed to login: $e');
      return null;
    }
  }

  /// Gets user statistics
  Future<Map<String, dynamic>?> getUserStats(String userId) async {
    try {
      final response = await _client.get(
        Uri.parse('$_currentBaseUrl/api/statistics/user/$userId'),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Failed to get user stats: $e');
      return null;
    }
  }

  /// Gets game-specific statistics for a user
  Future<Map<String, dynamic>?> getGameStats(String userId, String gameType) async {
    try {
      final response = await _client.get(
        Uri.parse('$_currentBaseUrl/api/statistics/user/$userId/game/$gameType'),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      print('Failed to get game stats: $e');
      return null;
    }
  }

  /// Disposes the HTTP client
  void dispose() {
    _client.close();
  }
}
