from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Pydantic models
class UserLocation(BaseModel):
    latitude: float
    longitude: float

@app.post("/get_location/")
async def get_location(user_location: UserLocation):
    # This endpoint just receives location data and returns it
    return {"latitude": user_location.latitude, "longitude": user_location.longitude}