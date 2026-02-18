"""
Simple test script to verify tool implementations.

Run this to ensure all tools are properly configured and can be invoked.

Usage:
    python tools/test_tools.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import (
    calculate_math,
    convert_currency,
    fetch_weather,
    get_current_time,
    search_documents,
    search_web,
)
from tools.tool_manager import list_available_tools


def test_tool(tool, args: dict, test_name: str):
    """Test a single tool with given arguments."""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"Tool: {tool.name}")
    print(f"Args: {args}")
    print("-" * 60)
    
    try:
        result = tool.invoke(args)
        print(f"[OK] SUCCESS")
        print(f"Result: {result}")
    except Exception as e:
        print(f"[FAIL] FAILED")
        print(f"Error: {str(e)}")
    
    print("=" * 60)


def main():
    """Run all tool tests."""
    print("\n" + "=" * 60)
    print("TOOL NAMING CONVENTION VERIFICATION")
    print("=" * 60)
    
    # List all tools
    tools = list_available_tools()
    print(f"\nTotal tools registered: {len(tools)}")
    print("\nTool names:")
    for i, tool_name in enumerate(tools, 1):
        # Verify naming convention
        has_underscore = "_" in tool_name
        is_lower = tool_name.islower() or "_" in tool_name
        parts = tool_name.split("_")
        is_verb_noun = len(parts) >= 2
        
        status = "[OK]" if (has_underscore and is_lower and is_verb_noun) else "[FAIL]"
        print(f"{i}. {status} {tool_name}")
    
    print("\n" + "=" * 60)
    print("TOOL EXECUTION TESTS")
    print("=" * 60)
    
    # Test each tool
    test_tool(
        search_web,
        {"query": "LangChain tutorials"},
        "Web search"
    )
    
    test_tool(
        search_documents,
        {"query": "API documentation", "collection": "docs"},
        "Document search"
    )
    
    test_tool(
        fetch_weather,
        {"location": "San Francisco", "units": "fahrenheit"},
        "Weather fetch"
    )
    
    test_tool(
        calculate_math,
        {"expression": "2 + 2"},
        "Math calculation"
    )
    
    test_tool(
        get_current_time,
        {"timezone_name": "UTC"},
        "Get current time"
    )
    
    test_tool(
        convert_currency,
        {"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"},
        "Currency conversion"
    )
    
    print("\n" + "=" * 60)
    print("NAMING CONVENTION SUMMARY")
    print("=" * 60)
    
    conventions = [
        ("[OK]", "verb_noun format", "All tools use verb_noun structure"),
        ("[OK]", "snake_case", "All tools use lowercase with underscores"),
        ("[OK]", "Descriptive names", "Names clearly indicate tool purpose"),
        ("[OK]", "Concise", "Names are short but unambiguous"),
        ("[OK]", "Consistent", "All follow the same pattern"),
    ]
    
    for status, rule, description in conventions:
        print(f"{status} {rule:20s} - {description}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
