from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://drkm:drkm@db:5432/drkm"
    redis_url: str = "redis://redis:6379/0"
    ollama_url: str = "http://ollama:11434"
    llm_model: str = "llama3.2:3b"
    embedding_model: str = "nomic-embed-text"
    drkm_api_key: str = "change-this-api-key"
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    admin_username: str = "admin"
    admin_email: str = "admin@example.com"
    admin_password: str = ""
    storage_path: str = "/data/documents"
    max_upload_mb: int = 100
    cors_origins: str = "http://localhost:3000"
    public_base_url: str = "http://localhost:3000"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True

settings = Settings()
