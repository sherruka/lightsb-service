from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/pages/{page_name}", response_class=HTMLResponse)
async def get_page(page_name: str):
    page_path = Path(f"app/pages/{page_name}.html")
    if page_path.exists():
        return HTMLResponse(content=page_path.read_text(), status_code=200)
    return HTMLResponse(content="Page not found", status_code=404)
