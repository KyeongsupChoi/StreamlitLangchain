# Tool Naming Conventions

This document outlines the tool naming conventions used in this project, following LangChain best practices.

## Core Principles

### 1. Use verb_noun Format ✓

Tools should be named with a verb followed by a noun, describing the action and target.

**Good Examples:**
```python
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    pass

@tool
def fetch_weather(location: str) -> str:
    """Fetch current weather for a location."""
    pass

@tool
def calculate_math(expression: str) -> str:
    """Calculate mathematical expressions."""
    pass

@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email message."""
    pass

@tool
def get_current_time(timezone: str = "UTC") -> str:
    """Get the current date and time."""
    pass
```

**Bad Examples:**
```python
# ❌ Too generic
@tool
def tool1():
    pass

# ❌ Not verb_noun format
@tool
def weather():
    pass

# ❌ Ambiguous
@tool
def helper():
    pass

# ❌ Uses camelCase instead of snake_case
@tool
def searchWeb():
    pass
```

### 2. Be Specific and Descriptive

Tool names should clearly indicate what they do without being overly verbose.

**Good Examples:**
- `search_web` - Clear what it searches
- `search_documents` - Distinct from web search
- `fetch_weather` - Specific data retrieval action
- `convert_currency` - Clear transformation
- `send_email` - Obvious action

**Bad Examples:**
- `search` - Too vague (search what?)
- `get_data` - Not specific enough
- `do_thing` - Meaningless
- `query` - Ambiguous action

### 3. Use snake_case Consistently

All tool names must use snake_case to align with Python and LangChain conventions.

**Correct:**
```python
search_web
fetch_weather
calculate_math
get_current_time
convert_currency
send_email
update_database
delete_record
```

**Incorrect:**
```python
searchWeb       # camelCase
SearchWeb       # PascalCase
search-web      # kebab-case
SEARCH_WEB      # SCREAMING_SNAKE_CASE
```

### 4. Keep Names Concise but Unambiguous

Tool names appear in the model's prompt, so keep them short while maintaining clarity.

**Good Balance:**
```python
search_web           # 10 chars, clear
fetch_weather        # 13 chars, specific
calculate_math       # 14 chars, obvious
get_current_time     # 16 chars, descriptive
```

**Too Verbose:**
```python
search_the_web_for_information_using_search_engine  # Too long
retrieve_current_meteorological_conditions          # Unnecessarily complex
```

**Too Terse:**
```python
srch    # Not clear
wx      # Requires domain knowledge
calc    # Ambiguous
time    # Could be many things
```

## Naming by Category

### Search Tools
- `search_web` - Web search
- `search_documents` - Internal document search
- `search_database` - Database queries
- `find_files` - File system search

### Data Retrieval Tools
- `fetch_weather` - Weather data
- `get_current_time` - Date/time info
- `retrieve_stock_price` - Financial data
- `fetch_user_profile` - User information

### Calculation Tools
- `calculate_math` - Mathematical operations
- `compute_statistics` - Statistical analysis
- `convert_currency` - Currency conversion
- `convert_units` - Unit conversions

### Communication Tools
- `send_email` - Email sending
- `send_message` - Messaging
- `post_notification` - Push notifications
- `create_ticket` - Support ticket creation

### Data Modification Tools
- `update_database` - Database updates
- `create_record` - Record creation
- `delete_entry` - Data deletion
- `modify_settings` - Configuration changes

## Documentation Requirements

Every tool must have:

1. **Clear docstring** explaining what it does
2. **Usage context** (when to use this tool)
3. **Parameter descriptions** with types
4. **Return value description**
5. **Error conditions** if applicable

**Example:**
```python
@tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for information using a search engine.
    
    Use this tool when the user asks for current information, recent events,
    or data that requires internet access.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        A formatted string with search results
        
    Raises:
        ValueError: If query is empty
        APIError: If the search API is unavailable
    """
    pass
```

## Checklist for New Tools

Before adding a new tool, verify:

- [ ] Name follows verb_noun format
- [ ] Name is specific and descriptive
- [ ] Name uses snake_case
- [ ] Name is concise but unambiguous
- [ ] Docstring explains the tool's purpose
- [ ] Usage context is documented (when to use it)
- [ ] All parameters have type hints and descriptions
- [ ] Return type is documented
- [ ] Error conditions are noted

## Tools in This Project

Current tools following these conventions:

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `search_web` | Search | Search the web for information |
| `search_documents` | Search | Search internal document collections |
| `fetch_weather` | Data Retrieval | Get current weather for a location |
| `calculate_math` | Calculation | Evaluate mathematical expressions |
| `get_current_time` | Data Retrieval | Get current date and time |
| `convert_currency` | Calculation | Convert between currencies |

## References

- [LangChain Tools Documentation](https://docs.langchain.com/tools)
- [PEP 8 - Python Naming Conventions](https://peps.python.org/pep-0008/#function-and-variable-names)
- Project checklist: `langchain_docs/Project_Checklist.md`
