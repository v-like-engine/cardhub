import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../providers/game_state_provider.dart';
import '../widgets/game_card.dart';
import 'game_menu_screen.dart';

/// Game selection screen showing available games as animated cards.
///
/// Features card reshuffling animation and displays four games:
/// Fool, 101, BlackJack, and Uno, plus a Back to Menu option.
class GameSelectionScreen extends StatefulWidget {
  @override
  _GameSelectionScreenState createState() => _GameSelectionScreenState();
}

class _GameSelectionScreenState extends State<GameSelectionScreen>
    with TickerProviderStateMixin {
  late AnimationController _reshuffleController;
  late AnimationController _dealController;
  final List<String> _games = ['fool', '101', 'blackjack', 'uno'];
  final List<String> _gameDisplayNames = ['Fool', '101', 'BlackJack', 'Uno'];
  final List<String> _gameDescriptions = [
    'Classic Russian card game',
    'Fast-paced number game',
    'Beat the dealer',
    'Colorful strategy game'
  ];

  @override
  void initState() {
    super.initState();
    _reshuffleController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    _dealController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    // Start the dealing animation
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _dealController.forward();
    });
  }

  @override
  void dispose() {
    _reshuffleController.dispose();
    _dealController.dispose();
    super.dispose();
  }

  /// Handles game card selection and navigation
  void _onGameSelected(String gameType) async {
    await _reshuffleController.forward();

    if (gameType == 'back') {
      Navigator.pop(context);
    } else {
      context.read<GameStateProvider>().setCurrentGame(gameType);
      Navigator.push(
        context,
        PageRouteBuilder(
          pageBuilder: (context, animation, secondaryAnimation) =>
              GameMenuScreen(gameType: gameType),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(
              opacity: animation,
              child: ScaleTransition(
                scale: Tween<double>(begin: 0.8, end: 1.0).animate(
                  CurvedAnimation(parent: animation, curve: Curves.easeOut),
                ),
                child: child,
              ),
            );
          },
          transitionDuration: const Duration(milliseconds: 600),
        ),
      ).then((_) {
        _reshuffleController.reset();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;

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
        child: Stack(
          children: [
            // Background texture
            Opacity(
              opacity: 0.1,
              child: Container(
                decoration: const BoxDecoration(
                  image: DecorationImage(
                    image: AssetImage('assets/images/felt_texture.png'),
                    fit: BoxFit.cover,
                  ),
                ),
              ),
            ),

            // Back button
            Positioned(
              top: 50,
              left: 20,
              child: IconButton(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(
                  Icons.arrow_back,
                  color: Colors.white,
                  size: 30,
                ),
              ),
            ),

            // Main content
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Title
                  Text(
                    'Select a Game',
                    style: TextStyle(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      shadows: [
                        Shadow(
                          offset: const Offset(3, 3),
                          blurRadius: 6,
                          color: Colors.black.withOpacity(0.7),
                        ),
                      ],
                    ),
                  ).animate().fadeIn(duration: 800.ms).slideY(begin: -0.3),

                  const SizedBox(height: 60),

                  // Game cards
                  _buildGameCards(screenSize),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Builds the game selection cards with dealing animation
  Widget _buildGameCards(Size screenSize) {
    return SizedBox(
      height: 300,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: EdgeInsets.symmetric(horizontal: 20),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Back to Menu card (first in hand)
            AnimatedBuilder(
              animation: _dealController,
              builder: (context, child) {
                double progress = _dealController.value;
                double cardProgress = (progress * 5).clamp(0.0, 1.0);

                return Transform.translate(
                  offset: Offset(0, 50 * (1 - cardProgress)),
                  child: Opacity(
                    opacity: cardProgress,
                    child: GameCard(
                      title: 'Back to Menu',
                      description: 'Return to main menu',
                      onTap: () => _onGameSelected('back'),
                      color: Colors.grey,
                      icon: Icons.arrow_back,
                    ).animate(controller: _reshuffleController).scale(
                      begin: const Offset(1.0, 1.0),
                      end: const Offset(0.0, 0.0),
                      curve: Curves.easeInOut,
                    ).then().scale(
                      begin: const Offset(0.0, 0.0),
                      end: const Offset(1.0, 1.0),
                      curve: Curves.elasticOut,
                    ),
                  ),
                );
              },
            ),

            const SizedBox(width: 20),

            // Game cards
            ...List.generate(_games.length, (index) {
              return AnimatedBuilder(
                animation: _dealController,
                builder: (context, child) {
                  double progress = _dealController.value;
                  double cardProgress = ((progress * 5) - (index + 1)).clamp(0.0, 1.0);

                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 10),
                    child: Transform.translate(
                      offset: Offset(0, 50 * (1 - cardProgress)),
                      child: Opacity(
                        opacity: cardProgress,
                        child: GameCard(
                          title: _gameDisplayNames[index],
                          description: _gameDescriptions[index],
                          onTap: () => _onGameSelected(_games[index]),
                          color: _getGameColor(_games[index]),
                          icon: _getGameIcon(_games[index]),
                        ).animate(controller: _reshuffleController).scale(
                          begin: const Offset(1.0, 1.0),
                          end: const Offset(0.0, 0.0),
                          curve: Curves.easeInOut,
                        ).then().scale(
                          begin: const Offset(0.0, 0.0),
                          end: const Offset(1.0, 1.0),
                          curve: Curves.elasticOut,
                        ),
                      ),
                    ),
                  );
                },
              );
            }),
          ],
        ),
      ),
    );
  }

  /// Returns appropriate color for each game type
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

  /// Returns appropriate icon for each game type
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