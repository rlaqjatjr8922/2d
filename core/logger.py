from pathlib import Path
from datetime import datetime
import inspect


# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 로그 폴더
LOG_DIR = BASE_DIR / "logs"

# 로그 파일
LOG_FILE = LOG_DIR / "latest.log"


def _write(level: str, message: str):
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    caller_file = Path(
        inspect.stack()[2].filename
    ).name

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = (
        f"[{now}] "
        f"[{level}] "
        f"[{caller_file}] "
        f"{message}"
    )

    print(line)

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:
        f.write(
            line + "\n"
        )


def progress(message: str):
    _write(
        "진행상황",
        message
    )


def error(message: str):
    _write(
        "오류",
        message
    )