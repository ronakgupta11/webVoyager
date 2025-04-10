import asyncio
from agent.graph import graph
from agent.state import AgentState
from utils.browser import get_browser_context

def run_agent_task(task: str):
    return asyncio.run(_run(task))

async def _run(task: str):
    page, browser, context = await get_browser_context()

    try:
        await page.goto("https://www.bing.com", wait_until="domcontentloaded")

        state: AgentState = {
            "page": page,
            "input": task,
            "img": "",
            "bboxes": [],
            "prediction": {"action": "", "args": []},
            "scratchpad": [],
            "observation": "",
        }

        screenshots = []
        actions = []

        async for step in graph.astream(state, {"recursion_limit": 50}):
            if "agent" in step:
                agent_data = step["agent"]
                prediction = agent_data.get("prediction", {})
                actions.append(prediction)
                screenshots.append(agent_data.get("img"))

                if prediction.get("action") == "ANSWER":
                    break

        return {
            "actions": actions,
            "screenshots": screenshots
        }

    finally:
        # Ensure browser and context are closed even if something fails
        await context.close()
        await browser.close()
