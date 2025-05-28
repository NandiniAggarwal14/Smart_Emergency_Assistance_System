from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Tuple
import requests
import heapq
from twilio.rest import Client

app = FastAPI()

class EmergencyRequest(BaseModel):
    latitude: float
    longitude: float
    emergency_type: str

help_stations_with_phone = [
    {"coordinates": (30.2837296, 77.997745), "phone_number": "+919389969916"},
    {"coordinates": (30.304785, 78.0209032), "phone_number": "+919389969916"},
    {"coordinates": (30.2909374, 78.0498482), "phone_number": "+919389969916"},
    {"coordinates": (30.3108936, 78.0121377), "phone_number": "+919389969916"},
    {"coordinates": (30.2820388, 78.002518), "phone_number": "+919389969916"},
    {"coordinates": (30.2875988, 78.0231428), "phone_number": "+919389969916"},
    {"coordinates": (30.2789269, 78.0012372), "phone_number": "+919389969916"},
    {"coordinates": (30.3125064, 78.0219506), "phone_number": "+919389969916"},
    {"coordinates": (30.3029695, 78.0214584), "phone_number": "+919389969916"},
    {"coordinates": (30.2919587, 77.9986905), "phone_number": "+919389969916"},
    {"coordinates": (30.311503, 77.982168), "phone_number": "+919389969916"},
    {"coordinates": (30.2864273, 78.0480676), "phone_number": "+919389969916"},
    {"coordinates": (30.3070576, 78.0095762), "phone_number": "+919389969916"}
]

def get_osrm_distance(origin: Tuple[float, float], destination: Tuple[float, float]):
    url = f"http://router.project-osrm.org/route/v1/foot/{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
    params = {"overview": "false"}
    response = requests.get(url, params=params)
    data = response.json()
    if 'routes' in data and data['routes']:
        distance_km = data['routes'][0]['distance'] / 1000
        return distance_km
    return float('inf')

def dijkstra(graph, start):
    pq = [(0, start)]
    distances = {start: 0}
    previous_nodes = {start: None}

    while pq:
        current_distance, current_node = heapq.heappop(pq)
        if current_distance > distances.get(current_node, float('inf')):
            continue
        for neighbor, weight in graph.get(current_node, {}).items():
            distance = current_distance + weight
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    return distances, previous_nodes

def send_sms_to_stations(emergency_type: str, user_location: Tuple[float, float], phone_numbers: List[str]):
    account_sid = 'AC4c024fc964c6236c3b439abd84d49329'
    auth_token = '946268ec7561cd7ea890a635da8e2c8d'
    from_phone = '+19137330629'
    message_body = f"Emergency: {emergency_type.upper()} reported! Immediate assistance required at location: {user_location}"

    client = Client(account_sid, auth_token)
    for number in phone_numbers:
        try:
            sent = client.messages.create(body=message_body, from_=from_phone, to=number)
            print(f"Sent to {number}: {sent.sid}")
        except Exception as e:
            print(f"Failed to send to {number}: {e}")

@app.post("/send_emergency/")
async def send_emergency(data: EmergencyRequest, background_tasks: BackgroundTasks):
    user_location = (data.latitude, data.longitude)
    emergency_type = data.emergency_type

    help_stations = [s["coordinates"] for s in help_stations_with_phone]
    graph = {}

    for station in help_stations:
        graph[station] = {}
        for other in help_stations:
            if station != other:
                dist = get_osrm_distance(station, other)
                graph[station][other] = dist

    graph[user_location] = {}
    for station in help_stations:
        dist = get_osrm_distance(user_location, station)
        graph[user_location][station] = dist

    distances, _ = dijkstra(graph, user_location)
    help_distances = [(station, distances[station]) for station in help_stations if station in distances]
    nearest = sorted(help_distances, key=lambda x: x[1])[:3]

    nearest_info = []
    phone_numbers = []

    for i, (station, dist) in enumerate(nearest):
        for station_info in help_stations_with_phone:
            if station_info["coordinates"] == station:
                phone = station_info["phone_number"]
                phone_numbers.append(phone)
                nearest_info.append({
                    "location": station,
                    "distance_km": round(dist, 2),
                    "phone": phone
                })

    # Background SMS sending
    background_tasks.add_task(send_sms_to_stations, emergency_type, user_location, phone_numbers)

    return {
        "message": f"{emergency_type.title()} alert sent to 3 nearest help stations.",
        "nearest_stations": nearest_info
    }
