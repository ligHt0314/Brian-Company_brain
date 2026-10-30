from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    app_env: str = "development"
    demo_mode: bool = True
    session_secret: str = "local-synthetic-demo-only-change-for-deployment"
    operator_reset_token: str = ""
    falkordb_host: str = "127.0.0.1"
    falkordb_port: int = 6389
    falkordb_password: str | None = None
    falkordb_graph: str = "company_brain_digiplus_services"
    sqlite_path: str = str(ROOT / ".data/digiplus.sqlite")
    upload_dir: str = str(ROOT / ".data/originals")
    log_path: str = str(ROOT / ".data/logs/application.jsonl")
    llm_request_timeout_ms: int = 10000
    llm_provider: str = "openai-compatible"
    llm_model: str = ""
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    demo_clock_iso: str = "2026-10-17T04:30:00Z"
    allowed_origin: str = "http://localhost:3000"
    graph_query_timeout_ms: int = 1500
    run_timeout_ms: int = 25000


settings = Settings()
