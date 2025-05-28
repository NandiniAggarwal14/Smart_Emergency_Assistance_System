# frontend.py
import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("🚨 Help Station Finder")
st.subheader("Detect Your Location and Report Emergency")

# Step 1: Get Location
location = get_geolocation()

if not location:
    st.warning("Please allow location access.")
    st.stop()

latitude = location["coords"]["latitude"]
longitude = location["coords"]["longitude"]
st.success(f"Location: {latitude:.6f}, {longitude:.6f}")

# Step 2: Select Emergency Type
emergency_type = st.selectbox(
    "Select Type of Emergency",
    ["Fire", "Accident", "Earthquake", "Medical", "Flood", "Robbery", "Other"]
)

# Step 3: Submit
if st.button("🚨 Send Alert to Help Stations"):
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "emergency_type": emergency_type
    }

    try:
        res = requests.post("http://127.0.0.1:8000/trigger_emergency/", json=payload)
        if res.status_code == 200:
            st.success("Alert sent successfully!")
            map_path = res.json()["map_path"]

            # Display the map
            with open(map_path, 'r', encoding='utf-8') as f:
                html_data = f.read()
            components.html(html_data, height=600)
        else:
            st.error("Failed to send alert.")
    except Exception as e:
        st.error(f"Error: {e}")
