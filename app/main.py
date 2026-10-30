
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime, timezone
from uuid import uuid4
import json
from pathlib import Path

app = FastAPI(
    title="Smart Community Security Guard",
    description=(
        "A community safety platform with incident reporting "
        "and future English and Nigerian Pidgin voice support."
    ),
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

class IncidentReport(BaseModel):
    description: str = Field(min_length=5, max_length=2000)
    language: Literal["English", "Nigerian Pidgin"] = "English"
    category: Literal[
        "fire", "medical", "security", "accident", "other"
    ] = "other"
    location: str = Field(min_length=2, max_length=200)
    urgency: Literal["low", "medium", "high", "critical"] = "medium"

import json
from pathlib import Path

INCIDENTS_FILE = Path("incidents.json")


def load_incidents():
    if INCIDENTS_FILE.exists():
        with INCIDENTS_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_incidents():
    with INCIDENTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(incidents, file, indent=4)


incidents = load_incidents()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/incidents", status_code=201)
def create_incident(report: IncidentReport):
    incident = {
        "id": str(uuid4()),
        **report.model_dump(),
        "status": "reported",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    incidents.append(incident)
    save_incidents()

    return {
        "message": "Incident report received",
        "incident": incident,
    }


@app.get("/incidents")
def list_incidents():
    return {"count": len(incidents), "incidents": incidents}
