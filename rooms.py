rooms = {

    "entrance": {
        "name": "Dungeon Entrance",
        "description": "You stand before an ancient dungeon. A dark corridor stretches north.",
        "north": "hall",
        "enemy": None,
        "items": [],
        "gold": 0
    },

    "hall": {
        "name": "Ancient Hall",
        "description": "A long hall stretches ahead. A goblin guards the passage.",
        "south": "entrance",
        "east": "treasure",
        "west": "library",
        "enemy": "goblin",
        "items": [],
        "gold": 0
    },

    "treasure": {
        "name": "Treasure Room",
        "description": "An abandoned treasure chamber filled with ancient artifacts.",
        "west": "hall",
        "enemy": None,
        "items": ["Sword", "Potion"],
        "gold": 50
    },

    "library": {
        "name": "Forgotten Library",
        "description": "Dust-covered bookshelves surround you. A skeleton warrior guards an ancient manuscript.",
        "east": "hall",
        "north": "crypt",
        "enemy": "skeleton",
        "items": [],
        "gold": 20
    },

    "crypt": {
        "name": "Haunted Crypt",
        "description": "Cold mist covers the stone floor. A terrifying Wraith emerges from the darkness.",
        "south": "library",
        "east": "armory",
        "enemy": "wraith",
        "items": ["Greater Potion"],
        "gold": 30
    },

    "armory": {
        "name": "Ancient Armory",
        "description": "An abandoned armory containing legendary weapons and a mysterious artifact.",
        "west": "crypt",
        "north": "boss_room",
        "enemy": None,
        "items": ["Longsword", "Shadow Blade", "Ancient Artifact"],
        "gold": 75
    },

    "boss_room": {
        "name": "Dragon's Chamber",
        "description": "A gigantic dragon guards the final chamber and its ancient treasures.",
        "south": "armory",
        "enemy": "dragon",
        "items": [],
        "gold": 0
    }
}