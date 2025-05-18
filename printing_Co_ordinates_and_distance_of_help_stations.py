import requests
import folium
from folium import PolyLine, Marker
import heapq

user_location = (30.3245, 78.0430) 
def fetch_help_stations(lat, lon, radius=2000):
    query = f"""
    [out:json];
    (
      node(around:{radius},{lat},{lon})[amenity~"hospital|clinic|doctors|police"];
      way(around:{radius},{lat},{lon})[amenity~"hospital|clinic|doctors|police"];
    );
    out center tags;
    """
    response = requests.post("https://overpass.kumi.systems/api/interpreter", data=query)
    data = response.json()

    locations = []
    for el in data['elements']:
        if 'lat' in el and 'lon' in el:
            latlon = (el['lat'], el['lon'])
        elif 'center' in el:
            latlon = (el['center']['lat'], el['center']['lon'])
        else:
            continue

        tags = el.get('tags', {})
        phone = tags.get('contact:phone') or tags.get('phone')
        locations.append((latlon, phone))
    return locations

help_stations_raw = fetch_help_stations(*user_location)
print(f"✅ Found {len(help_stations_raw)} help stations")

def osrm_distance(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=false"
    response = requests.get(url)
    if response.status_code == 200:
        routes = response.json()
        return routes['routes'][0]['distance'] / 1000  
    return float('inf')

distance_list = []
for (station_coords, phone) in help_stations_raw:
    dist = osrm_distance(user_location, station_coords)
    distance_list.append(((station_coords, phone), dist))

nearest_stations = sorted(distance_list, key=lambda x: x[1])[:3]
nearest_coords = [station[0] for station, _ in nearest_stations]
m = folium.Map(location=user_location, zoom_start=15)
folium.Marker(user_location, tooltip="You", icon=folium.Icon(color="blue")).add_to(m)

for (loc, phone), dist in distance_list:
    color = "green" if loc in nearest_coords else "red"
    tooltip = f"Phone: {phone}" if phone else "No contact info"
    folium.CircleMarker(loc, radius=6, color=color, fill=True, fill_opacity=0.9, tooltip=tooltip).add_to(m)
    print(f"Help Station Location: {loc} | Distance: {dist:.2f} km")

for i, ((station, phone), dist) in enumerate(nearest_stations):
    info = f"Help Station {i+1} ({dist:.2f} km)"
    if phone:
        info += f" | 📞 {phone}"
    Marker(station, tooltip=info, icon=folium.Icon(color="green")).add_to(m)
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{user_location[1]},{user_location[0]};{station[1]},{station[0]}?overview=full&geometries=geojson"
    route_resp = requests.get(osrm_url).json()
    route_coords = route_resp['routes'][0]['geometry']['coordinates']
    route_latlon = [(lat, lon) for lon, lat in route_coords]
    PolyLine(route_latlon, color="green", weight=4, opacity=0.8).add_to(m)


m.save("auto_helpstations_map.html")
print("✅ Map with nearest help stations saved as 'auto_helpstations_map.html'")
m
