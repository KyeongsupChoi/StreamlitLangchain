"""
Tool manager for binding and managing LangChain tools.

Project role:
  Central place to configure which tools are available to the model
  and how they should be bound.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from tools import (
    calculate_math,
    convert_currency,
    fetch_weather,
    get_current_time,
    search_documents,
    search_web,
)

logger = logging.getLogger(__name__)


# Tool registry - easily enable/disable tools by commenting out
AVAILABLE_TOOLS: list[BaseTool] = [
    search_web,
    search_documents,
    fetch_weather,
    calculate_math,
    get_current_time,
    convert_currency,
]


def bind_tools_to_model(
    model: BaseChatModel,
    tools: list[BaseTool] | None = None,
    tool_choice: str | None = None,
    parallel_tool_calls: bool = True,
) -> BaseChatModel:
    """
    Bind tools to a chat model for tool calling capability.
    
    Args:
        model: The base chat model to bind tools to
        tools: List of tools to bind. If None, uses AVAILABLE_TOOLS
        tool_choice: Optional tool selection strategy:
            - None: Model decides whether to use tools
            - "any": Model must use at least one tool
            - "tool_name": Model must use the specified tool
        parallel_tool_calls: Whether to allow parallel tool calling (default: True)
        
    Returns:
        The model with tools bound
        
    Example:
        >>> from llm.groq_chat_model import build_groq_chat_model
        >>> model = build_groq_chat_model(settings)
        >>> model_with_tools = bind_tools_to_model(model)
    """
    if tools is None:
        tools = AVAILABLE_TOOLS
        
    logger.info(
        "Binding %d tools to model: %s",
        len(tools),
        [t.name for t in tools]
    )
    
    bind_kwargs: dict[str, Any] = {}
    if tool_choice is not None:
        bind_kwargs["tool_choice"] = tool_choice
    if not parallel_tool_calls:
        bind_kwargs["parallel_tool_calls"] = False
        
    return model.bind_tools(tools, **bind_kwargs)


def get_tool_by_name(name: str) -> BaseTool | None:
    """
    Retrieve a tool by its name.
    
    Args:
        name: The tool name (e.g., "search_web", "fetch_weather")
        
    Returns:
        The tool if found, None otherwise
    """
    for tool in AVAILABLE_TOOLS:
        if tool.name == name:
            return tool
    return None


def list_available_tools() -> list[str]:
    """
    Get a list of all available tool names.
    
    Returns:
        List of tool names
    """
    return [tool.name for tool in AVAILABLE_TOOLS]
