"""
Generate assistant responses using LangChain chat models with tool calling support.

Project role:
  Enhanced response generation that supports tool execution loops.
  Handles tool calls, executes them, and feeds results back to the model.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool

from chat.history import ChatTurn

logger = logging.getLogger(__name__)


def _to_langchain_messages(history: list[ChatTurn]) -> list[BaseMessage]:
    """Convert chat history to LangChain messages."""
    messages: list[BaseMessage] = []
    for turn in history:
        role = turn["role"]
        content = turn["content"]
        if role == "system":
            messages.append(SystemMessage(content=content))
        elif role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        else:
            logger.warning("Unknown role in history: %s", role)
    return messages


def generate_reply_with_tools(
    *,
    history: list[ChatTurn],
    model,
    max_iterations: int = 5
) -> str:
    """
    Generate an assistant reply with tool calling support.
    
    This function implements the ReAct loop:
    1. Model generates response (possibly with tool calls)
    2. If tool calls present, execute them
    3. Return tool results to model
    4. Repeat until model produces final answer or max_iterations reached
    
    Args:
        history: Chat turns including system prompt and prior turns
        model: A LangChain chat model with tools bound via bind_tools()
        max_iterations: Maximum number of tool calling iterations (default: 5)
        
    Returns:
        Final assistant message content
        
    Raises:
        RuntimeError: If model returns empty response or exceeds max iterations
    """
    messages = _to_langchain_messages(history)
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        logger.info("Tool calling iteration %d/%d", iteration, max_iterations)
        
        # Invoke model
        response: AIMessage = model.invoke(messages)
        messages.append(response)
        
        # Check if model made tool calls
        tool_calls = getattr(response, "tool_calls", [])
        
        if not tool_calls:
            # No tool calls - this is the final answer
            content = getattr(response, "content", None)
            if content is None or (isinstance(content, str) and not content.strip()):
                raise RuntimeError("Model returned an empty response.")
            logger.info("Final response generated after %d iterations", iteration)
            return str(content)
        
        # Execute tool calls
        logger.info("Executing %d tool call(s)", len(tool_calls))
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            logger.info("Executing tool: %s with args: %s", tool_name, tool_args)
            
            try:
                # Get the tool from the model's bound tools
                tool = _find_tool_by_name(model, tool_name)
                if tool is None:
                    error_msg = f"Tool '{tool_name}' not found in bound tools"
                    logger.error(error_msg)
                    tool_result = ToolMessage(
                        content=f"Error: {error_msg}",
                        tool_call_id=tool_id
                    )
                else:
                    # Execute the tool
                    result = tool.invoke(tool_args)
                    tool_result = ToolMessage(
                        content=str(result),
                        tool_call_id=tool_id
                    )
                    logger.info("Tool '%s' executed successfully", tool_name)
                    
            except Exception as e:
                error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                logger.error(error_msg, exc_info=True)
                tool_result = ToolMessage(
                    content=f"Error: {error_msg}",
                    tool_call_id=tool_id
                )
            
            messages.append(tool_result)
    
    # Max iterations reached
    raise RuntimeError(
        f"Maximum tool calling iterations ({max_iterations}) reached without final answer"
    )


def _find_tool_by_name(model: Any, tool_name: str) -> BaseTool | None:
    """
    Find a tool in the model's bound tools by name.
    
    Args:
        model: The chat model with bound tools
        tool_name: Name of the tool to find
        
    Returns:
        The tool if found, None otherwise
    """
    # Access bound tools from the model
    # This works with LangChain's bind_tools() mechanism
    if hasattr(model, "bound_tools"):
        for tool in model.bound_tools:
            if tool.name == tool_name:
                return tool
    
    # Try alternate attribute names
    if hasattr(model, "tools"):
        for tool in model.tools:
            if tool.name == tool_name:
                return tool
    
    logger.warning("Could not find tool '%s' in model's bound tools", tool_name)
    return None
