import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/user_provider.dart';

/// Statistics screen showing detailed game performance data.
///
/// Displays comprehensive statistics for a specific game type
/// including win/loss records, achievements, and progress tracking.
class StatisticsScreen extends StatelessWidget {
  final String gameType;

  const StatisticsScreen({Key? key, required this.gameType}) : super(key: key);

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
                      '${_getGameDisplayName(gameType)} Statistics',
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),

              // Statistics content
              Expanded(
                child: Consumer<UserProvider>(
                  builder: (context, userProvider, child) {
                    return ListView(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      children: [
                        // Game Statistics
                        _buildStatisticsSection(
                          'Game Performance',
                          [
                            _buildStatCard(
                              'Games Played',
                              '${userProvider.gameSpecificPlayed[gameType] ?? 0}',
                              Icons.games,
                              const Color(0xFF2196F3),
                            ),
                            _buildStatCard(
                              'Games Won',
                              '${userProvider.gameSpecificWins[gameType] ?? 0}',
                              Icons.emoji_events,
                              const Color(0xFF4CAF50),
                            ),
                            _buildStatCard(
                              'Win Rate',
                              '${userProvider.getGameWinRate(gameType).toStringAsFixed(1)}%',
                              Icons.trending_up,
                              const Color(0xFFF57C00),
                            ),
                            _buildStatCard(
                              'Experience',
                              '${userProvider.totalExperience}',
                              Icons.star,
                              const Color(0xFF9C27B0),
                            ),
                          ],
                        ),

                        const SizedBox(height: 30),

                        // Progress Section
                        _buildProgressSection(userProvider),

                        const SizedBox(height: 30),

                        // Achievements Section
                        _buildAchievementsSection(userProvider),

                        const SizedBox(height: 50),
                      ],
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Builds a statistics section with cards
  Widget _buildStatisticsSection(String title, List<Widget> statCards) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 20),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 15,
          mainAxisSpacing: 15,
          childAspectRatio: 1.2,
          children: statCards,
        ),
      ],
    );
  }

  /// Builds an individual statistic card
  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            icon,
            size: 32,
            color: color,
          ),
          const SizedBox(height: 10),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 5),
          Text(
            title,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.white70,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  /// Builds the progress section
  Widget _buildProgressSection(UserProvider userProvider) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(
          color: Colors.white.withOpacity(0.2),
          width: 1,
        ),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Player Progress',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Icon(
                Icons.star,
                color: const Color(0xFFFFD700),
                size: 24,
              ),
              const SizedBox(width: 10),
              Text(
                'Level ${userProvider.currentLevel}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: (userProvider.totalExperience % 1000) / 1000,
              backgroundColor: Colors.white.withOpacity(0.2),
              valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFFFD700)),
              minHeight: 8,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'Next Level: ${userProvider.experienceForNextLevel} XP needed',
            style: const TextStyle(
              fontSize: 14,
              color: Colors.white70,
            ),
          ),
        ],
      ),
    );
  }

  /// Builds the achievements section
  Widget _buildAchievementsSection(UserProvider userProvider) {
    final gameAchievements = userProvider.achievements
        .where((achievement) => achievement.toLowerCase().contains(gameType.toLowerCase()))
        .toList();

    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(
          color: Colors.white.withOpacity(0.2),
          width: 1,
        ),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${_getGameDisplayName(gameType)} Achievements',
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 20),
          if (gameAchievements.isEmpty)
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.05),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: Colors.white.withOpacity(0.1),
                  width: 1,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.emoji_events_outlined,
                    color: Colors.white54,
                    size: 24,
                  ),
                  const SizedBox(width: 15),
                  const Expanded(
                    child: Text(
                      'No achievements yet. Start playing to unlock them!',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.white54,
                      ),
                    ),
                  ),
                ],
              ),
            )
          else
            ...gameAchievements.map((achievement) => _buildAchievementTile(achievement)),
        ],
      ),
    );
  }

  /// Builds an individual achievement tile
  Widget _buildAchievementTile(String achievement) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: const Color(0xFFFFD700).withOpacity(0.1),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: const Color(0xFFFFD700).withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.emoji_events,
            color: const Color(0xFFFFD700),
            size: 24,
          ),
          const SizedBox(width: 15),
          Expanded(
            child: Text(
              achievement,
              style: const TextStyle(
                fontSize: 16,
                color: Colors.white,
                fontWeight: FontWeight.w500,
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
}