import asyncio
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from woninet.server.routes import devices, stats
from woninet.main import get_monitor
from woninet.__init__ import __version__

# Global variables
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR = Path(__file__).parent / "templates"

monitor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global monitor

    # Startup
    monitor = get_monitor()
    monitor.start()

    # Assign the instance of Server
    server = app.state.uvicorn_server

    async def watch():
        """
        Periodic monitor watchdog. Triggers server shutdown when the monitor
        is no longer alive.
        """
        while True:
            await asyncio.sleep(1)
            if not monitor.is_alive():
                server.should_exit = True
                return

    task = asyncio.create_task(watch())

    try:
        yield
    finally:
        # Shutdown
        task.cancel()
        monitor.stop()


app = FastAPI(
    title="woninet",
    description="Network Monitoring Dashboard",
    lifespan=lifespan,
    version=__version__,
    docs_url=None,
    redoc_url=None,
)

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Routes
app.include_router(devices.router)
app.include_router(stats.router)


# The root path
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")
