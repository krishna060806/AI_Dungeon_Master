import re
import hashlib
import secrets
import hmac
import copy
import json
import html
from pathlib import Path

import streamlit as st

from player import Player
from enemies import enemies
from boss import boss
from items import items
from rooms import rooms
from ai_engine import generate_story


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Dungeon Master | The Forgotten Dungeon",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# LOCAL ACCOUNT AND SAVE STORAGE
# =========================================================

ACCOUNTS_FILE = Path(__file__).with_name("accounts.json")

SAVE_DIR = Path(__file__).with_name("saves")
LEGACY_SAVE_FILE = Path(__file__).with_name("streamlit_save.json")

SAVE_DIR.mkdir(exist_ok=True)

PASSWORD_ITERATIONS = 310000


# =========================================================
# ROOM ARTWORK
# =========================================================

ROOM_ART = {
    "entrance": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23",
    "hall": "https://www.pakutaso.com/shared/img/thumb/AIbA-AIP682s-035_TP_V4.jpg",
    "treasure": "https://www.academis.eu/dungeon_explorer/_images/chest.png",
    "library": "https://images.unsplash.com/photo-1507842217343-583bb7270b66",
    "crypt": "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/items/777160/0730b70c84f1f6785f1d073acf8c2ede1956af14.jpg",
    "armory": "https://media.fab.com/image_previews/gallery_images/be8343e9-2974-4434-a792-c9d8fede3c21/fc7d1409-e426-4fe7-bad2-c814f9677bdd.jpg",
    "boss_room": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1600&q=85"
}


# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --gold: #e5b45f;
    --gold-light: #ffe3a2;
    --gold-dark: #805326;
    --red: #b52c2c;
    --red-light: #f05b4f;
    --green: #6eaa65;
    --blue: #4c9acb;
    --bg: #08090d;
    --panel: #121319;
    --panel2: #1b1b23;
    --border: #6b4b27;
    --text: #eee7dc;
    --muted: #a49b8e;
}

