story = []


def add_event(text):
    story.append(str(text))


def get_story():
    return "\n".join(story[-6:])


def get_all_story():
    return story.copy()


def set_story(new_story):
    global story

    if isinstance(new_story, list):
        story = new_story.copy()
    else:
        story = []


def clear_story():
    global story
    story = []