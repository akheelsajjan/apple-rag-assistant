from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from app.graph import build_graph
import uuid

graph = build_graph()
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# Test 1 — irrelevant
print("=== IRRELEVANT ===")
config1 = {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}
result1 = app.invoke({"question": "what's the weather today"}, config=config1)
print(result1["answer"])

# Test 2 — ambiguous, then resolved via clarification
print("\n=== AMBIGUOUS -> CLARIFY -> RESOLVE ===")
config2 = {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}
result2 = app.invoke({"question": "what is the yield"}, config=config2)
print("Interrupted:", result2.get("__interrupt__"))

result2b = app.invoke(Command(resume="fruit"), config=config2)
print("Resolved domain:", result2b.get("domain"))
print("Answer:", result2b.get("answer"))

# Test 3 — web search fallback
print("\n=== WEB SEARCH FALLBACK ===")
config3 = {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}
result3 = app.invoke({"question": "what is Apple's current stock price today"}, config=config3)
print("web_search_needed:", result3.get("web_search_needed"))
print("Answer:", result3.get("answer"))