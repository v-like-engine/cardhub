import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';
import '../widgets/menu_card.dart';
import 'game_selection_screen.dart';
import 'settings_screen.dart';

/// Main menu screen featuring card-based navigation.
///
/// Displays three cards (Play, Settings, Exit) that reorder on hover
/// and provide smooth transitions to different parts of the application.
class MainMenuScreen extends StatefulWidget {
  @override
  _MainMenuScreenState createState() => _MainMenuScreenState();
}

class _MainMenuScreenState extends State<MainMenuScreen>
    with TickerProviderStateMixin {
  int _hoveredIndex = -1;
  late AnimationController _reshuffleController;

  @override
  void initState() {
    super.initState();
    _reshuffleController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    // Load settings when screen initializes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<SettingsProvider>().loadSettings();
    });
  }

  @override
  void dispose() {
    _reshuffleController.dispose();
    super.dispose();
  }

  /// Handles card tap events and navigates to appropriate screens
  void _onCardTapped(int index) async {
    await _reshuffleController.forward();

    switch (index) {
      case 0: // Play
        Navigator.push(
          context,
          PageRouteBuilder(
            pageBuilder: (context, animation, secondaryAnimation) =>
                GameSelectionScreen(),
            transitionsBuilder: (context, animation, secondaryAnimation, child) {
              return FadeTransition(opacity: animation, child: child);
            },
            transitionDuration: const Duration(milliseconds: 500),
          ),
        );
        break;
      case 1: // Settings
        Navigator.push(
          context,
          PageRouteBuilder(
            pageBuilder: (context, animation, secondaryAnimation) =>
                SettingsScreen(),
            transitionsBuilder: (context, animation, secondaryAnimation, child) {
              return SlideTransition(
                position: Tween<Offset>(
                  begin: const Offset(1.0, 0.0),
                  end: Offset.zero,
                ).animate(animation),
                child: child,
              );
            },
            transitionDuration: const Duration(milliseconds: 500),
          ),
        );
        break;
      case 2: // Exit
        _showExitDialog();
        break;
    }

    _reshuffleController.reset();
  }

  /// Shows confirmation dialog before exiting the application
  void _showExitDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF2D1B0F),
          title: const Text(
            'Exit Game',
            style: TextStyle(color: Colors.white),
          ),
          content: const Text(
            'Are you sure you want to exit SoundWound?',
            style: TextStyle(color: Colors.white70),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                // Save any unsaved data here
                Navigator.of(context).pop();
                // Exit the application
                // SystemNavigator.pop(); // Uncomment for actual exit
              },
              child: const Text('Exit'),
            ),
          ],
        );
      },
    );
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

            // Main content
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Title
                  Text(
                    'SoundWound',
                    style: TextStyle(
                      fontSize: 64,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      shadows: [
                        Shadow(
                          offset: const Offset(4, 4),
                          blurRadius: 8,
                          color: Colors.black.withOpacity(0.7),
                        ),
                      ],
                    ),
                  ).animate().fadeIn(duration: 1000.ms).slideY(begin: -0.3),

                  const SizedBox(height: 20),

                  Text(
                    'Premium Card Game Platform',
                    style: TextStyle(
                      fontSize: 24,
                      color: Colors.white70,
                      shadows: [
                        Shadow(
                          offset: const Offset(2, 2),
                          blurRadius: 4,
                          color: Colors.black.withOpacity(0.5),
                        ),
                      ],
                    ),
                  ).animate().fadeIn(delay: 500.ms, duration: 800.ms),

                  const SizedBox(height: 80),

                  // Menu cards
                  _buildMenuCards(screenSize),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Builds the three menu cards with hover effects and animations
  Widget _buildMenuCards(Size screenSize) {
    final cardTitles = ['Play', 'Settings', 'Exit'];
    final cardIcons = [Icons.play_arrow, Icons.settings, Icons.exit_to_app];
    final cardColors = [
      const Color(0xFF4CAF50),
      const Color(0xFF2196F3),
      const Color(0xFFF44336),
    ];

    return SizedBox(
      height: 200,
      child: Stack(
        alignment: Alignment.center,
        children: List.generate(3, (index) {
          // Calculate positions based on hover state
          double leftOffset = 0;
          double topOffset = 0;
          double scale = 1.0;
          int zIndex = index;

          if (_hoveredIndex == -1) {
            // Default fan layout
            leftOffset = (index - 1) * 80.0;
            topOffset = (index - 1).abs() * 20.0;
          } else if (_hoveredIndex == index) {
            // Hovered card comes to front
            zIndex = 10;
            scale = 1.1;
          } else {
            // Other cards move back
            leftOffset = _hoveredIndex == 0
                ? (index == 1 ? 100 : 150)
                : _hoveredIndex == 2
                    ? (index == 1 ? -100 : -150)
                    : (index < _hoveredIndex ? -120 : 120);
            topOffset = 40;
            scale = 0.9;
          }

          return AnimatedPositioned(
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeInOut,
            left: screenSize.width / 2 - 75 + leftOffset,
            top: topOffset,
            child: Transform.scale(
              scale: scale,
              child: MenuCard(
                title: cardTitles[index],
                icon: cardIcons[index],
                color: cardColors[index],
                onTap: () => _onCardTapped(index),
                onHover: (isHovering) {
                  setState(() {
                    _hoveredIndex = isHovering ? index : -1;
                  });
                },
                zIndex: zIndex,
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
        }),
      ),
    );
  }
}