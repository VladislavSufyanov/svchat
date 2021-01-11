from typing import Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB_NUMBER: int = 0

    @validator('REDIS_PORT', pre=False)
    def validate_redis_port(cls, v: int) -> int:
        if v < 1 or v > 65535:
            raise ValueError('Bad REDIS_PORT')
        return v

    class Config:
        case_sensitive = True
        env_file = '.env'
