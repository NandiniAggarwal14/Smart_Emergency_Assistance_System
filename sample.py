import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd

# Step 1: Center around Clock Tower, Dehradun
latitude = 30.3245
longitude = 78.0430

# Step 2: Load only major roads in 1.5 km radius
custom_filter = '["highway"~"primary|secondary|tertiary"]'
G = ox.graph_from_point((latitude, longitude), dist=1500, custom_filter=custom_filter, network_type='drive')

# Step 3: Get hospitals and police stations with names only
tags = {
    'amenity': ['hospital', 'police']
}
pois = ox.features_from_point((latitude, longitude), tags=tags, dist=1500)
pois = pois[(pois.geometry.type == "Point") & (pois['name'].notna())]

# Step 4: Add known fire stations manually
fire_stations_data = {
    'amenity': ['fire_station', 'fire_station'],
    'geometry': [Point(78.04345, 30.32135), Point(78.04401, 30.32381)],
    'name': ['Fire Station 1', 'Fire Station 2']
}
fire_stations = gpd.GeoDataFrame(fire_stations_data, crs="EPSG:4326")

# Combine all POIs
all_pois = gpd.GeoDataFrame(pd.concat([pois, fire_stations], ignore_index=True), crs="EPSG:4326")

# Filter out suspicious POIs by keywords in name (like wedding halls etc)
all_pois = all_pois[~all_pois['name'].str.contains("wedding|banquet|event|party", case=False, na=False)]

# Plot base map
fig, ax = ox.plot_graph(
    G,
    node_size=0,
    edge_color='gray',
    edge_linewidth=0.7,
    show=False,
    close=False,
    bgcolor='white'
)

# Label only major roads (handling both str and list road names)
plotted_names = set()
for u, v, key, data in G.edges(keys=True, data=True):
    name = data.get('name')
    x = (G.nodes[u]['x'] + G.nodes[v]['x']) / 2
    y = (G.nodes[u]['y'] + G.nodes[v]['y']) / 2

    if isinstance(name, list):
        for n in name:
            if n and n not in plotted_names:
                ax.text(x, y, n, fontsize=6.5, color='darkgreen', alpha=0.7)
                plotted_names.add(n)
    elif isinstance(name, str) and name not in plotted_names:
        ax.text(x, y, name, fontsize=6.5, color='darkgreen', alpha=0.7)
        plotted_names.add(name)

# Plot POIs with cleaner labels
colors = {'hospital': 'red', 'police': 'blue', 'fire_station': 'orange'}
markers = {'hospital': 'o', 'police': '^', 'fire_station': 's'}

for _, row in all_pois.iterrows():
    amenity = row['amenity']
    ax.scatter(
        row.geometry.x,
        row.geometry.y,
        c=colors[amenity],
        marker=markers[amenity],
        label=amenity if amenity not in ax.get_legend_handles_labels()[1] else "",
        s=90,
        edgecolors='black',
        linewidths=0.6,
        zorder=5
    )
    ax.text(
        row.geometry.x + 0.0003,
        row.geometry.y + 0.0003,
        row['name'],
        fontsize=7.5,
        color='black'
    )

# Final touches
plt.title("Prominent Emergency Services & Roads Near Clock Tower, Dehradun", fontsize=13)
plt.legend(title="Emergency Services", loc="lower right", fontsize=8)
plt.tight_layout()
plt.show()

# ---------------- Export graph edges for C++ ----------------
# Ensure graph has edge lengths
G = ox.distance.add_edge_lengths(G)

# Map POIs to closest graph nodes
poi_node_map = {}
for _, row in all_pois.iterrows():
    nearest_node = ox.distance.nearest_nodes(G, X=row.geometry.x, Y=row.geometry.y)
    poi_node_map[nearest_node] = row['name']

# Export edge list using names where available, with '-' between u and v labels
with open("graph_edges.txt", "w") as f:
    for u, v, data in G.edges(data=True):
        distance = data['length']
        u_label = poi_node_map.get(u, str(u))
        v_label = poi_node_map.get(v, str(v))
        f.write(f"{u_label} - {v_label} {distance:.2f}\n")

print("Graph edges saved to graph_edges.txt")
