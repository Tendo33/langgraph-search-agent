"""Configuration module for the agent.

Defines the Configuration class for managing agent settings such as model names and loop counts.
"""

import os
from typing import Any, Dict, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default="gemini-2.5-flash",
        description="The name of the language model to use for the agent's query generation.",
    )

    reflection_model: str = Field(
        default="gemini-2.5-flash",
        description="The name of the language model to use for the agent's reflection.",
    )

    answer_model: str = Field(
        default="gemini-2.5-pro",
        description="The name of the language model to use for the agent's answer.",
    )

    number_of_initial_queries: int = Field(
        default=3,
        description="The number of initial search queries to generate.",
    )

    max_research_loops: int = Field(
        default=2,
        description="The maximum number of research loops to perform.",
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig.

        Args:
            config: Optional RunnableConfig containing configuration values

        Returns:
            Configuration: A new Configuration instance with values from config
        """
        configurable: Dict[str, Any] = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: Dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values: Dict[str, Any] = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
