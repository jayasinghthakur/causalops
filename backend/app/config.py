"""Fail-closed configuration for the local-only foundation."""

from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    app_env: Literal["local", "test"] = "local"
    graph_host: Literal["127.0.0.1", "localhost", "falkordb", "falkordb-test"] = "127.0.0.1"
    graph_port: int = Field(default=6379, ge=1, le=65535)
    graph_name: str = Field(default="causalops_local", pattern=r"^causalops_[a-z0-9_]{1,64}$")
    graph_timeout_ms: int = Field(default=2000, ge=100, le=5000)

    @model_validator(mode="after")
    def isolate_environments(self) -> Self:
        if self.app_env == "test":
            if not self.graph_name.startswith("causalops_test_"):
                raise ValueError("Tests require a unique causalops_test_ graph")
            if self.graph_host == "falkordb-test":
                if self.graph_port != 6379:
                    raise ValueError("Container test database must use port 6379")
            elif self.graph_host not in {"localhost", "127.0.0.1"} or self.graph_port != 6380:
                raise ValueError("Host tests must use the isolated localhost:6380 database")
        elif self.graph_name != "causalops_local" or self.graph_host == "falkordb-test":
            raise ValueError("Local mode is restricted to causalops_local")
        return self

    def require_mutation_target(self) -> None:
        # Keep this guard at every write entry point, including teardown.
        Settings.model_validate(self.model_dump())