.stApp {
    background:
        radial-gradient(ellipse at 50% 0%, #302016 0%, transparent 38%),
        #08090d;
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1650px;
    padding: 1rem 1.2rem 1.5rem;
}

h1, h2, h3 {
    font-family: 'Cinzel', serif !important;
    color: var(--gold-light) !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #17151a, #090a0e);
    border-right: 2px solid var(--gold-dark);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.1rem;
}

.game-header {
    text-align: center;
    background: linear-gradient(90deg, #100d0c, #302016, #100d0c);
    border: 2px solid var(--gold-dark);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 18px;
    box-shadow: 0 5px 25px #0009, inset 0 0 25px #d99a3218;
    position: relative;
}

.game-header:before,
.game-header:after {
    content: "⚔";
    position: absolute;
    top: 18px;
    color: var(--gold);
    font-size: 30px;
}

.game-header:before { left: 25px; }
.game-header:after { right: 25px; }

.kicker {
    color: var(--gold);
    font-size: 9px;
    letter-spacing: 5px;
    text-transform: uppercase;
}

.game-title {
    font-family: 'Cinzel', serif;
    font-size: clamp(24px, 3vw, 39px);
    font-weight: 800;
    color: var(--gold-light);
    text-shadow: 0 0 18px #e8a63855;
}

.game-subtitle {
    color: #c7a77b;
    letter-spacing: 4px;
    font-family: 'Cinzel', serif;
    font-size: 12px;
}

.panel {
    background: linear-gradient(145deg, #1b191c, #101116);
    border: 1px solid var(--gold-dark);
    border-radius: 9px;
    padding: 13px;
    margin-bottom: 10px;
    box-shadow: inset 0 1px #ffffff08, 0 4px 12px #0007;
}

.section-title {
    font-family: 'Cinzel', serif;
    color: var(--gold-light);
    font-size: 16px;
    font-weight: 700;
    margin: 7px 0 10px;
    text-shadow: 0 0 10px #e5b45f22;
}

.ornament {
    text-align: center;
    color: var(--gold);
    letter-spacing: 5px;
    font-size: 12px;
    margin: 5px 0 9px;
}

.room-art {
    position: relative;
    height: 245px;
    background-size: cover;
    background-position: center;
    border: 2px solid var(--gold-dark);
    border-radius: 9px;
    overflow: hidden;
    box-shadow: 0 5px 20px #000b;
}

.room-art:after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
        0deg,
        rgba(0,0,0,.88) 0%,
        rgba(0,0,0,.12) 75%
    );
}

.room-art-label {
    position: absolute;
    z-index: 2;
    bottom: 15px;
    left: 17px;
    color: white;
    font-family: 'Cinzel', serif;
    font-size: 22px;
    font-weight: 700;
    text-shadow: 0 2px 8px black;
}

.room-description {
    background: linear-gradient(100deg, #d9b77f, #f1d9ac, #c49b61);
    color: #21160c;
    border: 3px double #76502a;
    border-radius: 7px;
    padding: 12px 15px;
    font-family: Georgia, serif;
    font-style: italic;
    font-size: 14px;
    margin-top: -1px;
    box-shadow: 0 4px 15px #0008;
}

.event {
    background: linear-gradient(100deg, #201f26, #15151b);
    border: 1px solid #393640;
    border-left: 3px solid #8b7b9c;
    border-radius: 6px;
    padding: 8px 10px;
    margin: 5px 0;
    font-size: 12px;
    line-height: 1.5;
}

.event-ai { border-left-color: #a78bd4; }

.event-combat {
    border-left-color: var(--red-light);
    background: linear-gradient(90deg, #321719, #17151b);
}

.event-reward {
    border-left-color: var(--gold);
    background: linear-gradient(90deg, #302416, #17151b);
}

.event-victory {
    border-left-color: var(--green);
    background: linear-gradient(90deg, #172719, #17151b);
}

.event-system { border-left-color: var(--blue); }

.hud-card {
    background: linear-gradient(145deg, #29232a, #111218);
    border: 1px solid var(--gold-dark);
    border-radius: 7px;
    padding: 9px;
    text-align: center;
}

.hud-label {
    color: #c5a675;
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.hud-value {
    color: var(--gold-light);
    font-family: 'Cinzel', serif;
    font-size: 22px;
    font-weight: 700;
}

.bar-label {
    font-size: 12px;
    color: var(--text);
    margin: 5px 0 3px;
}

.bar-track {
    height: 13px;
    background: #08090d;
    border: 1px solid #604a30;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: inset 0 2px 4px #000;
}

.bar-fill {
    height: 100%;
    border-radius: 20px;
    transition: width .3s ease;
}

.hp-fill {
    background: linear-gradient(90deg, #8d151b, #fa554c);
    box-shadow: 0 0 10px #f33a3a88;
}

.xp-fill {
    background: linear-gradient(90deg, #98601d, #ffda64);
    box-shadow: 0 0 10px #e9ad4488;
}

.enemy-panel {
    background: linear-gradient(110deg, #451719, #180f13);
    border: 1px solid #c34242;
    border-radius: 8px;
    padding: 11px;
    color: #ffd4d4;
}

.map-room {
    background: linear-gradient(100deg, #222027, #121319);
    border: 1px solid #45404a;
    border-radius: 6px;
    padding: 8px 10px;
    margin: 4px 0;
    font-size: 11px;
}

.map-current {
    border: 2px solid #e8b43c;
    background: linear-gradient(90deg, #49351a, #21180f);
    color: #ffe39b;
    box-shadow: 0 0 10px #e8b43c44;
}

.map-enemy { border-left: 3px solid #e94b4b; }
.map-cleared { border-left: 3px solid #6ca66a; }

.quest-row {
    background: #1c1b22;
    border: 1px solid #4c443d;
    border-radius: 6px;
    padding: 8px 10px;
    margin: 4px 0;
    font-size: 12px;
}

.quest-complete {
    border-color: #679966;
    color: #a7d7a3;
    background: #17231a;
}

.loot-item {
    background: linear-gradient(90deg, #332719, #17151a);
    border: 1px solid #98703b;
    border-radius: 6px;
    padding: 8px;
    color: var(--gold-light);
}

div.stButton > button {
    background: linear-gradient(180deg, #42352d, #201b1d);
    color: #fff0d5;
    border: 1px solid #a57b43;
    border-radius: 7px;
    min-height: 39px;
    font-family: 'Cinzel', serif;
    font-size: 11px;
    font-weight: 700;
    box-shadow: inset 0 1px #ffffff22, 0 3px 8px #0009;
    transition: all .2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(180deg, #8a632f, #493019);
    color: white;
    border-color: #ffe09b;
    box-shadow: 0 0 15px #e7b34b66;
    transform: translateY(-2px);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #c34331, #701b20);
    color: white;
    border: 1px solid #ff9b66;
    box-shadow: 0 0 12px #e4473655;
}

div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #f05a3b, #922126);
    box-shadow: 0 0 20px #ff554c88;
}

div.stButton > button:disabled {
    opacity: .3;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #29232a, #15151a);
    border: 1px solid #76552e;
    border-radius: 7px;
    padding: 8px;
}

[data-testid="stMetricValue"] {
    color: var(--gold-light);
    font-family: 'Cinzel', serif;
}

[data-testid="stMetricLabel"] {
    color: #c5a675;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #a12c25, #ff6950);
}

[data-testid="stForm"] {
    background: linear-gradient(145deg, #201c20, #111218);
    border: 1px solid var(--gold-dark);
    border-radius: 9px;
    padding: 12px;
}

input, textarea {
    background: #20212a !important;
    color: white !important;
}

hr {
    border-color: #57432d;
}

footer, #MainMenu {
    visibility: hidden;
}

@media (max-width: 900px) {
    .block-container {
        padding: .5rem;
    }

    .room-art {
        height: 180px;
    }

    .game-header:before,
    .game-header:after {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)
# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "authenticated_user": None,
    "started": False,
    "player": None,
    "current_room": "entrance",
    "current_enemy": None,
    "defeated_enemies": [],
    "collected_items": [],
    "collected_gold": [],
    "events": [],
    "completed": False,
    "game_over": False
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = copy.deepcopy(value)
# =========================================================
# EVENT HELPERS
# =========================================================

def add_event(message, category="system"):
    st.session_state.events.append({
        "message": str(message),
        "category": category
    })


# =========================================================
# ENEMY SYSTEM
# =========================================================

def setup_enemy():

    room_id = st.session_state.current_room
    enemy_type = rooms[room_id].get("enemy")

    st.session_state.current_enemy = None

    if not enemy_type:
        return

    enemy_id = f"{room_id}:{enemy_type}"

    if enemy_id in st.session_state.defeated_enemies:
        return

    if enemy_type == "dragon":
        data = copy.deepcopy(boss)

    elif enemy_type in enemies:
        data = copy.deepcopy(enemies[enemy_type])

    else:
        return

    data["id"] = enemy_id
    data["max_health"] = data["health"]

    st.session_state.current_enemy = data


# =========================================================
# ROOM SYSTEM
# =========================================================

def enter_room():

    room_id = st.session_state.current_room
    room = rooms[room_id]

    setup_enemy()

    add_event(f"You entered {room['name']}.", "system")

    enemy_type = room.get("enemy")
    enemy_id = f"{room_id}:{enemy_type}" if enemy_type else None

    if enemy_id and enemy_id in st.session_state.defeated_enemies:
        add_event(
            "The chamber is quiet. Your defeated enemy is gone.",
            "system"
        )
    else:
        add_event(room["description"], "ai")

    if room.get("gold", 0) and room_id not in st.session_state.collected_gold:

        amount = room["gold"]

        st.session_state.player.gold += amount
        st.session_state.collected_gold.append(room_id)

        add_event(f"You discovered {amount} gold!", "reward")


# =========================================================
# NEW GAME
# =========================================================

def new_game(name):

    name = name.strip() or "Unknown Hero"

    st.session_state.player = Player(name)
    st.session_state.current_room = "entrance"
    st.session_state.current_enemy = None
    st.session_state.defeated_enemies = []
    st.session_state.collected_items = []
    st.session_state.collected_gold = []
    st.session_state.events = []
    st.session_state.completed = False
    st.session_state.game_over = False
    st.session_state.started = True

    add_event(
        f"You awaken before an ancient dungeon hidden in mist. "
        f"Legends speak of a powerful artifact buried deep within. "
        f"A terrifying dragon guards the final treasure. "
        f"Your adventure begins, {name}.",
        "ai"
    )

    enter_room()

# =========================================================
# ACCOUNT MANAGEMENT
# =========================================================

def load_accounts():
    if not ACCOUNTS_FILE.exists():
        return {}

    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
            accounts = json.load(file)

        return accounts if isinstance(accounts, dict) else {}

    except (json.JSONDecodeError, OSError):
        return {}


def save_accounts(accounts):
    try:
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as file:
            json.dump(accounts, file, indent=4)

        return True

    except (OSError, TypeError, ValueError):
        return False


def valid_username(username):
    return bool(re.fullmatch(r"[a-z0-9_-]{3,20}", username))


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS
    )

    return {
        "salt": salt.hex(),
        "password_hash": password_hash.hex(),
        "iterations": PASSWORD_ITERATIONS
    }


def verify_password(password, account_data):
    try:
        salt = bytes.fromhex(account_data["salt"])
        expected_hash = bytes.fromhex(account_data["password_hash"])
        iterations = int(account_data["iterations"])

        if not 100000 <= iterations <= 1000000:
            return False

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations
        )

        return hmac.compare_digest(actual_hash, expected_hash)

    except (KeyError, TypeError, ValueError):
        return False


def register_account(username, password):
    username = username.strip().lower()

    if not valid_username(username):
        return False, "Username must be 3–20 characters: lowercase letters, numbers, _ or -."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    accounts = load_accounts()

    if username in accounts:
        return False, "That username already exists."

    accounts[username] = hash_password(password)

    if not save_accounts(accounts):
        return False, "Could not save account. Check folder permissions."

    return True, "Account created successfully. You can now log in."


def authenticate_account(username, password):
    username = username.strip().lower()
    accounts = load_accounts()

    account_data = accounts.get(username)

    if not account_data:
        return False

    return verify_password(password, account_data)


# =========================================================
# ACCOUNT SAVE PATH
# =========================================================

def get_user_save_path():
    username = st.session_state.authenticated_user

    if not username or not valid_username(username):
        return None

    return SAVE_DIR / f"{username}.json"


# =========================================================
# SAVE GAME
# =========================================================

def save_web_game():
    if not st.session_state.player:
        return False

    save_path = get_user_save_path()

    if save_path is None:
        return False

    data = {
        "story": st.session_state.events,
        "player": st.session_state.player.to_dict(),
        "current_room": st.session_state.current_room,
        "defeated_enemies": st.session_state.defeated_enemies,
        "collected_items": st.session_state.collected_items,
        "collected_gold": st.session_state.collected_gold,
        "current_enemy": st.session_state.current_enemy,
        "completed": st.session_state.completed,
        "game_over": st.session_state.game_over
    }

    try:
        temporary_path = save_path.with_suffix(".tmp")

        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        temporary_path.replace(save_path)

        return True

    except (OSError, TypeError, ValueError):
        return False


# =========================================================
# LOAD GAME
# =========================================================

def load_web_game():
    save_path = get_user_save_path()

    if save_path is None or not save_path.exists():
        return False

    try:
        with open(save_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        room_id = data["current_room"]

        if room_id not in rooms:
            return False

        player = Player.from_dict(data["player"])

        events = data.get("story", [])

        if not isinstance(events, list):
            events = []

        if events and isinstance(events[0], str):
            events = [
                {"message": event, "category": "system"}
                for event in events
            ]

        st.session_state.player = player
        st.session_state.current_room = room_id
        st.session_state.events = events
        st.session_state.defeated_enemies = data.get("defeated_enemies", [])
        st.session_state.collected_items = data.get("collected_items", [])
        st.session_state.collected_gold = data.get("collected_gold", [])
        st.session_state.current_enemy = data.get("current_enemy")
        st.session_state.completed = data.get("completed", False)
        st.session_state.game_over = data.get("game_over", False)
        st.session_state.started = True

        if st.session_state.current_enemy is None:
            setup_enemy()

        return True

    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, ValueError, OSError):
        return False


# =========================================================
# IMPORT OLD SAVE
# =========================================================

def import_legacy_save():
    if not LEGACY_SAVE_FILE.exists():
        return False

    user_save = get_user_save_path()

    if user_save is None or user_save.exists():
        return False

    try:
        with open(LEGACY_SAVE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        room_id = data.get("current_room")

        if room_id not in rooms or "player" not in data:
            return False

        player = Player.from_dict(data["player"])

        events = data.get("story", [])

        if not isinstance(events, list):
            events = []

        if events and isinstance(events[0], str):
            events = [
                {"message": event, "category": "system"}
                for event in events
            ]

        st.session_state.player = player
        st.session_state.current_room = room_id
        st.session_state.events = events
        st.session_state.defeated_enemies = data.get("defeated_enemies", [])
        st.session_state.collected_items = data.get("collected_items", [])
        st.session_state.collected_gold = data.get("collected_gold", [])
        st.session_state.current_enemy = data.get("current_enemy")
        st.session_state.completed = data.get("completed", False)
        st.session_state.game_over = data.get("game_over", False)
        st.session_state.started = True

        if st.session_state.current_enemy is None:
            setup_enemy()

        return save_web_game()

    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, ValueError, OSError):
        return False
    # =========================================================
# RESTORE SESSION ACCOUNT STATE
# =========================================================

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None


# =========================================================
# MOVEMENT
# =========================================================

def move(direction):

    if st.session_state.current_enemy:
        add_event("Defeat the enemy before leaving!", "system")
        return

    room = rooms[st.session_state.current_room]
    destination = room.get(direction)

    if not destination:
        add_event("You cannot go that way.", "system")
        return

    if destination == "boss_room":
        if (
            "Ancient Artifact" not in st.session_state.player.inventory
            and not st.session_state.completed
        ):
            add_event(
                "The ancient gate refuses to open. "
                "Only the bearer of the Ancient Artifact may enter.",
                "system"
            )
            return

    st.session_state.current_room = destination
    enter_room()
    save_web_game()


# =========================================================
# LEVELING
# =========================================================

def award_xp(amount):

    player = st.session_state.player
    player.xp += amount

    add_event(f"+{amount} XP", "reward")

    while player.xp >= player.xp_to_next:

        player.xp -= player.xp_to_next
        player.level += 1
        player.xp_to_next += 50
        player.max_health += 20
        player.attack += 5
        player.health = player.max_health

        add_event(
            f"LEVEL UP! Level {player.level}. "
            "+20 Maximum Health. +5 Base Attack. "
            "Health fully restored!",
            "victory"
        )


# =========================================================
# COMBAT
# =========================================================

def attack_enemy():

    enemy = st.session_state.current_enemy
    player = st.session_state.player

    if not enemy:
        return

    damage = player.get_attack(items)
    enemy["health"] -= damage

    add_event(
        f"You attacked {enemy['name']} and dealt {damage} damage!",
        "combat"
    )

    if enemy["health"] <= 0:

        add_event(f"{enemy['name']} DEFEATED!", "victory")

        gold = enemy.get("gold", 0)
        xp = enemy.get("xp", 0)

        player.gold += gold
        add_event(f"You received {gold} gold!", "reward")
        award_xp(xp)

        st.session_state.defeated_enemies.append(enemy["id"])
        st.session_state.current_enemy = None

        if enemy["name"].lower() == "dragon":

            st.session_state.completed = True

            add_event(
                "You defeated the Dragon and conquered the Forgotten Dungeon!",
                "victory"
            )

        save_web_game()
        return

    incoming = enemy["damage"]
    player.take_damage(incoming)

    add_event(
        f"{enemy['name']} attacked you for {incoming} damage. "
        f"Your HP: {player.health}/{player.max_health}",
        "combat"
    )

    if player.health <= 0:

        st.session_state.game_over = True
        add_event("GAME OVER. Your adventure has ended.", "combat")

    save_web_game()


# =========================================================
# INVENTORY
# =========================================================

def take_item(item_name):

    room = rooms[st.session_state.current_room]

    for item in room.get("items", []):

        if item.lower() == item_name.lower():

            item_id = f"{st.session_state.current_room}:{item}"

            if item_id in st.session_state.collected_items:
                add_event(f"{item} has already been collected.", "system")
                return

            if st.session_state.player.add_item(item):

                st.session_state.collected_items.append(item_id)
                add_event(f"ITEM COLLECTED: {item}", "reward")
                save_web_game()

            else:
                add_event(f"You already have {item}.", "system")

            return

    add_event(f"{item_name} is not available here.", "system")


def equip_item(item_name):

    player = st.session_state.player

    actual = next(
        (item for item in player.inventory if item.lower() == item_name.lower()),
        None
    )

    if not actual:
        add_event("You don't own that item.", "system")
        return

    data = items.get(actual.lower(), {})

    if data.get("type") != "weapon":
        add_event("That item cannot be equipped.", "system")
        return

    player.weapon = actual

    add_event(
        f"{actual} equipped! Total attack: {player.get_attack(items)}",
        "reward"
    )

    save_web_game()


def use_item(item_name):

    player = st.session_state.player

    actual = next(
        (item for item in player.inventory if item.lower() == item_name.lower()),
        None
    )

    if not actual:
        add_event("You don't have that item.", "system")
        return

    data = items.get(actual.lower(), {})

    if "heal" not in data:
        add_event("This item cannot be used.", "system")
        return

    healed = player.heal(data["heal"])

    if healed == 0:
        add_event("Your health is already full.", "system")
        return

    player.remove_item(actual)

    add_event(f"You restored {healed} HP!", "reward")
    save_web_game()


# =========================================================
# AI DUNGEON MASTER
# =========================================================

def ask_ai(action):

    player = st.session_state.player
    room = rooms[st.session_state.current_room]

    exits = [
        direction for direction in ["north", "south", "east", "west"]
        if room.get(direction)
    ]

    context = (
        f"Current room: {room['name']}\n"
        f"Description: {room['description']}\n"
        f"Available exits: {', '.join(exits)}\n"
        f"Player: {player.name}\n"
        f"Health: {player.health}/{player.max_health}\n"
        f"Inventory: {', '.join(player.inventory)}"
    )

    try:

        response = generate_story(action, context)

        if not response:
            add_event("The dungeon remains silent.", "ai")
            return

        safe_lines = [
            line for line in response.splitlines()
            if not line.strip().upper().startswith("ITEM:")
        ]

        safe_response = "\n".join(safe_lines).strip()

        if safe_response:
            add_event(safe_response, "ai")

        save_web_game()

    except Exception as error:
        add_event(f"AI Error: {error}", "system")


# =========================================================
# GAME HEADER
# =========================================================

st.markdown("""
<div class="game-header">
    <div class="kicker">An AI-powered text adventure</div>
    <div class="game-title">⚔ AI DUNGEON MASTER ⚔</div>
    <div class="game-subtitle">THE FORGOTTEN DUNGEON</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# AUTHENTICATION SCREEN
# =========================================================

if not st.session_state.authenticated_user:

    st.markdown("## 🏰 Welcome, Adventurer")
    st.write("Login to continue your journey or create a new player account.")

    login_tab, register_tab = st.tabs(["🔐 LOGIN", "📝 REGISTER"])

    with login_tab:

        with st.form("login_form"):

            login_username = st.text_input("Username")
            login_password = st.text_input("Password", type="password")

            login_submit = st.form_submit_button(
                "⚔ LOGIN",
                type="primary",
                use_container_width=True
            )

            if login_submit:

                username = login_username.strip().lower()

                if authenticate_account(username, login_password):

                    st.session_state.authenticated_user = username
                    st.rerun()

                else:
                    st.error("Incorrect username or password.")

    with register_tab:

        with st.form("register_form"):

            register_username = st.text_input("Choose Username")
            register_password = st.text_input(
                "Choose Password",
                type="password"
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            register_submit = st.form_submit_button(
                "📝 CREATE ACCOUNT",
                type="primary",
                use_container_width=True
            )

            if register_submit:

                if register_password != confirm_password:

                    st.error("Passwords do not match.")

                else:

                    success, message = register_account(
                        register_username,
                        register_password
                    )

                    if success:
                        st.success(message)
                        st.info("You can now log in.")
                    else:
                        st.error(message)

    st.stop()


# =========================================================
# PLAYER LANDING PAGE
# =========================================================

if not st.session_state.started:

    username = st.session_state.authenticated_user
    save_path = get_user_save_path()

    left, right = st.columns([1.4, 1])

    with left:

        st.markdown("## Enter the Forgotten Dungeon")
        st.success(f"Logged in as: {username}")

        st.write(
            "A forgotten artifact lies beneath ancient stone. "
            "Enemies guard the path, and a dragon waits beyond the sealed gate."
        )

        hero_name = st.text_input(
            "Choose Your Hero Name",
            value="Haku",
            key="hero_name_input"
        )

        if st.button(
            "⚔ BEGIN NEW ADVENTURE",
            type="primary",
            use_container_width=True
        ):

            new_game(hero_name)
            save_web_game()
            st.rerun()

        st.markdown("### Previous Progress")

        if save_path and save_path.exists():

            if st.button(
                "📜 CONTINUE SAVED ADVENTURE",
                use_container_width=True
            ):

                if load_web_game():
                    st.rerun()
                else:
                    st.error("Your save file could not be loaded.")

        else:
            st.caption("No saved adventure found for this account.")

        if LEGACY_SAVE_FILE.exists() and not (
            save_path and save_path.exists()
        ):

            if st.button(
                "📦 IMPORT PREVIOUS ADVENTURE",
                use_container_width=True
            ):

                if import_legacy_save():
                    st.success("Previous adventure imported!")
                    st.rerun()
                else:
                    st.error("Could not import the previous save.")

        if st.button("🚪 LOG OUT", use_container_width=True):

            st.session_state.authenticated_user = None
            st.rerun()

    with right:

        st.markdown("""
        <div class="panel">
            <div class="section-title">YOUR JOURNEY</div>
            <div class="ornament">✦ ━━━━━ ✦</div>
            <p>🗺 Explore seven connected chambers.</p>
            <p>⚔ Fight enemies and the final Dragon.</p>
            <p>🎒 Collect weapons and potions.</p>
            <p>⭐ Earn experience and level up.</p>
            <p>🐉 Find the Ancient Artifact.</p>
        </div>
        """, unsafe_allow_html=True)

    st.stop()
    # =========================================================
# CHARACTER HUD
# =========================================================

player = st.session_state.player

with st.sidebar:

    st.markdown("## 🧙 CHARACTER")
    st.markdown(f"### {html.escape(player.name)}")
    st.caption(f"LEVEL {player.level}")

    hp_percent = max(
        0,
        min(100, player.health / player.max_health * 100)
    )

    xp_percent = max(
        0,
        min(100, player.xp / player.xp_to_next * 100)
    )

    st.markdown(
        f'<div class="bar-label">❤️ HP {player.health}/{player.max_health}</div>'
        f'<div class="bar-track"><div class="bar-fill hp-fill" style="width:{hp_percent}%"></div></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="bar-label">⭐ XP {player.xp}/{player.xp_to_next}</div>'
        f'<div class="bar-track"><div class="bar-fill xp-fill" style="width:{xp_percent}%"></div></div>',
        unsafe_allow_html=True
    )

    st.markdown("")

    gold_col, attack_col = st.columns(2)

    with gold_col:
        st.markdown(
            f'<div class="hud-card"><div class="hud-label">🪙 GOLD</div>'
            f'<div class="hud-value">{player.gold}</div></div>',
            unsafe_allow_html=True
        )

    with attack_col:
        st.markdown(
            f'<div class="hud-card"><div class="hud-label">⚔ ATTACK</div>'
            f'<div class="hud-value">{player.get_attack(items)}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("")
    st.caption(f"🗡 EQUIPPED WEAPON: {player.weapon or 'None'}")

    st.markdown(
        '<div class="ornament">✦ ━━━━━ ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown("## 🎒 INVENTORY")

    if player.inventory:

        for item in player.inventory:

            equipped = (
                " ✓ EQUIPPED"
                if player.weapon and item.lower() == player.weapon.lower()
                else ""
            )

            st.write(f"• {item}{equipped}")

    else:
        st.caption("Inventory empty.")

    weapons_owned = [
        item for item in player.inventory
        if items.get(item.lower(), {}).get("type") == "weapon"
    ]

    if weapons_owned:

        selected_weapon = st.selectbox(
            "Choose weapon",
            weapons_owned
        )

        if st.button("⚔ EQUIP WEAPON", use_container_width=True):

            equip_item(selected_weapon)
            st.rerun()

    healing_items = [
        item for item in player.inventory
        if items.get(item.lower(), {}).get("heal")
    ]

    if healing_items:

        selected_potion = st.selectbox(
            "Choose healing item",
            healing_items
        )

        if st.button("🧪 USE ITEM", use_container_width=True):

            use_item(selected_potion)
            st.rerun()

    st.markdown(
        '<div class="ornament">✦ ━━━━━ ✦</div>',
        unsafe_allow_html=True
    )

    if st.button("💾 SAVE ADVENTURE", use_container_width=True):

        if save_web_game():
            st.success("Adventure saved!")
        else:
            st.error("Save failed.")

    st.caption(
        f"Logged in as: {st.session_state.authenticated_user}"
    )

    if st.button("🔄 SWITCH ACCOUNT / LOG OUT", use_container_width=True):

        save_web_game()

        st.session_state.authenticated_user = None

        for key, value in DEFAULTS.items():

            if key != "authenticated_user":
                st.session_state[key] = copy.deepcopy(value)

        st.rerun()


# =========================================================
# MAIN GAME LAYOUT
# =========================================================

room_id = st.session_state.current_room
room = rooms[room_id]
enemy = st.session_state.current_enemy

main_col, side_col = st.columns([1.7, 1], gap="medium")


# =========================================================
# MAIN GAME AREA
# =========================================================

with main_col:

    st.markdown(
        f'<div class="section-title">📍 {html.escape(room["name"])}</div>',
        unsafe_allow_html=True
    )

    art_url = ROOM_ART.get(room_id, ROOM_ART["entrance"])

    st.markdown(
        f'<div class="room-art" style="background-image:'
        f'linear-gradient(0deg,#0009,#0002),url({art_url});">'
        f'<div class="room-art-label">{html.escape(room["name"])}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if enemy:

        enemy_percent = max(
            0,
            min(100, enemy["health"] / enemy["max_health"] * 100)
        )

        st.markdown(
            f'<div class="enemy-panel">'
            f'<strong>☠ {html.escape(enemy["name"])}</strong>'
            f'<div class="bar-label">ENEMY HP: {max(0, enemy["health"])} / {enemy["max_health"]}</div>'
            f'<div class="bar-track"><div class="bar-fill hp-fill" style="width:{enemy_percent}%"></div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    else:

        enemy_type = room.get("enemy")
        enemy_id = f"{room_id}:{enemy_type}" if enemy_type else None

        if enemy_id and enemy_id in st.session_state.defeated_enemies:
            description = "This chamber is quiet. Your defeated enemy is gone."
        else:
            description = room["description"]

        st.markdown(
            f'<div class="room-description">{html.escape(description)}</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="ornament">✦ ━━━━━ ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">📖 ADVENTURE CHRONICLES</div>',
        unsafe_allow_html=True
    )

    with st.container(height=235, border=True):

        for event in st.session_state.events:

            category = event.get("category", "system")

            message = html.escape(
                event.get("message", "")
            ).replace("\n", "<br>")

            css = {
                "ai": "event-ai",
                "combat": "event-combat",
                "reward": "event-reward",
                "victory": "event-victory",
                "system": "event-system"
            }.get(category, "event-system")

            st.markdown(
                f'<div class="event {css}">{message}</div>',
                unsafe_allow_html=True
            )

    if enemy and not st.session_state.game_over:

        if st.button(
            "⚔ ATTACK THE ENEMY",
            type="primary",
            use_container_width=True
        ):

            attack_enemy()
            st.rerun()

    st.markdown(
        '<div class="ornament">✦ ━━━━━ ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">✨ THE DUNGEON MASTER</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.completed and not st.session_state.game_over:

        with st.form("action_form", clear_on_submit=True):

            action = st.text_input(
                "What will you do?",
                placeholder="Examine the strange symbols..."
            )

            submitted = st.form_submit_button(
                "✦ SEND ACTION ✦",
                use_container_width=True
            )

        if submitted and action.strip():

            if st.session_state.current_enemy:

                add_event(
                    "Defeat the enemy before taking another action.",
                    "system"
                )

            else:
                ask_ai(action.strip())

            st.rerun()
            # =========================================================
# RIGHT GAME PANEL
# =========================================================

with side_col:

    st.markdown(
        '<div class="section-title">🧭 MOVEMENT</div>',
        unsafe_allow_html=True
    )

    _, north_col, _ = st.columns([1, 1, 1])

    with north_col:

        if room.get("north"):

            if st.button(
                "⬆ NORTH",
                use_container_width=True,
                disabled=bool(enemy)
            ):
                move("north")
                st.rerun()

    west_col, center_col, east_col = st.columns(3)

    with west_col:

        if room.get("west"):

            if st.button(
                "⬅ WEST",
                use_container_width=True,
                disabled=bool(enemy)
            ):
                move("west")
                st.rerun()

    with center_col:

        st.markdown(
            '<div style="text-align:center;color:#e5b45f;'
            'padding-top:10px;font-size:20px;">✥</div>',
            unsafe_allow_html=True
        )

    with east_col:

        if room.get("east"):

            if st.button(
                "EAST ➡",
                use_container_width=True,
                disabled=bool(enemy)
            ):
                move("east")
                st.rerun()

    _, south_col, _ = st.columns([1, 1, 1])

    with south_col:

        if room.get("south"):

            if st.button(
                "⬇ SOUTH",
                use_container_width=True,
                disabled=bool(enemy)
            ):
                move("south")
                st.rerun()

    # -----------------------------------------------------
    # TREASURES
    # -----------------------------------------------------

    st.markdown(
        '<div class="ornament">✦ ━━━━━ ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">💎 TREASURES</div>',
        unsafe_allow_html=True
    )

    available_items = []

    for item in room.get("items", []):

        item_id = f"{room_id}:{item}"

        if item_id not in st.session_state.collected_items:
            available_items.append(item)

    if available_items:

        for item in available_items:

            if st.button(
                f"✧ COLLECT {item.upper()}",
                use_container_width=True
            ):
                take_item(item)
                st.rerun()

    else:

        st.caption("No uncollected treasures in this chamber.")

    # -----------------------------------------------------
    # QUEST JOURNAL
    # -----------------------------------------------------

    st.markdown(
        '<div class="ornament">✦ ━━━━━ ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">📜 QUEST JOURNAL</div>',
        unsafe_allow_html=True
    )

    artifact_found = (
        "Ancient Artifact" in player.inventory
    )

    artifact_css = (
        "quest-row quest-complete"
        if artifact_found else "quest-row"
    )

    dragon_css = (
        "quest-row quest-complete"
        if st.session_state.completed else "quest-row"
    )

    st.markdown(
        f'<div class="{artifact_css}">'
        f'{"✓" if artifact_found else "○"} '
        f'Find the Ancient Artifact</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="{dragon_css}">'
        f'{"✓" if st.session_state.completed else "○"} '
        f'Defeat the Dragon</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # DUNGEON ATLAS
    # -----------------------------------------------------

    st.markdown(
        '<div class="ornament">✦ ━━━━━ ✦</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">🗺 DUNGEON ATLAS</div>',
        unsafe_allow_html=True
    )

    for map_id, map_room in rooms.items():

        enemy_type = map_room.get("enemy")
        status = ""
        css = ""

        if enemy_type:

            enemy_id = f"{map_id}:{enemy_type}"

            if enemy_id in st.session_state.defeated_enemies:

                status = " ✓ CLEARED"
                css = "map-cleared"

            else:

                status = " ⚔ ENEMY"
                css = "map-enemy"

        if (
            map_id == "boss_room"
            and not artifact_found
            and not st.session_state.completed
        ):

            status += " 🔒 LOCKED"

        if map_id == room_id:
            css += " map-current"

        st.markdown(
            f'<div class="map-room {css}">'
            f'<strong>{html.escape(map_room["name"])}</strong>'
            f'{html.escape(status)}</div>',
            unsafe_allow_html=True
        )


# =========================================================
# END GAME
# =========================================================

if st.session_state.completed:

    st.divider()

    st.success(
        "🏆 YOU HAVE CONQUERED THE FORGOTTEN DUNGEON!"
    )

    player.show_stats()

    if st.button(
        "⚔ BEGIN A NEW ADVENTURE",
        type="primary"
    ):

        new_game(player.name)
        save_web_game()
        st.rerun()


elif st.session_state.game_over:

    st.divider()

    st.error("☠ GAME OVER")

    if st.button(
        "TRY AGAIN",
        type="primary"
    ):

        new_game(player.name)
        save_web_game()
        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="ornament">✦ ━━━━━━━━━━━━━━━━━━━━━ ✦</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="text-align:center;color:#927957;'
    'font-size:10px;letter-spacing:3px;">'
    'AI DUNGEON MASTER · THE FORGOTTEN DUNGEON · WEB EDITION'
    '</div>',
    unsafe_allow_html=True
)