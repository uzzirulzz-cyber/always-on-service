import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("service")

# Background worker task to execute persistent automation / polling
async def background_loop():
    logger.info("Background loop initialized and active.")
    try:
        while True:
            # Place recurring jobs / polling logic here
            logger.info("Heartbeat: Service is healthy and active 24/7.")
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        logger.info("Background loop shutting down gracefully.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: spawn background tasks
    task = asyncio.create_task(background_loop())
    yield
    # Shutdown: clean up background tasks
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

app = FastAPI(title="Always-On 24/7 Cloud Service", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok", "live": True}

@app.get("/")
async def root():
    return {"message": "Service is live and operating 24/7."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
