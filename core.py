import folium
from geopy.distance import geodesic
import networkx as nx
from twilio.rest import Client

help_stations = [
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

account_sid = 'AC4c024fc964c6236c3b439abd84d49329'
auth_token = '946268ec7561cd7ea890a635da8e2c8d'
twilio_phone_number = '+19137330629'

def generate_map_and_send_sms(user_location, emergency_type):
    G = nx.Graph()

    # Add user node
    G.add_node("user", pos=user_location)

    # Add help stations
    for i, (lat, lon, name, phone) in enumerate(help_stations):
        G.add_node(name, pos=(lat, lon))
        dist = geodesic(user_location, (lat, lon)).km
        G.add_edge("user", name, weight=dist)

    # Get 3 nearest stations using Dijkstra
    shortest_paths = nx.single_source_dijkstra_path_length(G, "user")
    nearest_stations = sorted(shortest_paths.items(), key=lambda x: x[1])[1:4]

    # Folium map
    m = folium.Map(location=user_location, zoom_start=12)
    folium.Marker(user_location, tooltip="You", icon=folium.Icon(color="red")).add_to(m)

    # Initialize Twilio
    client = Client(account_sid, auth_token)

    for station_name, _ in nearest_stations:
        for lat, lon, name, phone in help_stations:
            if name == station_name:
                folium.Marker((lat, lon), tooltip=name, icon=folium.Icon(color="green")).add_to(m)
                folium.PolyLine([user_location, (lat, lon)], color="blue").add_to(m)

                # Send SMS
                message = f"Emergency Alert: {emergency_type} reported near you. Please respond."
                try:
                    client.messages.create(
                        body=message,
                        from_=twilio_phone_number,
                        to=phone
                    )
                except Exception as e:
                    print(f"SMS to {name} failed: {e}")
                break

    m.save("map.html")
    return "map.html"
