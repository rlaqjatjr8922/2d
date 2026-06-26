from pathlib import Path
import yaml


class Context:
    # conf.yaml 전체
    config = {}

    # =====================
    # 4개 묶음 설정
    # =====================
    system_config = {}
    character_config = {}
    agent_config = {}
    ollama_llm = {}

    @classmethod
    def load(cls):
        base_dir = Path(__file__).resolve().parent.parent
        config_path = base_dir / "conf.yaml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"conf.yaml 파일이 없음: {config_path}"
            )

        with open(config_path, "r", encoding="utf-8") as f:
            cls.config = yaml.safe_load(f)

        if cls.config is None:
            raise ValueError("conf.yaml 내용이 비어있음")

        # =====================
        # 1. system_config
        # =====================
        cls.system_config = cls.config["system_config"]

        # =====================
        # 2. character_config
        # =====================
        cls.character_config = cls.config["character_config"]

        # =====================
        # 3. agent_config
        # =====================
        cls.agent_config = cls.config["agent_config"]

        # =====================
        # 4. ollama_llm
        # =====================
        cls.ollama_llm = cls.config["llm_configs"]["ollama_llm"]