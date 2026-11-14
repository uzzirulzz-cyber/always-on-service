import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("service")

class ChatRequest(BaseModel):
    prompt: str

async def background_loop():
    logger.info("Background loop initialized and active.")
    try:
        while True:
            logger.info("Heartbeat: Service is healthy and active 24/7.")
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        logger.info("Background loop shutting down gracefully.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(background_loop())
    yield
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

app = FastAPI(title="Always-On 24/7 Cloud Service", lifespan=lifespan)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return HTMLResponse("<h1>24/7 Model Service is Live</h1>")

@app.get("/health")
async def health():
    return {"status": "ok", "live": True}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_query = req.prompt.strip()
    logger.info(f"Received user prompt: {user_query}")
    response_text = f"Processed your request: '{user_query}'. Service is active and operating 24/7."
    return {"status": "success", "response": response_text}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
