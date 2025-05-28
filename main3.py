# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from core import generate_map_and_send_sms

app = FastAPI()

# Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmergencyRequest(BaseModel):
    latitude: float
    longitude: float
    emergency_type: str

@app.post("/trigger_emergency/")
async def trigger_emergency(data: EmergencyRequest):
    lat = data.latitude
    lon = data.longitude
    emergency = data.emergency_type

    html_path = generate_map_and_send_sms((lat, lon), emergency)
    return {"status": "success", "map_path": html_path}
