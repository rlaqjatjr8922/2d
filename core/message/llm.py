import json
import httpx

from core.context import Context
from core.logger import progress
from core.message.tools import get_tool_schemas


def _print_ai_request(url, payload):
    progress("========== AI에게 실제 보내는 값 시작 ==========")
    progress(f"요청 URL: {url}")

    progress(
        "요청 Payload:\n"
        + json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        )
    )

    progress("========== AI에게 실제 보내는 값 끝 ==========")


def _clean_messages(messages: list):
    """
    /v1/chat/completions에 보낼 message 정리
    role, content만 사용
    """
    cleaned = []

    for message in messages:
        cleaned.append(
            {
                "role": message.get("role"),
                "content": message.get("content", "")
            }
        )

    return cleaned


def _extract_content(data: dict):
    """
    /v1/chat/completions 응답에서 답변 내용 추출
    """
    return data["choices"][0]["message"].get(
        "content",
        ""
    )


def _get_ollama_config():
    """
    Context 구조가 4개 묶음이면 Context.ollama_llm 사용
    예전 구조면 Context.ollama_config 사용
    """
    if hasattr(Context, "ollama_llm"):
        return Context.ollama_llm

    return Context.ollama_config


def _get_llm_provider():
    """
    현재 선택된 LLM 제공자 확인
    """
    agent_config = Context.agent_config
    agent_name = agent_config.get(
        "conversation_agent_choice",
        "basic_memory_agent"
    )

    agent = agent_config.get(
        agent_name,
        {}
    )

    return agent.get(
        "llm_provider",
        ""
    )


def _build_payload(messages: list):
    llm = _get_ollama_config()

    payload = {
        "model": llm["model"],
        "messages": _clean_messages(messages)
    }

    # 3. 같은 단어 반복 억제
    if "frequency_penalty" in llm:
        payload["frequency_penalty"] = llm["frequency_penalty"]

    # 4. 같은 주제 반복 억제
    if "presence_penalty" in llm:
        payload["presence_penalty"] = llm["presence_penalty"]

    # 5. 응답 형식
    # null이면 보내지 않음
    if llm.get("response_format") is not None:
        response_format = llm["response_format"]

        if response_format == "json_object":
            payload["response_format"] = {
                "type": "json_object"
            }
        else:
            payload["response_format"] = response_format

    # 6. 랜덤 시드
    if "seed" in llm:
        payload["seed"] = llm["seed"]

    # 7. stop
    if llm.get("stop"):
        payload["stop"] = llm["stop"]

    # 8. stream
    payload["stream"] = llm.get(
        "stream",
        False
    )

    # 9. stream_options
    # stream true일 때만 보냄
    if payload["stream"] and llm.get("stream_options"):
        payload["stream_options"] = llm["stream_options"]

    # 10. temperature
    if "temperature" in llm:
        payload["temperature"] = llm["temperature"]

    # 11. top_p
    if "top_p" in llm:
        payload["top_p"] = llm["top_p"]

    # 12. max_tokens
    if "max_tokens" in llm:
        payload["max_tokens"] = llm["max_tokens"]

    # 13. tools
    enabled_tools = llm.get(
        "tools",
        []
    )

    tool_schemas = get_tool_schemas(
        enabled_tools
    )

    if tool_schemas:
        payload["tools"] = tool_schemas

        # 16. tool_choice
        if llm.get("tool_choice"):
            payload["tool_choice"] = llm["tool_choice"]

    # 14. reasoning_effort
    if llm.get("reasoning_effort"):
        payload["reasoning_effort"] = llm["reasoning_effort"]

    # 15. reasoning
    if llm.get("reasoning"):
        payload["reasoning"] = llm["reasoning"]

    # 17. logit_bias
    # 빈 dict면 보내지 않음
    if llm.get("logit_bias"):
        payload["logit_bias"] = llm["logit_bias"]

    # 18. user
    if llm.get("user"):
        payload["user"] = llm["user"]

    # 19. n
    if "n" in llm:
        payload["n"] = llm["n"]

    return payload


async def ask_llm(messages: list):
    llm_provider = _get_llm_provider()

    if llm_provider != "ollama_llm":
        raise ValueError(
            f"현재 지원하는 LLM은 ollama_llm 뿐임: {llm_provider}"
        )

    llm = _get_ollama_config()
    url = llm["base_url"]

    payload = _build_payload(
        messages
    )

    _print_ai_request(
        url,
        payload
    )

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            url,
            json=payload
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        progress(
            "AI 오류 응답:\n"
            + e.response.text
        )
        raise
    
    data = response.json()

    progress(
        "AI 원본 응답:\n"
        + json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )
    )

    return _extract_content(data)