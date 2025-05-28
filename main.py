from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserLocation(BaseModel):
    latitude: float
    longitude: float

@app.post("/get_location/")
async def get_location(user_location: UserLocation):
    return {"latitude": user_location.latitude, "longitude": user_location.longitude} 