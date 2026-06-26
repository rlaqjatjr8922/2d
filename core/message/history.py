message_history = []


def add_message(role: str, name: str, content: str):
    message_history.append(
        {
            "role": role,
            "name": name,
            "content": content
        }
    )


def get_message_history():
    return message_history.copy()


def clear_message_history():
    message_history.clear()