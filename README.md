# ♟️ Chess Platform

A modern, interactive chess application built with **Streamlit** and **python-chess**. Play against a ~1000 ELO bot, challenge friends in multiplayer mode, or manage the platform as an admin.

## ✨ Features

- **Interactive Canvas Board** – Single unified HTML5 Canvas interface with smooth piece selection and legal move highlighting
- **Bot Opponent** – Minimax-based chess engine with alpha-beta pruning (~1000 ELO rating) and realistic blunder rates
- **Multiplayer Mode** – Play against other users in real-time
- **User Authentication** – Secure login and registration with password hashing
- **Admin Dashboard** – Manage users, view game statistics, and configure platform settings
- **Game History** – Track all games with full move notation and game outcomes
- **ELO Rating System** – Competitive ranking system for players
- **Promotion Handling** – Pawn promotion dialog with piece selection
- **Check & Checkmate Detection** – Full legal move validation and game state management
- **Modern Dark Theme** – Custom-styled UI with professional typography and color scheme

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io) – Python web framework for rapid UI development
- **Chess Logic**: [python-chess](https://python-chess.readthedocs.io/) – Legal move validation and board manipulation
- **Styling**: Custom CSS with imported Google Fonts (Syne & JetBrains Mono)
- **Backend**: Pure Python with JSON-based persistence

## 📋 Requirements

- Python 3.8+
- Streamlit 1.35.0
- python-chess 1.999

## 🚀 Installation

1. **Clone or download the project**:
   ```bash
   cd streamlit_chess_app
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows**: `venv\Scripts\activate`
   - **macOS/Linux**: `source venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Running the Application

Start the app with:
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## 🎮 Game Modes

### 1. **Play vs Bot**
- Challenge the built-in chess engine
- Adjustable difficulty (depth-based minimax search)
- Engine makes realistic mistakes with configurable blunder rate
- Full game history and statistics

### 2. **Multiplayer**
- Invite other users to play
- Real-time board synchronization
- Track wins, losses, and draws
- View opponent profiles and statistics

### 3. **Admin Panel**
- **Default Credentials**: Username: `admin`, Password: `admin123`
- View all registered users and their statistics
- Monitor active games
- Access game history and analytics

## 📁 Project Structure

```
streamlit_chess_app/
├── app.py              # Main application with UI and game logic
├── requirements.txt    # Project dependencies
├── README.md          # This file
└── data/              # Auto-created directory
    ├── users.json     # User accounts and statistics
    └── games.json     # Game history and records
```

## 🔑 Key Components

### Chess Engine
- **Evaluation Function**: Piece-square tables (PST) for positional analysis
- **Move Ordering**: Captures and checks prioritized for alpha-beta pruning efficiency
- **Search**: Minimax with alpha-beta pruning (configurable depth)
- **Blunder Mechanism**: Realistic move mistakes based on probability

### UI Components
- **Single Canvas Board**: All board rendering in HTML5 Canvas (no grid duplication)
- **Interactive Selection**: Click-to-move piece interaction via JavaScript postMessage
- **Responsive Layout**: Wide layout with sidebar for game info and player stats
- **Custom Styling**: Dark theme with gold accents and professional fonts

## 🎯 How to Play

1. **Log in** with your username (create account or use default demo account)
2. **Choose a game mode**: Bot, Multiplayer, or (if admin) Admin Dashboard
3. **Click on a piece** to select it and see legal moves (highlighted)
4. **Click a destination square** to move the piece
5. **Promote pawns** when reaching the final rank by selecting from the promotion dialog
6. **View game status** in the sidebar (current turn, check warnings, move history)

### Examples of moves

Below are some common move examples in Standard Algebraic Notation (SAN) with equivalent UCI where helpful.

- **Simple pawn move**: `e4`  — UCI: `e2e4`
- **Piece development**: `Nf3`  — UCI: `g1f3`
- **Capture**: `exd5` (pawn from e4 captures on d5) — UCI: `e4d5`
- **Kingside castling**: `O-O` — UCI: `e1g1` (king) and `h1f1` (rook)
- **Queenside castling**: `O-O-O` — UCI: `e1c1` (king) and `a1d1` (rook)
- **En passant**: `exd6` e.p. (if applicable) — UCI: e.g. `e5d6`
- **Promotion**: `e8=Q` (pawn promotes to queen) — UCI: `e7e8q`

A short sample opening sequence (SAN):

1. e4 e5
2. Nf3 Nc6
3. Bb5 a6

This corresponds to the Ruy Lopez opening; moves in UCI would be: `e2e4 e7e5 g1f3 b8c6 f1b5 a7a6`.

## ⚙️ Configuration

### Bot Difficulty
- Modify `depth` parameter in `get_bot_move()` to adjust search depth (higher = stronger)
- Adjust `blunder_rate` to change how often the bot makes intentional mistakes (0.0-1.0)

### Default Admin Account
- Username: `admin`
- Password: `admin123` *(change after first login)*

## 📊 Game Statistics

The platform tracks:
- Total games played per user
- Wins, losses, and draws
- Win rate percentage
- ELO rating progression
- Game timestamps and move history

## 🔒 Security

- Passwords hashed with SHA-256
- Session management via Streamlit
- User authentication on all protected routes
- Admin role-based access control

## 🐛 Troubleshooting

**Board not rendering?**
- Clear browser cache or use incognito mode
- Ensure JavaScript is enabled in your browser

**Moves not registering?**
- Refresh the page
- Restart the Streamlit server: `Ctrl+C` then `streamlit run app.py`

**Login issues?**
- Default admin account: `admin` / `admin123`
- Check `data/users.json` for user records

## 📝 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

Feel free to fork, modify, and enhance this chess platform. Suggested improvements:
- Stronger chess engine (integrate Stockfish via subprocess)
- Opening book database
- Time controls and blitz modes
- Real-time multiplayer with WebSockets
- Database backend (SQLite/PostgreSQL)
- Tournament management system

---
jayanti
**Enjoy your chess! ♟️**
