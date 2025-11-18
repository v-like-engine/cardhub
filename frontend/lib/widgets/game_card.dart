import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// A realistic game card widget representing individual games.
///
/// Features detailed 3D appearance with shadows, hover effects,
/// and animations. Designed to look like premium game cards.
class GameCard extends StatefulWidget {
  final String title;
  final String description;
  final VoidCallback onTap;
  final Color color;
  final IconData icon;

  const GameCard({
    Key? key,
    required this.title,
    required this.description,
    required this.onTap,
    required this.color,
    required this.icon,
  }) : super(key: key);

  @override
  _GameCardState createState() => _GameCardState();
}

class _GameCardState extends State<GameCard>
    with SingleTickerProviderStateMixin {
  bool _isHovered = false;
  late AnimationController _animationController;
  late Animation<double> _elevationAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _elevationAnimation = Tween<double>(
      begin: 12.0,
      end: 20.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.08,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _rotationAnimation = Tween<double>(
      begin: 0.0,
      end: 0.02,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _handleHover(bool isHovering) {
    setState(() {
      _isHovered = isHovering;
    });

    if (isHovering) {
      _animationController.forward();
    } else {
      _animationController.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => _handleHover(true),
      onExit: (_) => _handleHover(false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedBuilder(
          animation: _animationController,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Transform.rotate(
                angle: _rotationAnimation.value,
                child: Container(
                  width: 180,
                  height: 250,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(15),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.4),
                        blurRadius: _elevationAnimation.value,
                        offset: Offset(0, _elevationAnimation.value / 2),
                      ),
                      BoxShadow(
                        color: Colors.black.withOpacity(0.2),
                        blurRadius: _elevationAnimation.value * 1.5,
                        offset: Offset(0, _elevationAnimation.value),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(15),
                    child: Stack(
                      children: [
                        // Card background with gradient
                        Container(
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: [
                                Colors.white,
                                const Color(0xFFF8F8F8),
                                const Color(0xFFEEEEEE),
                              ],
                            ),
                          ),
                        ),

                        // Color accent strip
                        Positioned(
                          top: 0,
                          left: 0,
                          right: 0,
                          child: Container(
                            height: 60,
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                                colors: [
                                  widget.color,
                                  widget.color.withOpacity(0.8),
                                ],
                              ),
                            ),
                          ),
                        ),

                        // Card border
                        Container(
                          decoration: BoxDecoration(
                            border: Border.all(
                              color: Colors.grey.withOpacity(0.3),
                              width: 1.5,
                            ),
                            borderRadius: BorderRadius.circular(15),
                          ),
                        ),

                        // Content
                        Padding(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Icon in colored area
                              Icon(
                                widget.icon,
                                size: 32,
                                color: Colors.white,
                              ),

                              const SizedBox(height: 20),

                              // Title
                              Text(
                                widget.title,
                                style: TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: widget.color,
                                  shadows: [
                                    Shadow(
                                      offset: const Offset(1, 1),
                                      blurRadius: 2,
                                      color: Colors.grey.withOpacity(0.3),
                                    ),
                                  ],
                                ),
                              ),

                              const SizedBox(height: 12),

                              // Description
                              Text(
                                widget.description,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[600],
                                  height: 1.4,
                                ),
                              ),

                              const Spacer(),

                              // Bottom decorative elements
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Container(
                                    width: 30,
                                    height: 3,
                                    decoration: BoxDecoration(
                                      color: widget.color.withOpacity(0.3),
                                      borderRadius: BorderRadius.circular(2),
                                    ),
                                  ),
                                  Icon(
                                    Icons.play_arrow,
                                    color: widget.color.withOpacity(0.6),
                                    size: 20,
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),

                        // Hover glow effect
                        if (_isHovered)
                          Container(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(15),
                              gradient: LinearGradient(
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                                colors: [
                                  widget.color.withOpacity(0.15),
                                  Colors.transparent,
                                ],
                              ),
                            ),
                          ).animate().fadeIn(duration: 200.ms),

                        // Card corner suit symbols (playing card style)
                        Positioned(
                          top: 10,
                          left: 10,
                          child: Column(
                            children: [
                              Text(
                                _getSuitSymbol(widget.title),
                                style: TextStyle(
                                  fontSize: 16,
                                  color: widget.color.withOpacity(0.7),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Icon(
                                widget.icon,
                                size: 14,
                                color: widget.color.withOpacity(0.7),
                              ),
                            ],
                          ),
                        ),
                        Positioned(
                          bottom: 10,
                          right: 10,
                          child: Transform.rotate(
                            angle: 3.14159, // 180 degrees
                            child: Column(
                              children: [
                                Text(
                                  _getSuitSymbol(widget.title),
                                  style: TextStyle(
                                    fontSize: 16,
                                    color: widget.color.withOpacity(0.7),
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                Icon(
                                  widget.icon,
                                  size: 14,
                                  color: widget.color.withOpacity(0.7),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  /// Returns appropriate suit symbol for the card
  String _getSuitSymbol(String title) {
    switch (title.toLowerCase()) {
      case 'fool':
        return '♠';
      case '101':
        return '♦';
      case 'blackjack':
        return '♣';
      case 'uno':
        return '♥';
      case 'back to menu':
        return '←';
      default:
        return '♠';
    }
  }
}