import 'package:flutter/material.dart';

/// Gameplay screen for playing card games.
///
/// This screen will host the actual game interface and will be
/// integrated with the Python backend for game logic and AI.
class GameplayScreen extends StatefulWidget {
  final String gameType;
  final bool isAI;

  const GameplayScreen({
    Key? key,
    required this.gameType,
    required this.isAI,
  }) : super(key: key);

  @override
  _GameplayScreenState createState() => _GameplayScreenState();
}

class _GameplayScreenState extends State<GameplayScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF0F4C3A),
              Color(0xFF2D1B0F),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header with back button and game info
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(
                        Icons.arrow_back,
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                    const SizedBox(width: 20),
                    Expanded(
                      child: Text(
                        '${_getGameDisplayName(widget.gameType)} ${widget.isAI ? "vs AI" : ""}',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ),
                    IconButton(
                      onPressed: () => _showGameMenu(),
                      icon: const Icon(
                        Icons.menu,
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                  ],
                ),
              ),

              // Game area placeholder
              Expanded(
                child: Center(
                  child: Container(
                    padding: const EdgeInsets.all(40),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: Colors.white.withOpacity(0.2),
                        width: 2,
                      ),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _getGameIcon(widget.gameType),
                          size: 80,
                          color: _getGameColor(widget.gameType),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          'Game Interface',
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 15),
                        Text(
                          'Coming Soon!',
                          style: TextStyle(
                            fontSize: 24,
                            color: Colors.white70,
                          ),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          'The gameplay interface will be implemented\nwith the Python backend integration.',
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.white60,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              // Bottom action bar placeholder
              Container(
                padding: const EdgeInsets.all(20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildActionButton('Draw', Icons.add, () {}),
                    _buildActionButton('Play', Icons.play_arrow, () {}),
                    _buildActionButton('Pass', Icons.skip_next, () {}),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Shows the in-game menu
  void _showGameMenu() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF2D1B0F),
          title: const Text(
            'Game Menu',
            style: TextStyle(color: Colors.white),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildMenuOption('Rules', Icons.help_outline, () {
                Navigator.of(context).pop();
                // Navigate to rules screen
              }),
              _buildMenuOption('Statistics', Icons.bar_chart, () {
                Navigator.of(context).pop();
                // Navigate to statistics screen
              }),
              _buildMenuOption('Settings', Icons.settings, () {
                Navigator.of(context).pop();
                // Navigate to settings screen
              }),
              _buildMenuOption('Exit Game', Icons.exit_to_app, () {
                Navigator.of(context).pop();
                Navigator.of(context).pop();
              }),
            ],
          ),
        );
      },
    );
  }

  /// Builds a menu option for the game menu
  Widget _buildMenuOption(String title, IconData icon, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon, color: Colors.white70),
      title: Text(
        title,
        style: const TextStyle(color: Colors.white),
      ),
      onTap: onTap,
    );
  }

  /// Builds an action button for the bottom bar
  Widget _buildActionButton(String label, IconData icon, VoidCallback onPressed) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        backgroundColor: _getGameColor(widget.gameType),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
    );
  }

  String _getGameDisplayName(String gameType) {
    switch (gameType) {
      case 'fool':
        return 'Fool';
      case '101':
        return '101';
      case 'blackjack':
        return 'BlackJack';
      case 'uno':
        return 'Uno';
      default:
        return gameType.toUpperCase();
    }
  }

  Color _getGameColor(String gameType) {
    switch (gameType) {
      case 'fool':
        return const Color(0xFFD32F2F);
      case '101':
        return const Color(0xFF1976D2);
      case 'blackjack':
        return const Color(0xFF388E3C);
      case 'uno':
        return const Color(0xFFF57C00);
      default:
        return Colors.grey;
    }
  }

  IconData _getGameIcon(String gameType) {
    switch (gameType) {
      case 'fool':
        return Icons.casino;
      case '101':
        return Icons.looks_one;
      case 'blackjack':
        return Icons.favorite;
      case 'uno':
        return Icons.color_lens;
      default:
        return Icons.games;
    }
  }
}