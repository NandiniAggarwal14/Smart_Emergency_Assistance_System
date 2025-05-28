import requests

user_location = (30.269745410969797, 77.99290170226186)

def fetch_help_stations(lat, lon, radius=6000):
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
print(f"Found {len(help_stations_raw)} help stations")

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

for (loc, phone), dist in distance_list:
    contact_info = f"Phone: {phone}" if phone else "No contact info"
    print(f"Help Station Location: {loc} | Distance: {dist:.2f} km | {contact_info}")
