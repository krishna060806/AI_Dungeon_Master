import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"


def generate_story(player_action, story_history):

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY missing from .env file."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",

                "content": """
You are an immersive fantasy dungeon master.

Your responsibilities:

1. Continue the adventure based on player actions.
2. Describe locations, enemies and discoveries.
3. Never make decisions on behalf of the player.
4. Give players meaningful choices.
5. Keep responses under 100 words.
6. Maintain consistency with previous events.
7. Make the adventure engaging and unpredictable.

ITEM DETECTION RULE:

Whenever the player successfully obtains an item,
include a separate line in this exact format:

ITEM: Item Name

Only generate this line when the player actually obtains
an item. Do not generate it for items merely mentioned.
"""
            },

            {
                "role": "user",

                "content": f"""
STORY SO FAR:

{story_history}

PLAYER ACTION:

{player_action}

Continue the adventure.
"""
            }
        ]
    )

    result = response.choices[0].message.content

    return result or "The dungeon falls silent. Try another action."