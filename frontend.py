import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

st.set_page_config(layout="wide")
st.title("Help Station Finder")
st.subheader("Step 1: Detect Your Live Location")

location = get_geolocation()

if not location:
    st.warning(" Please allow location access in your browser.")
    st.stop()

latitude = location["coords"]["latitude"]
longitude = location["coords"]["longitude"]

st.success(f"Your location: {latitude:.6f}, {longitude:.6f}")

if st.button("Send Location to Backend"):
    user_location = {"latitude": latitude, "longitude": longitude}
    res = requests.post("http://127.0.0.1:8000/get_location/", json=user_location)

    if res.status_code == 200:
        st.success("Location sent successfully!")
        st.write(res.json())
    else:
        st.error("Failed to send location to backend.")