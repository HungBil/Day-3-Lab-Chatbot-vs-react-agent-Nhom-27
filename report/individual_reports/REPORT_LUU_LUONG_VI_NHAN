# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Luu Luong Vi Nhan
- **Student ID**: 2A202600120
- **Date**: 6/4/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implemented**: 
  - `src/tools/travel_tools.py` — Core 6 travel planning tools with mock data
  - `src/tools/tool_registry.py` — Tool registry and dynamic execution engine
  - `src/tools/__init__.py` — Module exports

- **Code Highlights**: 
  - Designed 6 functions: `search_destination()`, `get_weather()`, `get_hotel_price()`, `estimate_food_cost()`, `search_attraction()`, `check_budget()`
  - Created mock datasets: `DESTINATIONS`, `WEATHER_DATA`, `HOTEL_PRICES`, `FOOD_COSTS`, `ATTRACTIONS` with realistic Vietnam travel data
  - Implemented `execute_tool(tool_name, args_str)` with robust argument parsing supporting JSON lists, tuples, and comma-separated formats
  - Added `get_tool_descriptions()` to auto-generate tool descriptions for LLM system prompt
  - Implemented `_normalize_city()` helper for case-insensitive lookups
  - All tools return string outputs compatible with agent's Observation field

- **Documentation**: Each tool has docstring specifying input/output format. Tools are registered in `TOOL_REGISTRY` with name, description, function reference, and expected args. The agent imports `get_tool_descriptions()` and `execute_tool()` to make tools available without hardcoding.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: 
  Agent failed to parse `Action` when LLM output malformed arguments:
  ```
  Action: get_hotel_price("Da Nang", "4-star", "3")
  ```
  The regex expected the star_level to be a simple string like `"4"`, but the LLM added `-star` suffix, causing `_parse_args()` to fail with "Invalid argument count: expected 3 args, got 2."

- **Log Source**: Similar patterns observed in `logs/AGENT_STEP` events. Tool call failed silently or returned error, breaking the Observation chain.

- **Diagnosis**: 
  Root cause: Tool description was ambiguous — it said `star_level` but didn't specify format constraints. The LLM had no examples showing exact string format (`"3"` vs `"3-star"`). This is a **tool specification issue**, not a bug in the tool itself.

- **Solution**: 
  Updated tool description in `tool_registry.py`:
  ```
  "get_hotel_price(city, star_level, nights): 
   Estimate hotel cost. star_level must be '3', '4', or '5' (string, no suffix).
   Returns nightly price and total for given nights."
  ```
  Added concrete example in system prompt showing exact format. After this change, agent correctly called `get_hotel_price("Da Nang", "4", "3")`.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: The `Thought` block acts as explicit step-by-step reasoning that the LLM commits to before taking action. Example:
   - **Chatbot**: "User wants a 3-day trip to Da Nang for 5M VND. 3-star hotel costs 500k/night = 1.5M, food 300k/day = 900k, attractions 500k. Total 2.9M — enough budget. Here's a plan: Day 1..." (All in one pass, no backtracking)
   - **Agent (ReAct)**: "Thought: I need destination info. → Action: search_destination. → Thought: Now check weather. → Action: get_weather. → ..." (Separates reasoning from execution)
   
   The separate `Thought` phase helps the agent explicitly reason about *what tool to call next*, instead of the LLM trying to generate both reasoning AND tool names in one messy output.

2.  **Reliability**: Agent performed *worse* in simple one-turn questions:
   - **Query**: "What's the weather in Sapa in December?"
   - **Chatbot**: "December in Sapa is cold (5-15°C), dry..." (1 turn, instant)
   - **Agent**: Called `search_destination("Sapa")` → `get_weather("Sapa", "12")` → final answer (3 steps, more latency)
   
   The overhead of the ReAct loop is unjustified for factual lookups the Chatbot can handle directly. ReAct shines only when *multi-step reasoning* is needed (e.g., "Plan a trip with total budget breakdown").

3.  **Observation**: Observations were critical feedback loops. When agent received observation like "3-star hotel: 500k/night × 3 = 1.5M VND", it could then reason: "Remaining budget: 5M - 1.5M = 3.5M for food/attractions." Without observations, the agent would hallucinate numbers. This closed-loop aspect is why ReAct beats Chatbot for *multi-step planning*.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: 
  - **Tool Distribution**: Currently all 6 tools are hardcoded. For 100+ tools, use semantic search (embeddings) to retrieve only relevant tools per query, reducing LLM context size.
  - **Async Execution**: Replace sequential tool calls with async/await — allow agent to batch multiple independent tool calls per step (e.g., `get_weather()` and `search_attraction()` in parallel).
  - **Tool Versioning**: Implement tool registry versioning so retired/updated tools can coexist without breaking existing agent traces.

- **Safety**: 
  - **Input Validation**: Add schema validation (pydantic) before tool execution — reject calls with invalid city names, negative budgets, etc.
  - **Cost Guard**: Implement hard limits on total agent steps and LLM token spend per request to prevent runaway costs.
  - **Supervisor LLM**: Add a second LLM that reviews the agent's final answer before returning to user (e.g., "Does this budget breakdown make sense?")
  - **Audit Trail**: Store all Thought/Action/Observation traces in a queryable database for debugging and compliance.

- **Performance**: 
  - **Caching**: Cache tool results by (tool_name, args) hash — if user asks same query twice, reuse results without re-calling LLM.
  - **Vector DB for Attractions**: Replace hardcoded `ATTRACTIONS` dict with vector DB (e.g., Weaviate) so we can semantic-search "I like hiking" → [list of adventure attractions] dynamically.
  - **Prompt Optimization**: Use prompt compression techniques to reduce token count while maintaining tool descriptions.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
