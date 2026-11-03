
import copy

from player import Player
from enemies import enemies
from boss import boss
from items import items
from rooms import rooms

from ai_engine import generate_story
from story import (
    add_event,
    get_story,
    get_all_story,
    set_story,
    clear_story
)

from save_manager import save_game, load_game
from item_detector import detect_item


class Game:

    def __init__(self):

        self.player = None
        self.current_room = "entrance"

        self.defeated_enemies = []
        self.collected_items = []
        self.collected_gold = []

        self.current_enemy = None
        self.running = False
        self.completed = False

        print("\n==============================")
        print("   AI DUNGEON MASTER v2.0")
        print("      THE FORGOTTEN DUNGEON")
        print("==============================")

        while True:

            print("\n1. New Game")
            print("2. Load Game")
            print("3. Quit")

            choice = input("\nChoose: ").strip()

            if choice == "1":
                self.new_game()
                break

            elif choice == "2":

                if self.load_saved_game():
                    break

                print("\nNo valid save found.")

            elif choice == "3":
                return

            else:
                print("\nInvalid choice.")

    # -------------------------
    # NEW GAME
    # -------------------------

    def new_game(self):

        clear_story()

        self.player = Player()

        name = input("\nEnter your hero name: ").strip()

        if not name:
            name = "Unknown Hero"

        self.player.name = name

        self.current_room = "entrance"

        self.defeated_enemies = []
        self.collected_items = []
        self.collected_gold = []

        self.current_enemy = None
        self.completed = False
        self.running = True

        add_event(
            f"""
Hero Name: {name}

You awaken before an ancient dungeon hidden in mist.

Legends speak of a powerful artifact buried deep
within the forgotten chambers.

A terrifying dragon guards the final treasure.

Your adventure begins...
"""
        )

        print("\nNew adventure created!")

        self.enter_room()

    # -------------------------
    # SAVE GAME
    # -------------------------

    def save(self):

        data = {
            "story": get_all_story(),

            "player": self.player.to_dict(),

            "current_room": self.current_room,

            "defeated_enemies": self.defeated_enemies,

            "collected_items": self.collected_items,

            "collected_gold": self.collected_gold,

            "current_enemy": self.current_enemy,

            "completed": self.completed
        }

        if save_game(data):

            print("\nGame Saved Successfully!")

        else:

            print("\nUnable to save game.")

    # -------------------------
    # LOAD GAME
    # -------------------------

    def load_saved_game(self):

        data = load_game()

        if not data:
            return False

        try:

            self.player = Player.from_dict(data["player"])

            room_id = data["current_room"]

            if room_id not in rooms:
                return False

            self.current_room = room_id

            set_story(data["story"])

            self.defeated_enemies = data.get(
                "defeated_enemies", []
            )

            self.collected_items = data.get(
                "collected_items", []
            )

            self.collected_gold = data.get(
                "collected_gold", []
            )

            self.completed = data.get(
                "completed", False
            )

            self.current_enemy = data.get("current_enemy")

            if self.current_enemy is None:
                self.setup_enemy()

            self.running = not self.completed

            print("\nGame Loaded Successfully!")

            if self.completed:

                print("\nThis adventure has already been completed.")

            return True

        except (KeyError, TypeError, ValueError) as error:

            print(f"\nLoad error: {error}")

            return False

    # -------------------------
    # PLAYER STATUS
    # -------------------------

    def show_quest(self):

        print("\n=== MAIN QUEST ===")

        if "Ancient Artifact" in self.player.inventory:

            print("[COMPLETED] Find the Ancient Artifact")

        else:

            print("[PENDING] Find the Ancient Artifact")

        if self.completed:

            print("[COMPLETED] Defeat the Dragon")

        else:

            print("[PENDING] Defeat the Dragon")

    # -------------------------
    # ROOM SYSTEM
    # -------------------------

    def enter_room(self):

        room = rooms[self.current_room]

        print("\n==============================")
        print(room["name"].upper())
        print("==============================")

        enemy_type = room.get("enemy")

        enemy_id = (
            f"{self.current_room}:{enemy_type}"
            if enemy_type else None
        )

        if enemy_id and enemy_id in self.defeated_enemies:

            print("The room is quiet. Your defeated enemy is gone.")

        else:

            print(room["description"])

        self.setup_enemy()

        if room["gold"] > 0:

            if self.current_room not in self.collected_gold:

                self.player.gold += room["gold"]

                self.collected_gold.append(
                    self.current_room
                )

                print(f"\n[FOUND GOLD: {room['gold']}]")

        if self.current_enemy:

            print(
                f"\n[WARNING: "
                f"{self.current_enemy['name']} APPEARED!]"
            )

    def setup_enemy(self):

        room = rooms[self.current_room]

        enemy_type = room.get("enemy")

        self.current_enemy = None

        if not enemy_type:
            return

        enemy_id = f"{self.current_room}:{enemy_type}"

        if enemy_id in self.defeated_enemies:
            return

        if enemy_type == "dragon":

            self.current_enemy = copy.deepcopy(boss)

        elif enemy_type in enemies:

            self.current_enemy = copy.deepcopy(
                enemies[enemy_type]
            )

        if self.current_enemy:

            self.current_enemy["id"] = enemy_id

    # -------------------------
    # DUNGEON MAP
    # -------------------------

    def show_map(self):

        print("\n========== DUNGEON MAP ==========")

        for room_id, room in rooms.items():

            status = ""

            enemy_type = room.get("enemy")

            if enemy_type:

                enemy_id = f"{room_id}:{enemy_type}"

                if enemy_id in self.defeated_enemies:
                    status = " [CLEARED]"
                else:
                    status = " [ENEMY]"

            if (
                room_id == "boss_room"
                and "Ancient Artifact" not in self.player.inventory
                and not self.completed
            ):

                status = " [LOCKED: ARTIFACT REQUIRED]"

            print(f"\n{room['name']}{status}")

            for direction in [
                "north", "south", "east", "west"
            ]:

                destination = room.get(direction)

                if destination:

                    print(
                        f"  {direction.title()} -> "
                        f"{rooms[destination]['name']}"
                    )

        print(
            f"\nCurrent Location: "
            f"{rooms[self.current_room]['name']}"
        )

    # -------------------------
    # ROOM MOVEMENT
    # -------------------------

    def move(self, direction):

        if self.current_enemy:

            print("\nDefeat the enemy before leaving!")

            return

        room = rooms[self.current_room]

        destination = room.get(direction)

        if not destination:

            print("\nYou cannot go that way.")

            return

        if destination == "boss_room":

            if (
                "Ancient Artifact" not in self.player.inventory
                and not self.completed
            ):

                print("\nThe ancient door refuses to open.")

                print(
                    "A magical voice whispers: "
                    "'Only the bearer of the Ancient Artifact "
                    "may enter.'"
                )

                return

        self.current_room = destination

        add_event(
            f"Player travelled to "
            f"{rooms[destination]['name']}."
        )

        self.enter_room()

    # -------------------------
    # COMBAT SYSTEM
    # -------------------------

    def attack_enemy(self):

        if not self.current_enemy:

            print("\nThere is no enemy here.")

            return

        enemy = self.current_enemy

        damage = self.player.get_attack(items)

        enemy["health"] -= damage

        print(
            f"\nYou attacked {enemy['name']} "
            f"and dealt {damage} damage!"
        )

        print(
            f"Enemy HP: {max(0, enemy['health'])}"
        )

        if enemy["health"] <= 0:

            print(f"\n{enemy['name']} DEFEATED!")

            gold_reward = enemy.get("gold", 0)

            xp_reward = enemy.get("xp", 0)

            self.player.gold += gold_reward

            print(
                f"You received {gold_reward} gold!"
            )

            self.player.gain_xp(xp_reward)

            self.defeated_enemies.append(
                enemy["id"]
            )

            add_event(
                f"{enemy['name']} was defeated by "
                f"{self.player.name}."
            )

            self.current_enemy = None

            if enemy["name"].lower() == "dragon":

                self.victory()

            return

        enemy_damage = enemy["damage"]

        self.player.take_damage(enemy_damage)

        print(
            f"\n{enemy['name']} attacked you "
            f"for {enemy_damage} damage!"
        )

        print(
            f"Your HP: "
            f"{self.player.health}/"
            f"{self.player.max_health}"
        )

        if self.player.health <= 0:

            self.defeat()

    # -------------------------
    # VICTORY AND DEFEAT
    # -------------------------

    def victory(self):

        self.completed = True

        self.running = False

        print("\n================================")
        print("       DUNGEON COMPLETED!")
        print("================================")

        print(
            f"\nCongratulations, {self.player.name}!"
        )

        print(
            "You defeated the Dragon and conquered "
            "the Forgotten Dungeon."
        )

        print("\n=== FINAL RESULTS ===")

        self.player.show_stats()

        print(
            "\nThe Ancient Artifact is finally yours."
        )

        add_event(
            f"{self.player.name} completed the Forgotten Dungeon."
        )

        print("\nTHE END.")

    def defeat(self):

        self.running = False

        print("\n================================")
        print("          GAME OVER")
        print("================================")

        print(
            f"\n{self.player.name} has fallen "
            "inside the Forgotten Dungeon."
        )

        print("Your adventure has ended.")

    # -------------------------
    # INVENTORY SYSTEM
    # -------------------------

    def show_inventory(self):

        print("\n========== INVENTORY ==========")

        if not self.player.inventory:

            print("Your inventory is empty.")

            return

        for index, item in enumerate(
            self.player.inventory,
            start=1
        ):

            equipped = ""

            if (
                self.player.weapon
                and item.lower() == self.player.weapon.lower()
            ):

                equipped = " [EQUIPPED]"

            print(
                f"{index}. {item}{equipped}"
            )

    # -------------------------
    # EQUIPMENT SYSTEM
    # -------------------------

    def equip_item(self, item_name):

        actual_item = next(
            (
                item for item in self.player.inventory
                if item.lower() == item_name.lower()
            ),
            None
        )

        if not actual_item:

            print("\nYou don't own that item.")

            return

        item_data = items.get(
            actual_item.lower()
        )

        if (
            not item_data
            or item_data.get("type") != "weapon"
        ):

            print("\nThat item cannot be equipped.")

            return

        self.player.weapon = actual_item

        print(
            f"\n{actual_item} equipped!"
        )

        print(
            f"Total attack: "
            f"{self.player.get_attack(items)}"
        )

    # -------------------------
    # ITEM USAGE
    # -------------------------

    def use_item(self, item_name):

        actual_item = next(
            (
                item for item in self.player.inventory
                if item.lower() == item_name.lower()
            ),
            None
        )

        if not actual_item:

            print("\nYou don't have that item.")

            return

        item_data = items.get(
            actual_item.lower(), {}
        )

        if "heal" not in item_data:

            print("\nThis item cannot be used.")

            return

        healed = self.player.heal(
            item_data["heal"]
        )

        if healed == 0:

            print("\nYour health is already full.")

            return

        self.player.remove_item(actual_item)

        print(
            f"\nYou restored {healed} HP!"
        )

        print(
            f"Health: {self.player.health}/"
            f"{self.player.max_health}"
        )

    # -------------------------
    # ITEM COLLECTION
    # -------------------------

    def take_item(self, item_name):

        room = rooms[self.current_room]

        requested_items = [
            item.strip().lower()
            for item in item_name.split(" and ")
        ]

        for requested in requested_items:

            found = False

            for item in room["items"]:

                item_id = f"{self.current_room}:{item}"

                if item.lower() == requested:

                    found = True

                    if item_id in self.collected_items:

                        print(
                            f"\n{item} has already been collected."
                        )

                        break

                    self.player.add_item(item)

                    self.collected_items.append(
                        item_id
                    )

                    print(
                        f"\n[ITEM COLLECTED: {item}]"
                    )

                    break

            if not found:

                print(
                    f"\n{requested.title()} "
                    "is not available here."
                )

    # -------------------------
    # AI STORY GENERATION
    # -------------------------

    def ai_action(self, action):

        print("\nGenerating story...")

        try:

            room = rooms[self.current_room]

            available_exits = [
                direction
                for direction in [
                    "north", "south", "east", "west"
                ]
                if room.get(direction)
            ]

            context = (
                f"Current room: {room['name']}\n"
                f"Description: {room['description']}\n"
                f"Available exits: "
                f"{', '.join(available_exits)}\n"
                f"Player: {self.player.name}\n"
                f"Health: {self.player.health}\n"
                f"Inventory: "
                f"{', '.join(self.player.inventory)}\n"
                f"Story so far:\n{get_story()}"
            )

            response = generate_story(
                action,
                context
            )

            if not response:

                print("\nThe dungeon remains silent.")

                return

            add_event(f"Player: {action}")

            add_event(response)

            item = detect_item(response)

            if item:

                if self.player.add_item(item):

                    print(
                        f"\n[ITEM ADDED: {item}]"
                    )

            print("\n" + response)

            print(
                "\nUse 'map' to see actual dungeon exits."
            )

        except Exception as error:

            print(f"\nAI Error: {error}")

    # -------------------------
    # MAIN GAME LOOP
    # -------------------------

    def start(self):

        if not self.running:

            return

        print("\n" + get_story())

        print("""
========== COMMANDS ==========

look
map
quest
go north
go south
go east
go west
attack
stats
inventory
equip sword
equip longsword
equip shadow blade
use potion
use greater potion
take sword
take ancient artifact
save
load
quit
""")

        while self.running:

            action = input("\n> ").strip()

            if not action:

                continue

            command = action.lower()

            if command == "quit":

                print("\nLeaving the dungeon...")

                break

            elif command == "save":

                self.save()

                continue

            elif command == "load":

                if self.load_saved_game():

                    if self.running:
                        print(get_story())

                else:

                    print("\nNo valid save found.")

                continue

            elif command == "inventory":

                self.show_inventory()

                continue

            elif command == "stats":

                self.player.show_stats()

                continue

            elif command == "quest":

                self.show_quest()

                continue

            elif command == "map":

                self.show_map()

                continue

            elif command == "look":

                self.enter_room()

                continue

            elif command == "attack":

                self.attack_enemy()

                continue

            elif command.startswith("go "):

                direction = command[3:].strip()

                if direction in [
                    "north", "south", "east", "west"
                ]:

                    self.move(direction)

                else:

                    print("\nInvalid direction.")

                continue

            elif command in [
                "north", "south", "east", "west"
            ]:

                self.move(command)

                continue

            elif command.startswith("equip "):

                self.equip_item(
                    action[6:].strip()
                )

                continue

            elif command.startswith("use "):

                self.use_item(
                    action[4:].strip()
                )

                continue

            elif command.startswith("take "):

                self.take_item(
                    action[5:].strip()
                )

                continue

            if self.current_enemy:

                print(
                    "\nAn enemy is attacking! "
                    "Use 'attack' to fight."
                )

                continue

            self.ai_action(action)

        print(
            "\nThanks for playing AI Dungeon Master!"
        )
