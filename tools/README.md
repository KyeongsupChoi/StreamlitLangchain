# Tools Module

This module implements LangChain tool calling with proper naming conventions following the project checklist.

## Quick Start

```python
# Import tools
from tools import search_web, fetch_weather, calculate_math

# Use with a model
from tools.tool_manager import bind_tools_to_model
model_with_tools = bind_tools_to_model(base_model)

# Generate response with tools
from chat.respond_with_tools import generate_reply_with_tools
response = generate_reply_with_tools(
    history=chat_history,
    model=model_with_tools
)
```

## Available Tools

All tools follow the **verb_noun** naming convention:

| Tool Name | Description | Example Usage |
|-----------|-------------|---------------|
| `search_web` | Search the web for information | User asks about current events |
| `search_documents` | Search internal documents | User asks about documentation |
| `fetch_weather` | Get weather for a location | User asks "What's the weather?" |
| `calculate_math` | Evaluate math expressions | User asks "Calculate 15% of 85" |
| `get_current_time` | Get current date/time | User asks "What time is it?" |
| `convert_currency` | Convert between currencies | User asks "Convert 100 USD to EUR" |

## Naming Conventions

All tools in this module follow these rules:

✓ **verb_noun format** - e.g., `search_web`, `fetch_weather`  
✓ **snake_case** - lowercase with underscores  
✓ **Descriptive** - clear purpose without being verbose  
✓ **Consistent** - all follow the same pattern

See `TOOL_NAMING_GUIDE.md` for complete documentation.

## File Structure

```
tools/
├── __init__.py              # Public exports
├── README.md                # This file
├── TOOL_NAMING_GUIDE.md     # Naming conventions guide
├── tool_manager.py          # Tool binding & registry
├── search_tools.py          # Search-related tools
├── data_tools.py            # Data retrieval & calculation
├── utility_tools.py         # Time & conversion utilities
└── test_tools.py            # Verification tests
```

## Testing

Run the test suite to verify all tools:

```bash
python tools/test_tools.py
```

Expected output:
```
============================================================
TOOL NAMING CONVENTION VERIFICATION
============================================================

Total tools registered: 6

Tool names:
1. [OK] search_web
2. [OK] search_documents
3. [OK] fetch_weather
4. [OK] calculate_math
5. [OK] get_current_time
6. [OK] convert_currency

...

All tests completed!
```

## Adding New Tools

1. Create the tool in an appropriate file (or create new category file):

```python
# tools/your_category.py
from langchain_core.tools import tool

@tool
def verb_noun(parameter: str) -> str:
    """
    Clear description of what this tool does.
    
    Use this when the user asks about [specific scenarios].
    
    Args:
        parameter: Description of parameter
        
    Returns:
        Description of return value
    """
    # Implementation
    return result
```

2. Export from `__init__.py`:

```python
from tools.your_category import verb_noun

__all__ = [
    # ... existing tools
    "verb_noun",
]
```

3. Register in `tool_manager.py`:

```python
from tools import verb_noun

AVAILABLE_TOOLS: list[BaseTool] = [
    # ... existing tools
    verb_noun,
]
```

4. Test the tool:

```bash
python tools/test_tools.py
```

## Documentation

- **TOOL_NAMING_GUIDE.md** - Comprehensive naming conventions
- **TOOLS_INTEGRATION_EXAMPLE.md** (in project root) - Integration guide
- **IMPLEMENTATION_SUMMARY.md** (in project root) - What was built

## Implementation Status

✅ 6 tools implemented with proper naming  
✅ Tool manager for binding and configuration  
✅ ReAct loop implementation for tool execution  
✅ Comprehensive documentation  
✅ Test suite for verification  
✅ Ready for Streamlit integration

See `IMPLEMENTATION_SUMMARY.md` for complete details.
