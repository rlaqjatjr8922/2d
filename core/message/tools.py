import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEMORY_DIR = BASE_DIR / "memory"
MEMORY_FILE = MEMORY_DIR / "memory.json"


# =====================
# 기억 파일 처리
# =====================

def _ensure_memory_file():
    MEMORY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text(
            "[]",
            encoding="utf-8"
        )


def _read_memories():
    _ensure_memory_file()

    try:
        return json.loads(
            MEMORY_FILE.read_text(
                encoding="utf-8"
            )
        )

    except Exception:
        return []


def _write_memories(memories):
    _ensure_memory_file()

    MEMORY_FILE.write_text(
        json.dumps(
            memories,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


# =====================
# 실제 도구 함수
# =====================

def save_memory(content: str):
    memories = _read_memories()

    memory = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": content
    }

    memories.append(memory)

    _write_memories(memories)

    return {
        "success": True,
        "message": "기억 저장 완료",
        "saved": memory
    }


def load_memory(query: str = ""):
    memories = _read_memories()

    if not query:
        return {
            "success": True,
            "message": "전체 기억 불러오기 완료",
            "memories": memories
        }

    result = []

    for memory in memories:
        content = memory.get(
            "content",
            ""
        )

        if query in content:
            result.append(memory)

    return {
        "success": True,
        "message": "기억 검색 완료",
        "query": query,
        "memories": result
    }


# =====================
# 가능한 모든 도구 스키마
# =====================

ALL_TOOL_SCHEMAS = {
    "save_memory": {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "중요한 내용을 장기 기억으로 저장한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "저장할 기억 내용"
                    }
                },
                "required": [
                    "content"
                ]
            }
        }
    },

    "load_memory": {
        "type": "function",
        "function": {
            "name": "load_memory",
            "description": "저장된 장기 기억을 불러온다. query가 비어 있으면 전체 기억을 불러온다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 기억 키워드. 전체 기억을 불러오려면 빈 문자열"
                    }
                },
                "required": []
            }
        }
    }
}


# =====================
# 도구 이름 → 실행 함수 매핑
# =====================

TOOL_RUNNERS = {
    "save_memory": save_memory,
    "load_memory": load_memory
}


# =====================
# conf.yaml tools 목록 기준으로 반환
# =====================

def get_tool_schemas(enabled_tools: list):
    schemas = []

    for tool_name in enabled_tools:
        if tool_name in ALL_TOOL_SCHEMAS:
            schemas.append(
                ALL_TOOL_SCHEMAS[tool_name]
            )

    return schemas


def run_tool(tool_name: str, arguments: dict):
    if arguments is None:
        arguments = {}

    if tool_name not in TOOL_RUNNERS:
        return {
            "success": False,
            "error": f"없는 도구: {tool_name}"
        }

    tool_func = TOOL_RUNNERS[tool_name]

    return tool_func(
        **arguments
    )