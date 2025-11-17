import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../providers/user_provider.dart';
import '../widgets/menu_card.dart';
import 'gameplay_screen.dart';
import 'statistics_screen.dart';
import 'rules_screen.dart';

/// Game-specific menu screen with options for each game.
///
/// Provides access to single-player AI games, statistics,
/// rules, and achievements for the selected game type.
class GameMenuScreen extends StatefulWidget {
  final String gameType;

  const GameMenuScreen({Key? key, required this.gameType}) : super(key: key);

  @override
  _GameMenuScreenState createState() => _GameMenuScreenState();
}

class _GameMenuScreenState extends State<GameMenuScreen>
    with TickerProviderStateMixin {
  late AnimationController _reshuffleController;
  late AnimationController _dealController;

  @override
  void initState() {
    super.initState();
    _reshuffleController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _dealController = AnimationController(
      duration: const Duration(milliseconds: 1500),
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

  /// Handles menu option selection
  void _onOptionSelected(String option) async {
    await _reshuffleController.forward();

    switch (option) {
      case 'play_ai':
        Navigator.push(
          context,
          PageRouteBuilder(
            pageBuilder: (context, animation, secondaryAnimation) =>
                GameplayScreen(gameType: widget.gameType, isAI: true),
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
        );
        break;
      case 'statistics':
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => StatisticsScreen(gameType: widget.gameType),
          ),
        );
        break;
      case 'rules':
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => RulesScreen(gameType: widget.gameType),
          ),
        );
        break;
      case 'back':
        Navigator.pop(context);
        break;
    }

    _reshuffleController.reset();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final gameDisplayName = _getGameDisplayName(widget.gameType);

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
                  // Game title and icon
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: Colors.white.withOpacity(0.2),
                        width: 1,
                      ),
                    ),
                    child: Column(
                      children: [
                        Icon(
                          _getGameIcon(widget.gameType),
                          size: 64,
                          color: _getGameColor(widget.gameType),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          gameDisplayName,
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
                        ),
                        const SizedBox(height: 5),
                        Text(
                          _getGameDescription(widget.gameType),
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.white70,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ).animate().fadeIn(duration: 800.ms).slideY(begin: -0.3),

                  const SizedBox(height: 60),

                  // Menu options
                  _buildMenuOptions(screenSize),

                  const SizedBox(height: 40),

                  // Quick stats
                  Consumer<UserProvider>(
                    builder: (context, userProvider, child) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 15,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(15),
                          border: Border.all(
                            color: Colors.white.withOpacity(0.2),
                            width: 1,
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            _buildQuickStat(
                              'Games Played',
                              '${userProvider.gameSpecificPlayed[widget.gameType] ?? 0}',
                              Icons.games,
                            ),
                            const SizedBox(width: 30),
                            _buildQuickStat(
                              'Win Rate',
                              '${userProvider.getGameWinRate(widget.gameType).toStringAsFixed(1)}%',
                              Icons.emoji_events,
                            ),
                          ],
                        ),
                      ).animate().fadeIn(delay: 1000.ms, duration: 600.ms);
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Builds the menu option cards with dealing animation
  Widget _buildMenuOptions(Size screenSize) {
    final options = [
      {'id': 'back', 'title': 'Back', 'icon': Icons.arrow_back, 'color': Colors.grey},
      {'id': 'play_ai', 'title': 'Play vs AI', 'icon': Icons.smart_toy, 'color': const Color(0xFF4CAF50)},
      {'id': 'statistics', 'title': 'Statistics', 'icon': Icons.bar_chart, 'color': const Color(0xFF2196F3)},
      {'id': 'rules', 'title': 'Rules', 'icon': Icons.help_outline, 'color': const Color(0xFFF57C00)},
    ];

    return SizedBox(
      height: 220,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: EdgeInsets.symmetric(horizontal: 20),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(options.length, (index) {
            final option = options[index];
            return AnimatedBuilder(
              animation: _dealController,
              builder: (context, child) {
                double progress = _dealController.value;
                double cardProgress = ((progress * 4) - index).clamp(0.0, 1.0);

                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 10),
                  child: Transform.translate(
                    offset: Offset(0, 50 * (1 - cardProgress)),
                    child: Opacity(
                      opacity: cardProgress,
                      child: MenuCard(
                        title: option['title'] as String,
                        icon: option['icon'] as IconData,
                        color: option['color'] as Color,
                        onTap: () => _onOptionSelected(option['id'] as String),
                        onHover: (isHovering) {},
                        zIndex: index,
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
        ),
      ),
    );
  }

  /// Builds a quick stat display
  Widget _buildQuickStat(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
        const SizedBox(height: 5),
        Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.white70,
          ),
        ),
      ],
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

  String _getGameDescription(String gameType) {
    switch (gameType) {
      case 'fool':
        return 'Classic Russian card game\nOutsmart your opponents';
      case '101':
        return 'Fast-paced number game\nReach exactly 101 points';
      case 'blackjack':
        return 'Beat the dealer\nGet as close to 21 as possible';
      case 'uno':
        return 'Colorful strategy game\nBe the first to empty your hand';
      default:
        return 'Card game';
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