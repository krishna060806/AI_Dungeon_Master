# ⚔️ AI Dungeon Master — The Forgotten Dungeon

An AI-powered fantasy text adventure where every action shapes your journey. Explore mysterious chambers, fight dangerous enemies, collect legendary weapons, level up your character, and defeat the final Dragon.

Built using Python, Streamlit and an AI-powered Dungeon Master connected through OpenRouter.

---

## 📌 Project Overview

AI Dungeon Master is an interactive RPG that combines traditional game mechanics with AI-generated storytelling.

Players explore a connected dungeon, interact with the environment, fight enemies, collect items and complete quests. An AI Dungeon Master generates narrative responses based on the player's actions, making each interaction more immersive.

The project includes both a terminal-based game and a Streamlit-based web interface.

## ✨ Features

### 🎮 Gameplay
- Seven interconnected dungeon rooms.
- Interactive room exploration and movement.
- Enemy encounters and turn-based combat.
- Dragon boss battle.
- Weapon collection and equipment.
- Healing potions and inventory management.

### ⭐ Player Progression
- XP and leveling system.
- Increasing maximum health and attack damage.
- Gold rewards for defeating enemies.
- Character statistics and progression tracking.

### 🤖 AI Dungeon Master
- AI-generated fantasy storytelling.
- Context-aware narrative responses.
- Player-driven interactions.
- OpenRouter API integration.

### 👤 Player Accounts
- Local account registration and login.
- Password hashing using PBKDF2-HMAC-SHA256.
- Separate save files for individual accounts.
- Save and load adventure progress.
- Switch between player accounts.

### 🖥️ Web Interface
- Fantasy-themed Streamlit interface.
- Character HUD and health/XP indicators.
- Adventure chronicles.
- Dungeon atlas and quest journal.
- Room artwork and enemy health indicators.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core game logic |
| Streamlit | Web interface |
| OpenRouter | AI model API access |
| OpenAI Python SDK | API communication |
| python-dotenv | Environment variable management |
| JSON | Local account and game-save storage |
| HTML/CSS | Interface styling |

## 🏰 Dungeon Locations

The Forgotten Dungeon contains seven connected locations:

1. Dungeon Entrance
2. Ancient Hall
3. Treasure Room
4. Forgotten Library
5. Haunted Crypt
6. Ancient Armory
7. Dragon's Chamber

Players must obtain the Ancient Artifact before entering the final chamber.

## ⚔️ Game Mechanics

- **Combat:** Fight enemies using equipped weapons.
- **Inventory:** Collect weapons, potions and quest items.
- **Progression:** Gain XP and unlock stronger character stats.
- **Exploration:** Navigate interconnected rooms.
- **Quest:** Obtain the Ancient Artifact and defeat the Dragon.
- **Persistence:** Save and restore individual adventures.

## 📂 Project Structure

```text
AI_Dungeon_Master/
│
├── main.py
├── game.py
├── ai_engine.py
├── story.py
├── player.py
├── player_data.py
│
├── boss.py
├── enemies.py
├── rooms.py
├── items.py
├── item_detector.py
│
├── save_manager.py
├── library_management.py
│
├── streamlit_app.py
│
├── requirements.txt
├── .gitignore
├── .env
│
├── accounts.json
├── save.json
├── streamlit_save.json
│
└── saves/
```

**Note:** Local account files, save files and `.env` are generated or used locally and should not be committed to GitHub.

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/krishna060806/AI_Dungeon_Master.git
```

### 2. Navigate to the project directory

```bash
cd AI_Dungeon_Master
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the API key

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Obtain an API key from [OpenRouter](https://openrouter.ai/).

Never publish your API key.

### 5. Run the web application

```bash
streamlit run streamlit_app.py
```

The application will open in your browser.

### 6. Run the terminal version

```bash
python main.py
```

## 🔐 Account and Save Management

The Streamlit version supports multiple local player accounts.

- Account credentials are stored locally.
- Passwords are hashed rather than stored as plaintext.
- Each account has its own game-save file.
- Game progress can be restored after logging in.

**Important:** This is a local account system, not a cloud authentication service. Local files are not protected against someone who has access to the computer.

## 🧠 AI Integration

The AI Dungeon Master uses an OpenRouter-compatible API through the OpenAI Python SDK.

The AI generates narrative responses based on:
- Current room and environment.
- Player actions.
- Character health and inventory.
- Available exits and adventure context.

Game mechanics such as combat, inventory and progression are handled by Python rather than being controlled directly by AI-generated narrative.

## 🚀 Future Improvements

- More dungeon locations and quest lines.
- Additional enemy types and boss encounters.
- Enhanced character progression.
- Multiplayer adventures.
- Cloud-based player profiles.
- Improved AI memory and narrative consistency.
- Additional save-slot management.

## 👨‍💻 Developer

**Krishna Dwivedi**

B.Tech — Computer Science and Engineering  
Specialization: Artificial Intelligence and Analytics

GitHub: [@krishna060806](https://github.com/krishna060806)

---

*Explore the dungeon. Face the unknown. Become the legend.* 🐉