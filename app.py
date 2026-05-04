import streamlit as st
import requests
from agent_logic import run_travel_scout

def get_destination_image(destination):
    try:
        formatted_dest = destination.strip().title().replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_dest}"
        
        headers = {'User-Agent': 'TravelScoutApp/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "originalimage" in data and "source" in data["originalimage"]:
                return data["originalimage"]["source"]
    except Exception as e:
        print(f"Image fetch error: {e}")
    return None

def main():
    st.set_page_config(page_title="AI Travel Scout", layout="wide")
    
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #1E3A8A; font-weight: bold;'>AI Travel Scout</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #6B7280; margin-top: -15px; margin-bottom: 40px;'>Your Intelligent Trip Research Partner</h3>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("Trip Details")
        
        destination = st.text_input("Destination", placeholder="e.g. Dubai, Tokyo, Paris")
        
        all_months = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]
        month = st.selectbox("When?", all_months)
        
        vibe = st.multiselect(
            "Travel Style",
            ["Street Food", "Hidden Gems", "Luxury", "Nature", "No Crowds", "Culture"]
        )
        
        st.divider()
        include_hotels = st.checkbox("Include Hotel Recommendations?", value=True)
        
        submit_button = st.button("Start Scouting", use_container_width=True, type="primary")

    if submit_button:
        if destination:
            with st.spinner(f"Scouting the best spots in {destination}..."):
                try:
                    result = run_travel_scout(destination, month, vibe, include_hotels)
                    image_url = get_destination_image(destination)
                    
                    st.success(f"Scouting complete for {destination}!")
                    
                    with st.container(border=True):
                        st.markdown("### Your Itinerary & Tips")
                        st.write(result)
                        
                        if image_url:
                            st.divider()
                            st.image(image_url, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a destination in the sidebar to start.")

if __name__ == "__main__":
    main()