import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Manages application settings including volume, graphics, and user preferences.
///
/// This provider handles persistence of settings using SharedPreferences
/// and provides reactive updates to the UI when settings change.
class SettingsProvider with ChangeNotifier {
  double _masterVolume = 1.0;
  double _sfxVolume = 1.0;
  double _musicVolume = 1.0;
  bool _animationsEnabled = true;
  String _screenResolution = 'auto';
  bool _fullscreen = false;

  /// Master volume level (0.0 to 1.0)
  double get masterVolume => _masterVolume;

  /// Sound effects volume level (0.0 to 1.0)
  double get sfxVolume => _sfxVolume;

  /// Background music volume level (0.0 to 1.0)
  double get musicVolume => _musicVolume;

  /// Whether card animations are enabled
  bool get animationsEnabled => _animationsEnabled;

  /// Screen resolution setting
  String get screenResolution => _screenResolution;

  /// Fullscreen mode enabled
  bool get fullscreen => _fullscreen;

  /// Initializes settings from persistent storage
  Future<void> loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    _masterVolume = prefs.getDouble('masterVolume') ?? 1.0;
    _sfxVolume = prefs.getDouble('sfxVolume') ?? 1.0;
    _musicVolume = prefs.getDouble('musicVolume') ?? 1.0;
    _animationsEnabled = prefs.getBool('animationsEnabled') ?? true;
    _screenResolution = prefs.getString('screenResolution') ?? 'auto';
    _fullscreen = prefs.getBool('fullscreen') ?? false;
    notifyListeners();
  }

  /// Sets master volume and saves to storage
  Future<void> setMasterVolume(double volume) async {
    _masterVolume = volume;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setDouble('masterVolume', volume);
    notifyListeners();
  }

  /// Sets sound effects volume and saves to storage
  Future<void> setSfxVolume(double volume) async {
    _sfxVolume = volume;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setDouble('sfxVolume', volume);
    notifyListeners();
  }

  /// Sets music volume and saves to storage
  Future<void> setMusicVolume(double volume) async {
    _musicVolume = volume;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setDouble('musicVolume', volume);
    notifyListeners();
  }

  /// Toggles animation settings and saves to storage
  Future<void> toggleAnimations() async {
    _animationsEnabled = !_animationsEnabled;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('animationsEnabled', _animationsEnabled);
    notifyListeners();
  }

  /// Sets screen resolution and saves to storage
  Future<void> setScreenResolution(String resolution) async {
    _screenResolution = resolution;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('screenResolution', resolution);
    notifyListeners();
  }

  /// Toggles fullscreen mode and saves to storage
  Future<void> toggleFullscreen() async {
    _fullscreen = !_fullscreen;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('fullscreen', _fullscreen);
    notifyListeners();
  }
}