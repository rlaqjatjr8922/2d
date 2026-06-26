from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.context import Context
from core.logger import progress
from core.logger import error
from core.message_pipeline import message_pipeline
from core.message.history import (
    get_message_history,
    clear_message_history
)


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


class Packet(BaseModel):
    message: str


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "main.html")


@app.get("/camera")
def camera_page():
    return FileResponse(STATIC_DIR / "camera.html")


@app.get("/screen")
def screen_page():
    return FileResponse(STATIC_DIR / "screen.html")


@app.get("/browser")
def browser_page():
    return FileResponse(STATIC_DIR / "browser.html")


@app.get("/config")
def config():
    return {
        "system_config": Context.system_config,
        "character_config": Context.character_config,
        "agent_config": Context.agent_config,
        "ollama_llm": Context.ollama_llm
    }


@app.get("/status")
def status():
    return {
        "type": "server_status",
        "conf_version": Context.system_config["conf_version"],
        "server": {
            "host": Context.system_config["host"],
            "port": Context.system_config["port"]
        },
        "character": Context.character_config,
        "agent": Context.agent_config,
        "ollama_llm": {
            "base_url": Context.ollama_llm["base_url"],
            "model": Context.ollama_llm["model"]
        }
    }


@app.post("/chat")
async def chat(packet: Packet):
    if not packet.message.strip():
        return {
            "type": "error",
            "message": "message 값이 없음",
            "last": True
        }

    try:
        progress(
            f"사용자 메시지 수신: {packet.message}"
        )

        ai_message = await message_pipeline(
            packet.message
        )

        return {
            "type": "ai_message",
            "message": ai_message,
            "last": True,
            "conf_version": Context.system_config["conf_version"],
            "character": Context.character_config,
            "agent": Context.agent_config,
            "ollama_llm": {
                "model": Context.ollama_llm["model"]
            }
        }

    except Exception as e:
        error(
            f"채팅 처리 실패: {e}"
        )

        return {
            "type": "error",
            "message": f"서버 오류: {e}",
            "last": True
        }


@app.get("/history")
def history():
    return {
        "type": "message_history",
        "history": get_message_history()
    }


@app.post("/history/clear")
def history_clear():
    clear_message_history()

    return {
        "type": "message_history_clear",
        "success": True
    }


def start_ai_server():
    host = Context.system_config["host"]
    port = Context.system_config["port"]

    progress(f"설정 버전: {Context.system_config['conf_version']}")
    progress(f"캐릭터 이름: {Context.character_config['character_name']}")
    progress(f"VRM 모델: {Context.character_config['vrm_model_name']}")
    progress(f"아바타: {Context.character_config['avatar']}")
    progress(f"Ollama 모델: {Context.ollama_llm['model']}")
    progress(f"Ollama 주소: {Context.ollama_llm['base_url']}")

    progress(f"웹서버 여는 중: http://{host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False
    )