# agent/graph.py
from agent.state import AgentState
from agent.logic import mark_page, format_descriptions, parse, update_scratchpad,annotate
from agent.tools import click, type_text, scroll, wait, go_back, to_google

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START


prompt = hub.pull("wfh/web-voyager")
print(prompt.input_variables)
llm = ChatOpenAI(model="gpt-4o", max_tokens=4096)

agent = annotate | RunnablePassthrough.assign(
    prediction=format_descriptions | prompt | llm | StrOutputParser() | parse
)

graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent)
graph_builder.set_entry_point("agent")

graph_builder.add_node("update_scratchpad", update_scratchpad)
graph_builder.add_edge("update_scratchpad", "agent")

tools = {
    "Click": click,
    "Type": type_text,
    "Scroll": scroll,
    "Wait": wait,
    "GoBack": go_back,
    "Google": to_google,
}

for name, fn in tools.items():
    graph_builder.add_node(name, RunnableLambda(fn) | (lambda obs: {"observation": obs}))
    graph_builder.add_edge(name, "update_scratchpad")

def select_tool(state: AgentState):
    action = state["prediction"]["action"]
    if action == "ANSWER":
        return END
    if action == "retry":
        return "agent"
    return action

graph_builder.add_conditional_edges("agent", select_tool)
graph = graph_builder.compile()


from IPython import display
from playwright.async_api import async_playwright
async def call_agent(question: str, page, max_steps: int = 150):
    event_stream = graph.astream(
        {
            "page": page,
            "input": question,
            "scratchpad": [],
        },
        {
            "recursion_limit": max_steps,
        },
    )
    final_answer = None
    steps = []
    async for event in event_stream:
        # We'll display an event stream here
        if "agent" not in event:
            continue
        pred = event["agent"].get("prediction") or {}
        action = pred.get("action")
        action_input = pred.get("args")
        display.clear_output(wait=False)
        steps.append(f"{len(steps) + 1}. {action}: {action_input}")
        print("\n".join(steps))
        display.display(display.Image(base64.b64decode(event["agent"]["img"])))
        if "ANSWER" in action:
            final_answer = action_input[0]
            break
    return final_answer


async def run_agent(task: str):
    browser = await async_playwright().start()
# We will set headless=False so we can watch the agent navigate the web.
    browser = await browser.chromium.launch(headless=False, args=None)
    page = await browser.new_page()
    _ = await page.goto("https://www.google.com")
    res = await call_agent("Could you explain the WebVoyager paper (on arxiv)?", page)
    print(f"Final response: {res}")


