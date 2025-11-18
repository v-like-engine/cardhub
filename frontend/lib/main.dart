import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/main_menu_screen.dart';
import 'providers/game_state_provider.dart';
import 'providers/settings_provider.dart';
import 'providers/user_provider.dart';

/// Main entry point for the SoundWound card game application.
///
/// This app provides a platform for playing various card games including
/// Fool, 101, BlackJack, and Uno with AI opponents and online multiplayer.
void main() {
  runApp(SoundWoundApp());
}

/// Root widget for the SoundWound application.
///
/// Sets up the necessary providers for state management and defines
/// the overall theme and navigation structure.
class SoundWoundApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => GameStateProvider()),
        ChangeNotifierProvider(create: (_) => SettingsProvider()),
        ChangeNotifierProvider(create: (_) => UserProvider()),
      ],
      child: Consumer<SettingsProvider>(
        builder: (context, settings, child) {
          return MaterialApp(
            title: 'SoundWound Card Games',
            theme: ThemeData(
              primarySwatch: Colors.green,
              scaffoldBackgroundColor: const Color(0xFF0F4C3A),
              fontFamily: 'CardGame',
              elevatedButtonTheme: ElevatedButtonThemeData(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF8B4513),
                  foregroundColor: Colors.white,
                  elevation: 8,
                  shadowColor: Colors.black45,
                ),
              ),
            ),
            home: MainMenuScreen(),
            debugShowCheckedModeBanner: false,
          );
        },
      ),
    );
  }
}