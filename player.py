
class Player:

    def __init__(self, name="Unknown Hero"):

        self.name = name

        self.level = 1
        self.xp = 0
        self.xp_to_next = 100

        self.health = 100
        self.max_health = 100

        self.gold = 0
        self.attack = 10

        self.inventory = ["Torch"]
        self.weapon = None

    def show_stats(self):

        print("\n=== PLAYER STATUS ===")

        print(f"Name: {self.name}")
        print(f"Level: {self.level}")
        print(f"XP: {self.xp}/{self.xp_to_next}")

        print(
            f"Health: {self.health}/{self.max_health}"
        )

        print(f"Gold: {self.gold}")
        print(f"Base Attack: {self.attack}")
        print(f"Weapon: {self.weapon or 'None'}")

    def add_item(self, item):

        if item and item not in self.inventory:

            self.inventory.append(item)
            return True

        return False

    def remove_item(self, item):

        if item in self.inventory:

            self.inventory.remove(item)

            if self.weapon == item:
                self.weapon = None

            return True

        return False

    def heal(self, amount):

        old_health = self.health

        self.health = min(
            self.max_health,
            self.health + amount
        )

        return self.health - old_health

    def take_damage(self, amount):

        self.health = max(
            0,
            self.health - amount
        )

    def get_attack(self, items):

        damage = self.attack

        if self.weapon:

            weapon_data = items.get(
                self.weapon.lower(), {}
            )

            damage += weapon_data.get(
                "damage", 0
            )

        return damage

    def gain_xp(self, amount):

        self.xp += amount

        print(f"\n[+{amount} XP]")

        while self.xp >= self.xp_to_next:

            self.xp -= self.xp_to_next

            self.level += 1

            self.xp_to_next += 50

            self.max_health += 20
            self.attack += 5

            self.health = self.max_health

            print("\n==========================")
            print("       LEVEL UP!")
            print("==========================")

            print(f"You reached Level {self.level}!")
            print("+20 Maximum Health")
            print("+5 Base Attack")
            print("Health fully restored!")

    def to_dict(self):

        return {
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next": self.xp_to_next,
            "health": self.health,
            "max_health": self.max_health,
            "gold": self.gold,
            "attack": self.attack,
            "inventory": self.inventory,
            "weapon": self.weapon
        }

    @classmethod
    def from_dict(cls, data):

        player = cls(
            data.get("name", "Unknown Hero")
        )

        player.level = data.get("level", 1)
        player.xp = data.get("xp", 0)

        player.xp_to_next = data.get(
            "xp_to_next", 100
        )

        player.max_health = data.get(
            "max_health", 100
        )

        player.health = max(
            0,
            min(
                data.get("health", 100),
                player.max_health
            )
        )

        player.gold = data.get("gold", 0)
        player.attack = data.get("attack", 10)

        player.inventory = data.get(
            "inventory", ["Torch"]
        )

        player.weapon = data.get("weapon")

        return player
