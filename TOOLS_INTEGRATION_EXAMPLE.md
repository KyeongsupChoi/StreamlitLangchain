# Tools Integration Example

This guide shows how to integrate the tool calling functionality into your Streamlit app.

## Quick Start

### 1. Basic Tool Binding

```python
from llm.groq_chat_model import build_groq_chat_model
from tools.tool_manager import bind_tools_to_model
from config.env import load_groq_settings

# Build base model
settings = load_groq_settings()
base_model = build_groq_chat_model(settings)

# Bind tools to the model
model_with_tools = bind_tools_to_model(base_model)
```

### 2. Use in Chat Response

```python
from chat.respond_with_tools import generate_reply_with_tools

# Generate response with tool calling support
response = generate_reply_with_tools(
    history=chat_history,
    model=model_with_tools,
    max_iterations=5
)
```

### 3. Complete Streamlit Integration

Here's how to modify `streamlit_app.py` to support tool calling:

```python
import streamlit as st
from config.env import load_groq_settings
from llm.groq_chat_model import build_groq_chat_model
from tools.tool_manager import bind_tools_to_model, list_available_tools
from chat.respond_with_tools import generate_reply_with_tools
from chat.history import add_turn, create_history
from app.main import render_chat_ui
from observability.logging_config import setup_logging

setup_logging()

st.title("LangChain Chat with Tools")

# Sidebar - Tool Configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Enable/disable tools
    enable_tools = st.checkbox("Enable Tool Calling", value=True)
    
    if enable_tools:
        st.subheader("Available Tools")
        available_tools = list_available_tools()
        st.write(f"📋 {len(available_tools)} tools loaded:")
        for tool_name in available_tools:
            st.text(f"  • {tool_name}")
        
        max_iterations = st.slider(
            "Max Tool Iterations",
            min_value=1,
            max_value=10,
            value=5,
            help="Maximum number of tool calling iterations"
        )

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = create_history(system_prompt="You are a helpful assistant.")

# Initialize model
settings = load_groq_settings()
base_model = build_groq_chat_model(settings)

# Conditionally bind tools
if enable_tools:
    model = bind_tools_to_model(base_model)
    st.sidebar.success("✓ Tools enabled")
else:
    model = base_model
    st.sidebar.info("Tools disabled")

# Render chat UI
render_chat_ui(st.session_state.history)

# Handle user input
if prompt := st.chat_input("Message"):
    # Add user message
    st.session_state.history = add_turn(
        st.session_state.history,
        role="user",
        content=prompt
    )
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if enable_tools:
                    # Use tool-enabled response generation
                    response = generate_reply_with_tools(
                        history=st.session_state.history,
                        model=model,
                        max_iterations=max_iterations
                    )
                else:
                    # Use standard response generation
                    from chat.respond import generate_reply
                    response = generate_reply(
                        history=st.session_state.history,
                        model=model
                    )
                
                st.write(response)
                
                # Add assistant message to history
                st.session_state.history = add_turn(
                    st.session_state.history,
                    role="assistant",
                    content=response
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
```

## Customizing Tools

### Add a New Tool

1. Create the tool in the appropriate category file (or create a new one):

```python
# tools/custom_tools.py
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

@tool
def fetch_stock_price(symbol: str) -> str:
    """
    Fetch current stock price for a given symbol.
    
    Use this tool when the user asks about stock prices or market data.
    
    Args:
        symbol: Stock ticker symbol (e.g., "AAPL", "GOOGL", "MSFT")
        
    Returns:
        Current stock price information
    """
    logger.info("Tool called: fetch_stock_price for symbol='%s'", symbol)
    
    # Your implementation here
    return f"Stock price for {symbol}: $150.25 (placeholder)"
```

2. Register it in `tools/__init__.py`:

```python
from tools.custom_tools import fetch_stock_price

__all__ = [
    # ... existing tools
    "fetch_stock_price",
]
```

3. Add it to `tool_manager.py`:

```python
from tools import fetch_stock_price

AVAILABLE_TOOLS: list[BaseTool] = [
    # ... existing tools
    fetch_stock_price,
]
```

### Selective Tool Binding

You can selectively bind only certain tools:

```python
from tools import search_web, fetch_weather, calculate_math
from tools.tool_manager import bind_tools_to_model

# Only bind specific tools
model_with_limited_tools = bind_tools_to_model(
    model,
    tools=[search_web, fetch_weather, calculate_math]
)
```

### Force Tool Usage

Force the model to use a specific tool:

```python
# Model MUST use a tool
model = bind_tools_to_model(
    base_model,
    tool_choice="any"
)

# Model MUST use a specific tool
model = bind_tools_to_model(
    base_model,
    tool_choice="search_web"
)
```

### Disable Parallel Tool Calls

```python
model = bind_tools_to_model(
    base_model,
    parallel_tool_calls=False
)
```

## Testing Tools

### Test Individual Tool

```python
from tools import search_web

# Test the tool directly
result = search_web.invoke({"query": "LangChain tutorials"})
print(result)
```

### Test with Model

```python
from langchain_core.messages import HumanMessage

response = model_with_tools.invoke([
    HumanMessage(content="What's the weather in San Francisco?")
])

print("Tool calls:", response.tool_calls)
```

## Best Practices

1. **Tool Naming**: Follow verb_noun format (see `TOOL_NAMING_GUIDE.md`)
2. **Error Handling**: Always handle errors gracefully in tool implementations
3. **Logging**: Log tool executions for debugging and monitoring
4. **Documentation**: Provide clear docstrings explaining when to use each tool
5. **Iteration Limits**: Set appropriate `max_iterations` to prevent infinite loops
6. **Validation**: Validate tool inputs before execution

## Troubleshooting

### Tool Not Being Called

- Check tool description is clear and matches user intent
- Verify tool is registered in `AVAILABLE_TOOLS`
- Ensure model supports tool calling (Groq models do)

### Tool Execution Errors

- Check logs in `logs/app.log` for detailed error messages
- Verify tool arguments match the expected schema
- Test tool directly before using with model

### Too Many Iterations

- Reduce `max_iterations` if needed
- Improve tool descriptions to help model reach conclusions faster
- Consider if the task requires tool calling at all

## Example Conversations

### With Tools Enabled

**User**: What's the weather in Tokyo?

**Assistant** (internal tool call): `fetch_weather(location="Tokyo")`

**Tool Result**: Weather in Tokyo: Sunny, 22°C, humidity 65%, wind 10 km/h

**Assistant**: The weather in Tokyo is currently sunny with a temperature of 22°C. The humidity is at 65% with winds of 10 km/h. It's a pleasant day!

---

**User**: Calculate 15% tip on a $85 bill

**Assistant** (internal tool call): `calculate_math(expression="85 * 0.15")`

**Tool Result**: Result: 12.75

**Assistant**: A 15% tip on an $85 bill would be $12.75. The total would be $97.75.

## Next Steps

- Implement real API integrations for tools (weather API, search API, etc.)
- Add streaming support for tool calls
- Create tool usage analytics and monitoring
- Add tool call visualization in the UI
- Implement tool result caching for performance
