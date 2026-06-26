from core.context import Context
from core.message.history import get_message_history


def build_system_prompt():
    system_config = Context.system_config
    character_config = Context.character_config

    tool_prompts = system_config["tool_prompts"]

    character_name = character_config["character_name"]

    persona_prompt = character_config.get(
        "persona_prompt",
        ""
    )

    if persona_prompt:
        persona_prompt = persona_prompt.format(
            character_name=character_name
        )

    vrm_expression_prompt = tool_prompts.get(
        "vrm_expression_prompt",
        ""
    )

    tool_guidance_prompt = tool_prompts.get(
        "tool_guidance_prompt",
        ""
    )

    parts = []

    if persona_prompt:
        parts.append(persona_prompt)

    if vrm_expression_prompt:
        parts.append(vrm_expression_prompt)

    if tool_guidance_prompt:
        parts.append(tool_guidance_prompt)

    return "\n\n".join(parts)


def build_messages(user_message: str):
    system_prompt = build_system_prompt()

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(
        get_message_history()
    )

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    return messages