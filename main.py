# # main.py
# from fastapi import FastAPI
# from agent.graph import graph, run_agent
# from playwright.async_api import async_playwright
# from agent.state import AgentState
# import asyncio
# app = FastAPI()
# import json
# from fastapi.responses import StreamingResponse
# from playwright.sync_api import sync_playwright
# # @app.on_event("startup")
# # async def startup():
# #     global browser, context
# #     pw = await async_playwright().start()
# #     # browser = await pw.chromium.launch(headless=False)
# #     browser = await pw.firefox.connect(f"wss://production-sfo.browserless.io/firefox/playwright?token=S5rLVbFVGssQnv6056e18a116cef9d4e942d2e8ec7")
# #     context = await browser.new_context()



# # @app.on_event("shutdown")
# # async def shutdown():
# #     try:
# #         await browser.close()
# #     except Exception as e:
# #         print(f"Error during browser shutdown: {e}")


# @app.post("/run-agent")
# async def run_agent(task: str):

#     page = await context.new_page()
#     # await page.goto("https://www.google.com", wait_until="domcontentloaded")
#     await page.goto("https://www.bing.com", wait_until="domcontentloaded")

#     async def event_stream():
#         state: AgentState = {
#             "page": page,  # make sure page is available
#             "input": task,
#             "img": "",
#             "bboxes": [],
#             "prediction": {"action": "", "args": []},
#             "scratchpad": [],
#             "observation": "",
          
#         }

#         async for step in graph.astream(state, {"recursion_limit": 50}):
#             # Send every step where agent made a decision
#             if "agent" in step:
#                 data = step["agent"]
#                 payload = {
#                     "action": data.get("prediction", {}).get("action"),
#                     "args": data.get("prediction", {}).get("args"),
#                     "screenshot": data.get("img"),  # base64 image
#                 }
#                 print(f"Sending event: {payload['action'], payload['args']}")
#                 yield f"data: {json.dumps(payload)}\n\n"
#                 await asyncio.sleep(0.1)

#     return StreamingResponse(event_stream(), media_type="text/event-stream")
    # stream = graph.astream({
    #     "page": page,
    #     "input": task,
    #     "scratchpad": []
    # }, {
    #     "recursion_limit": 150
    # })

    # screenshots = []
    # actions = []

    # async for step in stream:
    #     if "agent" in step:
    #         pred = step["agent"].get("prediction") or {}
    #         actions.append(pred)
    #         screenshots.append(step["agent"]["img"])
    #     if "observation" in step and "ANSWER" in step.get("agent", {}).get("prediction", {}).get("action", ""):
    #         break

    # return {
    #     "actions": actions,
    #     "screenshots": screenshots
    # }
# run_agent("what are the latest blogs on langchain?").__await__()



from fastapi import FastAPI
from tasks import execute_web_task
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/run-agent")
async def submit_task(task: str):
    task_result = execute_web_task.delay(task)
    return JSONResponse({"status": "queued", "task_id": task_result.id})

@app.get("/task-status/{task_id}")
async def get_status(task_id: str):
    from tasks import app as celery_app
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
