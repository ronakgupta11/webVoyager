from celery import Celery
from utils.langgraph_runner import run_agent_task

app = Celery("web_voyager", broker="redis://localhost:6379/0")
app.config_from_object("celeryconfig")

@app.task
def execute_web_task(task: str):
    result = run_agent_task(task)
    return result  # or store result in Redis, etc.
