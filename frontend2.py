import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

st.set_page_config(layout="wide")
st.title("Emergency Help Station Finder")

st.subheader(" Step 1: Detect Your Location")

if "sent" not in st.session_state:
    st.session_state["sent"] = False

location = get_geolocation()

if not location:
    st.warning("Please allow location access in your browser.")
    st.stop()

latitude = location["coords"]["latitude"]
longitude = location["coords"]["longitude"]

st.success(f"Your location: {latitude:.6f}, {longitude:.6f}")

st.subheader("Step 2: Choose Emergency Type")

emergency_type = st.selectbox("Select emergency:", [
    "fire", "accident", "earthquake", "medical", "flood", "crime"
])

if st.button("Send Emergency Alert") and not st.session_state["sent"]:
    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "emergency_type": emergency_type
    }
    res = requests.post("http://127.0.0.1:8000/send_emergency/", json=payload)
    
    if res.status_code == 200:
        data = res.json()
        st.success(data["message"])
        st.write("Nearest Stations Info:")
        for station in data["nearest_stations"]:
            st.write(station)
        st.session_state["sent"] = True
    else:
        st.error("Failed to send emergency. Try again.")

if st.session_state["sent"]:
    if st.button("Reset Alert"):
        st.session_state["sent"] = False
