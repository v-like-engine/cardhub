import 'package:flutter/material.dart';

/// Rules screen displaying comprehensive game instructions.
///
/// Shows detailed rules for each game with interactive card examples
/// and step-by-step gameplay instructions.
class RulesScreen extends StatelessWidget {
  final String gameType;

  const RulesScreen({Key? key, required this.gameType}) : super(key: key);

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
              // Header
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
                    Text(
                      '${_getGameDisplayName(gameType)} Rules',
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),

              // Rules content
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    children: [
                      _buildGameRules(gameType),
                      const SizedBox(height: 50),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Builds the rules content based on game type
  Widget _buildGameRules(String gameType) {
    switch (gameType) {
      case 'fool':
        return _buildFoolRules();
      case '101':
        return _build101Rules();
      case 'blackjack':
        return _buildBlackjackRules();
      case 'uno':
        return _buildUnoRules();
      default:
        return _buildDefaultRules();
    }
  }

  /// Builds Fool game rules
  Widget _buildFoolRules() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildRuleSection(
          'Overview',
          'Fool is a classic Russian card game where the goal is to get rid of all your cards. The last player with cards becomes the "Fool".',
          Icons.info_outline,
        ),
        _buildRuleSection(
          'Setup',
          '''• Uses a standard 52-card deck
• Each player starts with 6 cards
• One card is placed face-up to determine the trump suit
• Remaining cards form the draw pile''',
          Icons.settings,
        ),
        _buildRuleSection(
          'Gameplay',
          '''• Players take turns attacking and defending
• Attacker plays a card, defender must beat it
• To beat a card: play higher card of same suit OR any trump card
• Defender can pick up all cards if unable to defend
• Successful defender becomes next attacker''',
          Icons.play_arrow,
        ),
        _buildRuleSection(
          'Winning',
          '''• First player to empty their hand wins
• Last player with cards is the "Fool"
• Trump cards beat all non-trump cards
• Ace is highest, 6 is lowest''',
          Icons.emoji_events,
        ),
      ],
    );
  }

  /// Builds 101 game rules
  Widget _build101Rules() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildRuleSection(
          'Overview',
          'A fast-paced card game where players aim to reach exactly 101 points without going over.',
          Icons.info_outline,
        ),
        _buildRuleSection(
          'Setup',
          '''• Uses a standard 52-card deck
• Each player starts with 4 cards
• One card is placed face-up as the starter
• Number cards = face value, Face cards = 10, Ace = 11 or 1''',
          Icons.settings,
        ),
        _buildRuleSection(
          'Gameplay',
          '''• Players take turns playing cards to reach 101 points
• Must play a card matching suit or rank of top card
• Special cards have unique effects:
  - 8: Skip next player
  - Jack: Change suit
  - King: Reverse direction''',
          Icons.play_arrow,
        ),
        _buildRuleSection(
          'Winning',
          '''• First player to reach exactly 101 points wins
• Going over 101 points results in elimination
• If no legal play, draw from deck
• Last player standing wins if no one reaches 101''',
          Icons.emoji_events,
        ),
      ],
    );
  }

  /// Builds BlackJack game rules
  Widget _buildBlackjackRules() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildRuleSection(
          'Overview',
          'Beat the dealer by getting a hand value as close to 21 as possible without going over.',
          Icons.info_outline,
        ),
        _buildRuleSection(
          'Card Values',
          '''• Number cards (2-10): Face value
• Face cards (J, Q, K): 10 points each
• Ace: 1 or 11 (whichever is better)
• Blackjack: Ace + 10-value card = 21''',
          Icons.style,
        ),
        _buildRuleSection(
          'Gameplay',
          '''• You and dealer each get 2 cards initially
• Your cards are face-up, dealer has one face-down
• Choose to Hit (take card) or Stand (keep current total)
• Dealer must hit on 16 and stand on 17
• Bust if total exceeds 21''',
          Icons.play_arrow,
        ),
        _buildRuleSection(
          'Winning',
          '''• Beat dealer without busting
• Blackjack (21 with 2 cards) beats regular 21
• If you bust, you lose immediately
• If dealer busts and you don't, you win
• Tie ("Push") if same total''',
          Icons.emoji_events,
        ),
      ],
    );
  }

  /// Builds Uno game rules
  Widget _buildUnoRules() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildRuleSection(
          'Overview',
          'Be the first player to empty your hand by matching colors, numbers, or using special action cards.',
          Icons.info_outline,
        ),
        _buildRuleSection(
          'Setup',
          '''• Uses special Uno deck (108 cards)
• Each player starts with 7 cards
• One card is placed face-up to start
• 4 colors: Red, Blue, Green, Yellow
• Numbers 0-9, plus action cards''',
          Icons.settings,
        ),
        _buildRuleSection(
          'Action Cards',
          '''• Skip: Next player loses their turn
• Reverse: Change direction of play
• Draw Two: Next player draws 2 cards
• Wild: Change color to any choice
• Wild Draw Four: Change color + next player draws 4''',
          Icons.auto_awesome,
        ),
        _buildRuleSection(
          'Gameplay',
          '''• Match color or number of top card
• Play action cards for special effects
• Say "Uno" when you have one card left
• Draw from deck if no legal play
• First to empty hand wins the round''',
          Icons.play_arrow,
        ),
        _buildRuleSection(
          'Winning',
          '''• First player to get rid of all cards wins
• Penalty for forgetting to say "Uno": draw 2 cards
• Points scored based on cards remaining in opponents' hands
• First to 500 points wins the game''',
          Icons.emoji_events,
        ),
      ],
    );
  }

  /// Builds default rules for unknown games
  Widget _buildDefaultRules() {
    return _buildRuleSection(
      'Game Rules',
      'Rules for this game are not yet available. Please check back later for detailed instructions.',
      Icons.help_outline,
    );
  }

  /// Builds a rule section with title, content, and icon
  Widget _buildRuleSection(String title, String content, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 25),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(
          color: Colors.white.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: ExpansionTile(
        title: Row(
          children: [
            Icon(
              icon,
              color: _getGameColor(gameType),
              size: 24,
            ),
            const SizedBox(width: 15),
            Expanded(
              child: Text(
                title,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ),
        iconColor: Colors.white,
        collapsedIconColor: Colors.white70,
        backgroundColor: Colors.transparent,
        children: [
          Padding(
            padding: const EdgeInsets.all(20),
            child: Text(
              content,
              style: const TextStyle(
                fontSize: 16,
                color: Colors.white70,
                height: 1.5,
              ),
            ),
          ),
        ],
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
}