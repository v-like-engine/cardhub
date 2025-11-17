# cardhub - Premium Card Game Platform

cardhub is a comprehensive card game platform that allows users to play classic card games (Fool, 101, BlackJack, and Uno) with AI opponents and online multiplayer. Built with Flutter for the frontend and Python for the backend, it provides a Steam-like experience for tabletop card games.

## Features

### 🎮 Game Collection
- **Fool (Durak)**: Classic Russian card game with strategic trump play
- **101**: Fast-paced point accumulation game with special card effects
- **BlackJack**: Traditional casino card game with optimal AI strategy
- **Uno**: Colorful strategy game with action cards and color management

### 🤖 Intelligent AI
- Multiple difficulty levels (Easy, Medium, Hard)
- Game-specific strategies and decision-making
- Realistic timing and behavior patterns
- Strategic card counting and risk assessment

### 🎨 Immersive UI
- Card-based navigation with realistic animations
- 3D card appearance with shadows and depth
- Smooth transitions and reshuffling effects
- Responsive design for both mobile and desktop

### 📊 Comprehensive Statistics
- Individual game statistics and win rates
- Achievement system with unlockable rewards
- Experience points and player leveling
- Leaderboards and competitive rankings

### 🎯 User Experience
- Guest and registered user accounts
- Persistent game statistics and progress
- Customizable themes and preferences
- Detailed game rules and tutorials

## Technology Stack

### Frontend (Flutter)
- **Framework**: Flutter 3.x
- **State Management**: Provider pattern
- **Animations**: Flutter Animate package
- **Local Storage**: SharedPreferences
- **UI Components**: Material Design with custom cards

### Backend (Python)
- **Framework**: Flask with RESTful API
- **Database**: SQLAlchemy ORM with SQLite
- **Game Engine**: Object-oriented design with inheritance
- **AI System**: Strategic algorithms with difficulty scaling
- **Architecture**: Modular design with clear separation of concerns

## Project Structure

```
cardhub/
├── frontend/                 # Flutter application
│   ├── lib/
│   │   ├── main.dart        # Application entry point
│   │   ├── screens/         # UI screens
│   │   ├── widgets/         # Reusable UI components
│   │   └── providers/       # State management
│   ├── assets/              # Images, fonts, sounds
│   └── pubspec.yaml         # Flutter dependencies
│
├── backend/                 # Python backend
│   ├── game_engine/         # Core game logic
│   │   ├── base_game.py     # Abstract base game class
│   │   ├── blackjack.py     # BlackJack implementation
│   │   ├── fool.py          # Fool game implementation
│   │   ├── one_hundred_one.py # 101 game implementation
│   │   └── uno.py           # Uno implementation
│   ├── ai/                  # AI algorithms
│   │   ├── base_ai.py       # Abstract AI base class
│   │   ├── blackjack_ai.py  # BlackJack AI strategy
│   │   ├── fool_ai.py       # Fool AI strategy
│   │   ├── one_hundred_one_ai.py # 101 AI strategy
│   │   └── uno_ai.py        # Uno AI strategy
│   ├── models/              # Data models
│   │   ├── card.py          # Standard playing card
│   │   ├── deck.py          # Card deck management
│   │   ├── uno_card.py      # Uno-specific cards
│   │   └── uno_deck.py      # Uno deck management
│   ├── database/            # Database layer
│   │   ├── models.py        # SQLAlchemy models
│   │   └── database.py      # Database management
│   └── api/                 # REST API
│       ├── app.py           # Flask application
│       └── routes/          # API route handlers
│
└── README.md               # This file
```

## Installation and Setup

### Prerequisites
- Python 3.8+ with pip
- Flutter SDK 3.0+
- Git

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install flask flask-cors sqlalchemy python-dateutil
   ```

4. **Initialize database**:
   ```bash
   python -c "from database.database import get_database_manager; get_database_manager().initialize_database()"
   ```

5. **Start the API server**:
   ```bash
   python api/app.py
   ```

The backend API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Flutter dependencies**:
   ```bash
   flutter pub get
   ```

3. **Run the application**:
   ```bash
   flutter run
   ```

For web development:
```bash
flutter run -d chrome
```

## API Endpoints

### Authentication
- `POST /api/auth/guest` - Create guest user
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/validate/{user_id}` - Validate user

### Games
- `POST /api/games/create` - Create new game
- `POST /api/games/{game_id}/start` - Start game
- `POST /api/games/{game_id}/move` - Make game move
- `GET /api/games/{game_id}/state` - Get game state
- `GET /api/games/{game_id}/rules` - Get game rules
- `POST /api/games/{game_id}/abandon` - Abandon game

### Users
- `GET /api/users/{user_id}` - Get user profile
- `GET /api/users/{user_id}/achievements` - Get user achievements

### Statistics
- `GET /api/statistics/user/{user_id}` - Get user statistics
- `GET /api/statistics/leaderboard` - Get leaderboards

## Game Rules

### Fool (Durak)
Classic Russian card game where players attack and defend with cards. Trump cards beat non-trump cards, and higher cards of the same suit beat lower cards. The goal is to empty your hand first.

### 101
Players accumulate points toward exactly 101. Special cards have effects:
- **8**: Skip next player
- **Jack**: Wild card (change suit)
- **King**: Reverse direction

### BlackJack
Get as close to 21 as possible without going over. Face cards = 10, Aces = 1 or 11. Beat the dealer's hand to win.

### Uno
Match colors or numbers, use action cards strategically:
- **Skip**: Next player loses turn
- **Reverse**: Change direction
- **Draw Two**: Next player draws 2 cards
- **Wild**: Change color
- **Wild Draw Four**: Change color + next player draws 4

## AI Difficulty Levels

### Easy
- 30% randomness in decisions
- Makes obvious beginner mistakes
- Conservative play style
- Longer decision times

### Medium
- 15% randomness in decisions
- Occasional strategic errors
- Balanced aggressive/defensive play
- Moderate decision times

### Hard
- 5% randomness in decisions
- Near-optimal strategic play
- Advanced techniques (card counting in BlackJack)
- Quick decision times

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use type hints for function parameters and returns
- Include comprehensive docstrings for all classes and methods
- No inline comments (use descriptive variable names and docstrings)
- Use OOP best practices with proper inheritance

### Flutter Code
- Follow Flutter/Dart style guidelines
- Use meaningful widget and variable names
- Include documentation comments for public APIs
- Implement proper state management with Provider
- Use const constructors where possible

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flutter team for the excellent cross-platform framework
- Python community for the robust backend ecosystem
- Card game communities for rule specifications and strategies
- Open source contributors who made this project possible

## Future Enhancements

- **Online Multiplayer**: Real-time games with WebSocket connections
- **Tournament Mode**: Structured competitions with brackets
- **Custom Card Games**: SDK for third-party game developers
- **Social Features**: Friends, chat, and game sharing
- **Mobile Optimizations**: Gesture controls and haptic feedback
- **Analytics Dashboard**: Detailed game performance insights