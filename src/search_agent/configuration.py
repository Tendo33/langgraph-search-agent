"""Configuration module for the LangGraph research agent."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """Runtime configuration for the research workflow."""

    query_generator_model: str = Field(
        default="gemini-2.5-flash",
        description="Model used for generating search queries.",
    )
    reflection_model: str = Field(
        default="gemini-2.5-flash",
        description="Model used for reflection and gap analysis.",
    )
    answer_model: str = Field(
        default="gemini-2.5-pro",
        description="Model used for final answer synthesis.",
    )
    number_of_initial_queries: int = Field(
        default=3,
        description="Initial number of search queries to generate.",
    )
    max_research_loops: int = Field(
        default=2,
        description="Maximum research loop count.",
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create configuration using request config > env > defaults priority."""
        configurable: Dict[str, Any] = (
            config.get("configurable", {}) if config else {}
        )

        values: Dict[str, Any] = {}
        for name in cls.model_fields.keys():
            if name in configurable and configurable[name] is not None:
                values[name] = configurable[name]
                continue

            env_value = os.getenv(name.upper())
            if env_value is not None:
                values[name] = env_value

        return cls(**values)

    def to_configurable(self) -> Dict[str, Any]:
        """Convert to runnable configurable dict."""
        return self.model_dump()
