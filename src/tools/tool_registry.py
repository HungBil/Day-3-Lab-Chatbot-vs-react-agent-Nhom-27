"""
Tool Registry: Central registry that maps tool names to their functions and descriptions.
The ReAct agent uses this registry to discover and execute tools.

API for Person 1 (Agent Core):
    - TOOL_REGISTRY: list of tool dicts
    - get_tool_descriptions() -> str: formatted string for system prompt
    - execute_tool(tool_name, args_str) -> str: run a tool by name with string args
"""
import json
import re
from src.tools.travel_tools import (
    search_destination, get_weather, get_hotel_price,
    estimate_food_cost, search_attraction, check_budget,
)


TOOL_REGISTRY = [
    {
        "name": "search_destination",
        "description": (
            "Search for basic information about a travel destination in Vietnam. "
            "Input: a single string — the city name (e.g. 'Đà Nẵng'). "
            "Returns: region, description, local specialties, best travel season."
        ),
        "function": search_destination,
        "args": ["city"],
    },
    {
        "name": "get_weather",
        "description": (
            "Get weather information for a city in a specific month. "
            "Input: two arguments — city (string, e.g. 'Đà Nẵng') and month (string 1-12, e.g. '6'). "
            "Returns: temperature, weather condition, and travel advice."
        ),
        "function": get_weather,
        "args": ["city", "month"],
    },
    {
        "name": "get_hotel_price",
        "description": (
            "Get estimated hotel price and suggestions. "
            "Input: three arguments — city (string), star_level (string: '3', '4', or '5'), nights (string, number of nights). "
            "Returns: price per night, total cost, and hotel name suggestions."
        ),
        "function": get_hotel_price,
        "args": ["city", "star_level", "nights"],
    },
    {
        "name": "estimate_food_cost",
        "description": (
            "Estimate daily and total food cost for a trip. "
            "Input: three arguments — city (string), days (string), budget_level (string: 'low', 'mid', or 'high'). "
            "low = street food; mid = local restaurants; high = upscale dining. "
            "Returns: cost per day and total food budget."
        ),
        "function": estimate_food_cost,
        "args": ["city", "days", "budget_level"],
    },
    {
        "name": "search_attraction",
        "description": (
            "Search for tourist attractions by city and interest. "
            "Input: two arguments — city (string) and interest (string: 'beach', 'culture', 'adventure', or 'food'). "
            "Returns: list of top attractions with entry fees and descriptions."
        ),
        "function": search_attraction,
        "args": ["city", "interest"],
    },
    {
        "name": "check_budget",
        "description": (
            "Compare total estimated cost against the user's budget. "
            "Input: two arguments — total_cost (string, VND number e.g. '3800000') and budget (string, VND number e.g. '5000000'). "
            "Returns: whether the trip is within budget, with recommendations."
        ),
        "function": check_budget,
        "args": ["total_cost", "budget"],
    },
]


def get_tool_descriptions() -> str:
    """
    Return formatted tool descriptions for the agent's system prompt.
    Person 1 calls this in get_system_prompt().
    """
    lines = []
    for tool in TOOL_REGISTRY:
        lines.append(f"- {tool['name']}: {tool['description']}")
    return "\n".join(lines)


def execute_tool(tool_name: str, args_str: str) -> str:
    """
    Execute a tool by name with the given raw arguments string.
    Supports multiple argument formats that LLMs commonly produce:
      1. JSON object: {"city": "Đà Nẵng", "month": "6"}
      2. JSON array: ["Đà Nẵng", "6"]
      3. Comma-separated: Đà Nẵng, 6
      4. Single string: Đà Nẵng

    Person 1 calls this in the ReAct loop after parsing Action.

    Args:
        tool_name: Name of the tool to execute.
        args_str: Raw argument string from LLM output.

    Returns:
        Tool result as string, or error message if tool not found / args invalid.
    """
    for tool in TOOL_REGISTRY:
        if tool["name"] == tool_name:
            func = tool["function"]
            expected_args = tool["args"]
            return _call_with_parsed_args(func, expected_args, args_str)

    available = ", ".join(t["name"] for t in TOOL_REGISTRY)
    return f"Lỗi: Tool '{tool_name}' không tồn tại. Các tool có sẵn: {available}."


def _call_with_parsed_args(func, expected_args: list, args_str: str) -> str:
    """
    Parse args_str into the correct arguments and call func.
    Handles JSON, comma-separated, and single-value formats.
    """
    args_str = args_str.strip()

    # --- Strategy 1: Try JSON object ---
    try:
        parsed = json.loads(args_str)
        if isinstance(parsed, dict):
            call_args = [str(parsed.get(a, "")) for a in expected_args]
            return func(*call_args)
        elif isinstance(parsed, list):
            call_args = [str(a) for a in parsed]
            return _safe_call(func, expected_args, call_args)
        elif isinstance(parsed, (str, int, float)):
            return func(str(parsed))
    except (json.JSONDecodeError, TypeError):
        pass

    # --- Strategy 2: Comma-separated ---
    # Clean surrounding brackets/parens/quotes
    cleaned = args_str
    cleaned = re.sub(r'^[\[\(\{"\']|[\]\)\}"\']$', '', cleaned).strip()

    parts = _smart_split(cleaned)

    if len(parts) == 0:
        # Fallback: use entire string as single arg
        return func(cleaned) if len(expected_args) == 1 else func(args_str)

    return _safe_call(func, expected_args, parts)


def _smart_split(text: str) -> list:
    """
    Split arguments by comma, but handle quoted strings properly.
    e.g. '"Đà Nẵng", "6"' -> ['Đà Nẵng', '6']
    """
    parts = []
    current = ""
    in_quotes = False
    quote_char = None

    for char in text:
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
        elif char == "," and not in_quotes:
            parts.append(current.strip().strip('"').strip("'"))
            current = ""
            continue
        else:
            current += char

    if current.strip():
        parts.append(current.strip().strip('"').strip("'"))

    return [p for p in parts if p]  # Remove empty strings


def _safe_call(func, expected_args: list, provided: list) -> str:
    """
    Call func with provided args, padding with defaults if needed.
    """
    # Trim to expected count
    call_args = provided[:len(expected_args)]

    # Pad with empty strings if too few
    while len(call_args) < len(expected_args):
        call_args.append("")

    try:
        return func(*call_args)
    except TypeError as e:
        return f"Lỗi khi gọi tool: {e}. Expected {len(expected_args)} args: {expected_args}, got: {provided}"
