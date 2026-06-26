from core.context import Context
from core.ai_server import start_ai_server
from core.logger import progress
from core.logger import error


progress("Mane 시작")

try:
    progress("Context 설정 불러오는 중")
    Context.load()
    progress("Context 설정 불러오기 완료")

except Exception as e:
    error(f"Context 설정 불러오기 실패 : {e}")
    raise


try:
    progress("AI 웹서버 시작")
    start_ai_server()

except Exception as e:
    error(f"AI 웹서버 시작 실패 : {e}")
    raise