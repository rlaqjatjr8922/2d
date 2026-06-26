from core.message.prompt import build_messages
from core.message.llm import ask_llm
from core.message.history import add_message


async def message_pipeline(message: str):
    messages = build_messages(message)

    ai_message = await ask_llm(messages)

    add_message(
        "user",
        message
    )

    add_message(
        "assistant",
        ai_message
    )

    return ai_message