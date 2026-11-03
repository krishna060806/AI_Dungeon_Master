import re


def detect_item(text):

    if not text:
        return None

    pattern = r"^\s*ITEM\s*:\s*(.+?)\s*$"

    match = re.search(
        pattern,
        text,
        re.IGNORECASE | re.MULTILINE
    )

    if match:
        item = match.group(1).strip()

        if item:
            return item

    return None