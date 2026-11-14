import asyncio
import logging
import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn
import openai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("service")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    default_config = {
        "provider": "openrouter",
        "api_key": "",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "google/gemini-2.0-flash-001",
        "system_prompt": "You are a helpful, always-on AI assistant."
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return {**default_config, **json.load(f)}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    return default_config

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

class ModelSettings(BaseModel):
    provider: str
    api_key: str = ""
    base_url: str = ""
    model: str
    system_prompt: str = ""

class ChatRequest(BaseModel):
    prompt: str

async def background_loop():
    logger.info("Background loop active.")
    try:
        while True:
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        pass

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
    return HTMLResponse("<h1>Model Service is Live</h1>")

@app.get("/health")
async def health():
    return {"status": "ok", "live": True}

@app.get("/api/settings")
async def get_settings():
    cfg = load_config()
    safe_cfg = dict(cfg)
    if safe_cfg.get("api_key"):
        key = safe_cfg["api_key"]
        safe_cfg["has_api_key"] = True
        safe_cfg["api_key_masked"] = key[:4] + "..." + key[-4:] if len(key) > 8 else "***"
        safe_cfg["api_key"] = ""
    else:
        safe_cfg["has_api_key"] = False
        safe_cfg["api_key_masked"] = ""
    return safe_cfg

@app.post("/api/settings")
async def update_settings(settings: ModelSettings):
    current = load_config()
    updated = {
        "provider": settings.provider,
        "base_url": settings.base_url.strip(),
        "model": settings.model.strip(),
        "system_prompt": settings.system_prompt.strip()
    }
    if settings.api_key.strip():
        updated["api_key"] = settings.api_key.strip()
    else:
        updated["api_key"] = current.get("api_key", "")
    save_config(updated)
    return {"status": "saved", "model": updated["model"], "provider": updated["provider"]}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    cfg = load_config()
    prompt = req.prompt.strip()
    api_key = cfg.get("api_key") or os.environ.get("MODEL_API_KEY", "")

    if not api_key:
        return {
            "response": f"⚠️ No API Key configured for provider '{cfg.get('provider')}'. Click '⚙️ Model Settings' in the top right to enter your API key."
        }

    provider = cfg.get("provider", "openai")
    base_url = cfg.get("base_url") or None
    model_name = cfg.get("model", "gpt-4o-mini")

    try:
        # Standard OpenAI client supports OpenAI, OpenRouter, Groq, Mistral, Together, Ollama, etc.
        client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
        messages = []
        if cfg.get("system_prompt"):
            messages.append({"role": "system", "content": cfg["system_prompt"]})
        messages.append({"role": "user", "content": prompt})

        completion = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            timeout=45.0
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        logger.exception("Inference error")
        return {"response": f"Inference Error ({provider}): {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
