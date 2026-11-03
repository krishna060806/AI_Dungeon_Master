player_name = ""

inventory = ["Torch"]


def show_inventory():
    print("\n=== INVENTORY ===")

    if not inventory:
        print("Your inventory is empty.")
        return

    for index, item in enumerate(inventory, start=1):
        print(f"{index}. {item}")


def add_item(item):
    if item and item not in inventory:
        inventory.append(item)
        return True

    return False


def remove_item(item):
    if item in inventory:
        inventory.remove(item)
        return True

    return False